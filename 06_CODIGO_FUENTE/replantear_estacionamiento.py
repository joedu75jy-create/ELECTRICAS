"""Propuesta XY por paños del estacionamiento. No calcula iluminación ni peraltes.

Uso: python replantear_estacionamiento.py entrega_v1.dxf posiciones_v1.json salida
Las franjas se obtienen de pares de caras A-DETL de la arquitectura recibida.
Los IDs se conservan; la asignación a nuevos puntos minimiza desplazamientos por paño.
"""
from pathlib import Path
from collections import defaultdict, Counter
import csv
import hashlib
import json
import math
import shutil
import sys
import zipfile

import ezdxf
from ezdxf import bbox
from ezdxf.addons.drawing import Frontend, RenderContext, layout, pymupdf
from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration
import fitz
import numpy as np
from scipy.optimize import linear_sum_assignment

ROOM = 'ESTACIONAMIENTO VEHICULAR Y CIRCULACION'
BLUE = '#006b9f'
INK = '#243849'
MM = 72 / 25.4
LAYER = 'IE-LUM-EST-PROPUESTA-R02'
# Caras libres de columnas / franjas, leídas de la base arquitectónica en metros.
BAYS = [(20.49, 25.52), (26.07, 32.16), (32.71, 37.74), (38.29, 44.42), (44.97, 49.30)]


def graphic_box(ref):
    # El bbox del INSERT completo incluye atributos ocultos y da falsos positivos.
    b = bbox.extents(ref.virtual_entities())
    return (b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y)


def overlap(a, b):
    return a[0] < b[2] - 1e-7 and a[2] > b[0] + 1e-7 and a[1] < b[3] - 1e-7 and a[3] > b[1] + 1e-7


def distance(a, b):
    return math.hypot(max(a[0]-b[2], b[0]-a[2], 0), max(a[1]-b[3], b[1]-a[3], 0))


def beam_strips(m):
    horizontal, vertical = defaultdict(list), defaultdict(list)
    for e in m.query('LINE[layer=="A-DETL"]'):
        a, b = e.dxf.start, e.dxf.end
        if abs(a.y-b.y) < 1e-6:
            horizontal[tuple(round(x, 5) for x in sorted([a.x, b.x]))].append((round(a.y, 5), e.dxf.handle))
        if abs(a.x-b.x) < 1e-6:
            vertical[tuple(round(y, 5) for y in sorted([a.y, b.y]))].append((round(a.x, 5), e.dxf.handle))
    result = []
    for direction, table in [('H', horizontal), ('V', vertical)]:
        for span, faces in table.items():
            if span[1]-span[0] < 2:
                continue
            for i, (c, handle) in enumerate(faces):
                for c2, handle2 in faces[i+1:]:
                    if abs(abs(c-c2)-.4) > .001:
                        continue
                    rect = (span[0], min(c, c2), span[1], max(c, c2)) if direction == 'H' else (min(c, c2), span[0], max(c, c2), span[1])
                    if rect[2] > 20.49 and rect[0] < 49.3 and rect[3] > 11.415 and rect[1] < 37.425:
                        result.append(dict(rect=rect, caras=[handle, handle2], capa='A-DETL', orientacion=direction))
    return result


def candidate_positions():
    # Cada intervalo es un espacio libre entre caras; filas equidistantes dentro.
    low = [11.415 + (16.475-11.415)*(k+.5)/2 for k in range(2)]
    middle = [16.875 + (24.105-16.875)*(k+.5)/3 for k in range(3)]
    upper = [24.505 + (29.835-24.505)*(k+.5)/2 for k in range(2)]
    ys = [low+middle, low+middle+[27.095], low+middle+upper+[31.6, 35.45], middle+upper+[31.6, 35.45], middle+upper+[31.6, 35.45]]
    # En el paño oriental central hay dos bancos de ductos proyectados entre
    # Y=22,85 y 24,09. Repartir sus seis puntos debajo de esas proyecciones.
    ys[4] = [18.05, 20.0, 21.95] + upper + [31.6, 35.45]
    # La fila norte se eleva 0,255 m respecto del centro del paño para evitar
    # la proyección del ducto en X=47,32..48,455; se alinean sus seis unidades.
    result = []
    for i, ((a, b), rows, count) in enumerate(zip(BAYS, ys, [1, 3, 2, 2, 2]), 1):
        result.append([dict(x=a+(b-a)*(k+.5)/count, y=y, pano=i) for y in rows for k in range(count)])
    assert [len(x) for x in result] == [5, 18, 18, 14, 14]
    return result


def refs_in_room(doc):
    return [e for e in doc.modelspace().query('INSERT') if e.get_attrib_text('AMBIENTE') == ROOM]


def projected_ducts(doc):
    result = [
        dict(rect=(47.32, 33.87, 48.455, 34.61), fuente='A-DETL: 6A7A..6A89'),
        dict(rect=(47.195, 23.77, 49.435, 24.09), fuente='A-DETL: 6A8A..6AC0'),
        dict(rect=(47.195, 22.85, 49.435, 23.17), fuente='A-DETL: 6AC2..6AF8'),
    ]
    for e in doc.modelspace().query('INSERT'):
        if 'DuctoPrOyeccion2D' not in e.dxf.name:
            continue
        b = bbox.extents(v for v in e.virtual_entities() if v.dxftype() in ('LINE', 'LWPOLYLINE', 'POLYLINE', 'ARC', 'CIRCLE'))
        if b.has_data and b.extmax.x > 20 and b.extmax.y > 11 and b.extmin.y < 38:
            result.append(dict(rect=(b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y), fuente='Proyeccion de ducto INSERT ' + e.dxf.handle))
    return result


def add_sheet(doc, name, width, height, center, size, view_center, view_height, title, general=False):
    p = doc.layouts.new(name)
    p.page_setup(size=(width, height), margins=(0, 0, 0, 0), units='mm')
    vp = p.add_viewport(center=center, size=size, view_center_point=view_center, view_height=view_height)
    vp.dxf.layer = 'Defpoints'
    vp.dxf.flags = 16384
    # Diferenciar los puntos ajenos al alcance en las hojas CAD, conservando
    # los colores globales originales del modelo y de la arquitectura.
    for layer in doc.layers:
        if layer.dxf.name.startswith('IE-LUM-') and layer.dxf.name != LAYER:
            overrides = layer.get_vp_overrides()
            overrides.set_rgb(vp.dxf.handle, (170, 176, 181))
            overrides.commit()

    def text(s, x, y, h=3, w=None):
        p.add_mtext(s, dxfattribs={'insert': (x, y), 'char_height': h, 'width': w or width-32, 'style': 'EI_LUM_REGULAR', 'layer': 'IE-LAMINA'})

    p.add_lwpolyline([(8, 8), (width-8, 8), (width-8, height-8), (8, height-8)], close=True, dxfattribs={'layer': 'IE-LAMINA'})
    text(title, 16, height-18, 5)
    text('Propuesta de ubicación XY por paños | Sin recorridos | Pendiente de recálculo', 16, height-30, 3.2)
    if general:
        text('ESTACIONAMIENTO', 641, 518, 5, 180)
        text('69 luminarias L-01-15 / 15 W-A', 641, 503, 3.5, 178)
        text('Azul: nuevas posiciones propuestas. Gris: las otras 93 luminarias, sin revisar en esta entrega.', 641, 488, 3.2, 175)
        text('CRITERIO', 641, 437, 3.5, 175)
        text('Distribución por espacios libres entre las franjas de la arquitectura. Se mantienen las 69 unidades, sus bloques y su orientación.', 641, 423, 3.2, 175)
        text('COMPROBACIÓN EN PLANTA', 641, 352, 3.5, 175)
        text('Sin superposición gráfica con las franjas y proyecciones de ductos contrastadas. Tamaños de símbolos gráficos; no son huellas físicas.', 641, 338, 3.2, 175)
        text('ALTURA Y MONTAJE', 641, 260, 3.5, 175)
        text('Adosado a losa previsto. La altura de 3,89 m del cálculo anterior queda solo como referencia; la altura propuesta está pendiente de cortes y peraltes.', 641, 246, 3.2, 175)
        text('ALCANCE', 641, 166, 3.5, 175)
        text('162 luminarias en el archivo integrado. Solo se replantean las 69 del estacionamiento. El resto conserva su distribución anterior y requiere revisión propia.', 641, 152, 3.2, 175)
    else:
        text('69 unidades / 1.035 W | Distribución: 5 + 18 + 18 + 14 + 14 por franja longitudinal', 16, 136, 3.2)
        text('Bloques aprobados, sin códigos exteriores. Azul: propuesta; gris: luminarias de otros ambientes sin intervenir.', 16, 121, 2.9)
        text('Filas ajustadas en el norte y paño oriental central para evitar proyecciones de ductos de la base arquitectónica.', 16, 106, 2.9)
        text('Verificar dimensiones reales del equipo, alturas, peraltes, ductos y acceso de mantenimiento con estructuras e instalaciones.', 16, 91, 2.9)
    text('Escala 1:100 | Modelo en metros | REV 02 | Ubicación propuesta, pendiente de validación lumínica', 16, 29, 2.8)
    text('No se trasladan los resultados de lux ni uniformidad del DIALux anterior a esta nueva distribución.', 16, 19, 2.6)
    return p


def render_sheet(doc, sheet, width, height, target_layer, cache=None):
    if cache and cache.exists():
        return fitz.open(cache)
    backend = pymupdf.PyMuPdfBackend()
    frontend = Frontend(RenderContext(doc), backend, config=Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR))

    def override(entity, props):
        if props.layer == target_layer or (target_layer == '*' and props.layer.startswith('IE-LUM-')):
            props.color = BLUE
        elif props.layer.startswith('IE-LUM-'):
            props.color = '#aab0b5'
        elif not props.layer.startswith('IE-') and entity.dxftype() != 'VIEWPORT':
            props.color = '#858c93'
            props.lineweight = .10

    frontend.push_property_override_function(override)
    frontend.draw_layout(doc.layouts.get(sheet), finalize=True)
    data = backend.get_pdf_bytes(layout.Page(width, height, layout.Units.mm), settings=layout.Settings(fit_page=False, scale=1))
    result = fitz.open(stream=data, filetype='pdf')
    # El backend redondea el tamaño de página a puntos enteros; fijar el medio
    # exacto conserva la escala y la transformación de las hojas CAD.
    assert abs(result[0].rect.width-width*MM) < 1.1 and abs(result[0].rect.height-height*MM) < 1.1
    result[0].set_mediabox(fitz.Rect(0, 0, width*MM, height*MM))
    if cache:
        result.save(cache)
    return result


def compare_pdf(before, after, strips, changes, out):
    pdf = fitz.open()
    page = pdf.new_page(width=594*MM, height=420*MM)
    font = '/usr/share/fonts/truetype/open-sans/OpenSans-Regular.ttf'
    page.insert_font(fontname='OpenSans', fontfile=font)

    def text(x, y, s, size=10, color=(.14, .22, .29)):
        page.insert_text((x*MM, y*MM), s, fontname='OpenSans', fontsize=size, color=color)

    text(14, 18, 'ESTACIONAMIENTO | ANTES Y PROPUESTA ENTRE VIGAS', 19)
    text(14, 29, '69 luminarias en ambos casos | Sin recorridos | Revisión visual de posiciones, pendiente de cálculo', 11)
    # Mismo recorte y misma escala en ambas vistas del plano A1.
    world = (20.0, 10.5, 50.2, 37.8)
    clip = fitz.Rect((68+10*world[0])*MM, (506-10*world[3])*MM, (68+10*world[2])*MM, (506-10*world[1])*MM)
    plot_width = 268
    plot_height = plot_width*(world[3]-world[1])/(world[2]-world[0])
    for x, source, title, is_before in [(14, before, 'ANTES / POSICIONES DE DIALux', True), (312, after, 'PROPUESTA / POR PAÑOS', False)]:
        text(x, 48, title, 13)
        target = fitz.Rect(x*MM, 59*MM, (x+plot_width)*MM, (59+plot_height)*MM)
        page.show_pdf_page(target, source, 0, clip=clip)

        def point(xx, yy):
            return fitz.Point((x+(xx-world[0])*plot_width/(world[2]-world[0]))*MM, (59+(world[3]-yy)*plot_width/(world[2]-world[0]))*MM)

        for item in strips:
            a, b, c, d = item['rect']
            a, c = max(a, world[0]), min(c, world[2])
            b, d = max(b, world[1]), min(d, world[3])
            if a >= c or b >= d:
                continue
            r = fitz.Rect(point(a, d), point(c, b))
            page.draw_rect(r, color=(.77, .46, .15), fill=(1, .76, .34), fill_opacity=.18, width=.3)
        if is_before:
            for row in changes:
                if not row['franjas_antes']:
                    continue
                xx, yy = row['x_antes_m'], row['y_antes_m']
                page.draw_rect(fitz.Rect(point(xx-.18, yy+.72), point(xx+.18, yy-.72)), color=(.8, .14, .17), width=.85)
            n = sum(bool(r['franjas_antes']) for r in changes)
            text(x, 326, f'{n} símbolos superpuestos a franjas en planta, marcados en rojo.', 10, (.72, .12, .15))
        else:
            text(x, 326, '0 superposiciones gráficas con las franjas contrastadas.', 10, (0, .37, .3))
            text(x, 335, 'Se conservan las 69 unidades. Altura de montaje: pendiente.', 10)
    text(14, 354, 'Naranja: franjas obtenidas de caras dibujadas en A-DETL. Su identificación estructural y peralte requieren confirmación.', 10)
    text(14, 365, 'La comprobación usa el contorno gráfico del símbolo (1,20 m de largo en el modelo), no una dimensión física confirmada.', 10)
    text(14, 376, 'Las filas norte y del paño oriental central se ajustan para separar los símbolos de las proyecciones de ductos.', 10)
    text(14, 399, 'REV 02 | Sin resultados nuevos de iluminancia o uniformidad. Los otros 93 puntos del semisótano no se han replanteado.', 10)
    pdf.save(out/'ESTACIONAMIENTO_ANTES_DESPUES_REV02.pdf', garbage=4, deflate=True)
    page.get_pixmap(dpi=120).save(out/'ESTACIONAMIENTO_ANTES_DESPUES_REV02.png')
    return pdf


def main(base, coordinates, output):
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    d = ezdxf.readfile(base)
    old = ezdxf.readfile(base)
    records = json.loads(Path(coordinates).read_text())
    targets = candidate_positions()
    strips = beam_strips(d.modelspace())
    assert len(strips) == 44, 'Revisar geometría de la base: cambió la detección de caras.'
    old_refs = {e.get_attrib_text('ID'): e for e in refs_in_room(old)}
    new_refs = refs_in_room(d)
    assert len(new_refs) == 69
    layer = d.layers.new(LAYER, dxfattribs={'color': 5, 'lineweight': 18})
    layer.dxf.true_color = int(BLUE[1:], 16)
    old.layers.new('IE-LUM-EST-REFERENCIA', dxfattribs={'color': 5, 'lineweight': 18}).dxf.true_color = int(BLUE[1:], 16)
    for e in old_refs.values():
        e.dxf.layer = 'IE-LUM-EST-REFERENCIA'
    changes = []
    ducts = projected_ducts(d)
    for bay_index, ((left, right), points) in enumerate(zip(BAYS, targets), 1):
        refs = sorted([e for e in new_refs if left < e.dxf.insert.x < right], key=lambda e: e.get_attrib_text('ID'))
        assert len(refs) == len(points)
        costs = np.array([[math.dist(tuple(e.dxf.insert)[:2], (p['x'], p['y']))**2 for p in points] for e in refs])
        ii, jj = linear_sum_assignment(costs)
        for i, j in zip(ii, jj):
            e, p = refs[i], points[j]
            identifier = e.get_attrib_text('ID')
            previous = old_refs[identifier]
            before_box = graphic_box(previous)
            before_hits = [k+1 for k, s in enumerate(strips) if overlap(before_box, s['rect'])]
            x0, y0 = e.dxf.insert.x, e.dxf.insert.y
            e.translate(p['x']-x0, p['y']-y0, 0)
            e.dxf.layer = LAYER
            for tag, value in {
                'ALTURA_M': 'PENDIENTE', 'FUENTE_XY': 'Propuesta por panos REV02 sobre arquitectura recibida',
                'ESTADO': 'PROPUESTA VISUAL REV02 - PENDIENTE RECALCULO',
                'MONTAJE': 'Adosado a losa previsto; confirmar altura con secciones y peraltes',
                'GIRO_REFERENCIA': '90 grados; lineales verticales mantenidas en propuesta',
            }.items():
                e.get_attrib(tag).dxf.text = value
            for tag, value in {'ALTURA_REF_DIALUX_M': '3.89', 'X_REF_DIALUX_M': str(x0), 'Y_REF_DIALUX_M': str(y0), 'PANO_REV02': str(bay_index)}.items():
                e.add_attrib(tag, value, insert=(p['x'], p['y']), dxfattribs={'height': .25, 'flags': 1, 'style': 'EI_LUM_REGULAR'})
            after_box = graphic_box(e)
            after_hits = [k+1 for k, s in enumerate(strips) if overlap(after_box, s['rect'])]
            assert not after_hits, (identifier, after_hits)
            assert not any(overlap(after_box, duct['rect']) for duct in ducts), (identifier, 'ducto')
            assert left < after_box[0] and after_box[2] < right
            changes.append(dict(id=identifier, numero_dialux=int(previous.get_attrib_text('NUMERO_LOCAL')), pano=bay_index,
                                x_antes_m=x0, y_antes_m=y0, x_propuesto_m=round(p['x'], 5), y_propuesto_m=round(p['y'], 5),
                                desplazamiento_m=round(math.dist((x0, y0), (p['x'], p['y'])), 4),
                                altura_ref_dialux_m=3.89, altura_propuesta_m='PENDIENTE',
                                franjas_antes=before_hits, franjas_propuesta=after_hits,
                                separacion_grafica_franjas_m=round(min(distance(after_box, s['rect']) for s in strips), 4),
                                separacion_grafica_proyecciones_ductos_m=round(min(distance(after_box, duct['rect']) for duct in ducts), 4)))
    changes.sort(key=lambda r: r['id'])
    assert len({(r['x_propuesto_m'], r['y_propuesto_m']) for r in changes}) == 69
    assert sum(bool(r['franjas_antes']) for r in changes) == 22
    # Conservar la arquitectura y los otros 93 puntos exactamente como estaban.
    original = ezdxf.readfile(base)
    moved_handles = {e.dxf.handle for e in new_refs}
    for e in original.modelspace():
        if e.dxf.handle not in moved_handles:
            assert e.dxf.all_existing_dxf_attribs() == d.entitydb[e.dxf.handle].dxf.all_existing_dxf_attribs()
    assert len(d.modelspace()) == len(original.modelspace())
    for name in list(d.layouts.names()):
        if name.startswith('IE_'):
            d.layouts.delete(name)
    general = add_sheet(d, 'IE_PROPUESTA_A1_REV02', 841, 594, (318, 290), (600, 480), (25, 20.2), 48,
                        'SEMISÓTANO | PROPUESTA ENTRE VIGAS / REV 02', general=True)
    detail = add_sheet(d, 'IE_ESTACIONAMIENTO_A2_REV02', 420, 594, (210, 347), (380, 380), (34.8, 24.2), 38,
                       'ESTACIONAMIENTO | PROPUESTA / REV 02')
    target = out/'SEMISOTANO_LUMINARIAS_PROPUESTA_REV02.dxf'
    d.saveas(target)
    rd = ezdxf.readfile(target)
    audit = rd.audit()
    assert not audit.errors and not audit.fixes
    assert len(refs_in_room(rd)) == 69
    assert sum(e.has_attrib('TIPO') for e in rd.modelspace().query('INSERT')) == 162
    for e in refs_in_room(rd):
        assert all(a.is_invisible for a in e.attribs)
        assert e.get_attrib_text('ALTURA_M') == 'PENDIENTE'
        assert not any(overlap(graphic_box(e), s['rect']) for s in strips)
        assert not any(overlap(graphic_box(e), duct['rect']) for duct in ducts)
    print('DXF: 69 propuestas; 22 superposiciones graficas anteriores; 0 en propuesta.', flush=True)
    signature = hashlib.sha256(Path(base).read_bytes() + Path(__file__).read_bytes()).hexdigest()[:12]
    cache = out.parent / ('.' + out.name + '_render_' + signature)
    cache.mkdir(exist_ok=True)
    before_pdf = render_sheet(old, 'IE_LUMINARIAS_A1', 841, 594, 'IE-LUM-EST-REFERENCIA', cache/'antes.pdf')
    print('Vista anterior renderizada.', flush=True)
    general_pdf = render_sheet(rd, general.name, 841, 594, LAYER, cache/'general.pdf')
    print('Vista general de propuesta renderizada.', flush=True)
    detail_pdf = render_sheet(rd, detail.name, 420, 594, LAYER, cache/'detalle.pdf')
    print('Detalle de estacionamiento renderizado.', flush=True)
    comparison = compare_pdf(before_pdf, general_pdf, strips, changes, out)
    final = fitz.open()
    for source in [comparison, detail_pdf, general_pdf]:
        final.insert_pdf(source)
    final.save(out/'SEMISOTANO_PROPUESTA_REV02_VISTA.pdf', garbage=4, deflate=True)
    # Recorte del detalle: coordenadas del viewport (20..400, 157..537 mm).
    detail_pdf[0].get_pixmap(dpi=130, clip=fitz.Rect(20*MM, 57*MM, 400*MM, 437*MM)).save(out/'ESTACIONAMIENTO_PROPUESTA_REV02.png')
    report = dict(estacionamiento=69, luminarias_totales=162, otros_puntos_sin_replantear=93,
                  cantidades_por_franja=[5, 18, 18, 14, 14], potencia_estacionamiento_w=1035,
                  franjas_contrastadas=len(strips), simbolos_superpuestos_antes=22, simbolos_superpuestos_propuesta=0,
                  separacion_grafica_minima_franjas_m=min(r['separacion_grafica_franjas_m'] for r in changes),
                  proyecciones_de_ductos_contrastadas=len(ducts), superposiciones_graficas_ductos_propuesta=0, altura_propuesta='PENDIENTE',
                  errores_auditoria=len(audit.errors), correcciones_auditoria=len(audit.fixes),
                  fuente_franjas='Pares de caras A-DETL de la arquitectura; pendiente confirmacion estructural y peraltes',
                  alcance_comprobacion='Superposicion XY de simbolos graficos, no colision fisica 3D ni validacion luminica',
                  dxf_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (out/'COMPROBACION_REV02.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    (out/'FRANJAS_ARQUITECTURA.json').write_text(json.dumps(strips, ensure_ascii=False, indent=2))
    (out/'PROYECCIONES_DUCTOS.json').write_text(json.dumps(ducts, ensure_ascii=False, indent=2))
    (out/'CAMBIOS_69_ESTACIONAMIENTO.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2))
    with (out/'CAMBIOS_69_ESTACIONAMIENTO.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(changes[0]))
        writer.writeheader()
        writer.writerows(changes)
    by_id = {r['id']: r for r in changes}
    for r in records:
        if r['id'] in by_id:
            c = by_id[r['id']]
            r['x_ref_dialux_m'], r['y_ref_dialux_m'] = r['x_m'], r['y_m']
            r['altura_ref_dialux_m'] = r.pop('altura_m')
            r['x_m'], r['y_m'] = c['x_propuesto_m'], c['y_propuesto_m']
            r['altura_m'] = None
            r['observacion'] = 'Propuesta XY REV02; altura pendiente; requiere recalculo DIALux con vigas.'
    (out/'LUMINARIAS_INTEGRADAS_REV02.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
    (out/'LEEME_REV02.md').write_text('''# Propuesta por paños del estacionamiento — REV 02

Abra SEMISOTANO_LUMINARIAS_PROPUESTA_REV02.dxf: un único modelo en metros con la base y 162 luminarias. Se replantean solo las 69 L-01-15 del estacionamiento vehicular y circulación (1.035 W). Las otras 93 conservan su ubicación anterior y no quedan validadas por esta revisión. Sin recorridos ni códigos exteriores.

El PDF tiene tres páginas: comparación antes/después con las franjas marcadas; detalle de la propuesta a 1:100; plano integrado general a 1:100. El archivo comparativo individual contiene solo la primera página. Azul: estacionamiento revisado; gris: otros puntos. Naranja: caras de franjas contrastadas; rojo en el antes: superposición gráfica.

Se contrastaron 44 franjas de 0,40 m dibujadas como pares de líneas en A-DETL y las proyecciones de ductos registradas en PROYECCIONES_DUCTOS.json. Se identificaron 22 símbolos superpuestos a las franjas en el estacionamiento anterior. La propuesta no superpone su contorno gráfico con esas franjas ni con las proyecciones de ductos contrastadas. No es un certificado de ausencia de interferencias físicas: los símbolos conservan dimensiones gráficas de la propuesta aprobada; faltan dimensiones reales de equipos, estructuras, peraltes y coordinación completa de instalaciones.

La distribución conserva por franja longitudinal 5, 18, 18, 14 y 14 unidades. Se centran las columnas dentro de los anchos libres entre caras de columnas; las filas se reparten dentro de los intervalos libres. La fila norte se separa del ducto y alinea sus seis luminarias a Y=35,45 m. En el paño oriental central se reparten seis puntos en Y=18,05, 20,00 y 21,95 m para evitar los dos bancos de ductos proyectados. Los IDs originales se mantienen mediante asignación de mínimo desplazamiento al nuevo conjunto de puntos por franja. La tabla de cambios registra cada XY anterior y propuesto.

Montaje previsto: adosado a losa, pendiente de verificar por sección. Los 3,89 m de DIALux se guardan solo en ALTURA_REF_DIALUX_M. ALTURA_M queda PENDIENTE para estas 69 unidades. Las nuevas coordenadas se identifican como propuesta, no como coordenadas del cálculo anterior. Z=0 se conserva porque es una representación en planta.

La altura libre, las sombras y los niveles de lux/uniformidad requieren recálculo en DIALux con vigas y demás obstáculos modelados. No se ha hecho ese recálculo ni se heredan sus resultados anteriores. La cantidad de 69 se conserva para comparación, su suficiencia no está confirmada. La identificación estructural de las franjas y sus peraltes debe confirmarse con estructuras.

Los bloques y la arquitectura se conservan. La única intervención en el modelo son las 69 referencias y sus atributos. Auditoría DXF sin errores ni correcciones; guardado y reapertura comprobados. No se dispone de AutoCAD en este entorno. Fuentes OpenSans incluidas.
''', encoding='utf-8')
    for name in ['OpenSans-Regular.ttf', 'OpenSans-Semibold.ttf', 'LICENCIA_OPENSANS.txt']:
        source = Path(base).parent/name
        if source.exists():
            shutil.copy2(source, out/name)
    package = out/'SEMISOTANO_PROPUESTA_REV02_ENTREGA.zip'
    with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in out.iterdir():
            if file.is_file() and file.suffix != '.zip':
                z.write(file, file.name)
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None and sum(n.endswith('.dxf') for n in z.namelist()) == 1
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
