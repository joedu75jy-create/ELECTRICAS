"""REV03: bloques de luminarias en metros, proporcionados por sus medidas.
Uso: python ajustar_medidas_luminarias.py integrado_rev02.dxf salida
Conserva todas las posiciones, orientaciones y datos de montaje de REV02.
"""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import math
import shutil
import sys
import zipfile

import ezdxf
from ezdxf import bbox
import fitz
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from instalar_luminarias_semisotano import CADCanvas, FONT
from presentar_todas_luminarias import Catalog, BODY
from replantear_estacionamiento import render_sheet, beam_strips, graphic_box, overlap, projected_ducts, ROOM

MM = 72/25.4
BLUE = '#006b9f'
SOURCES = {
    'corta': 'https://www.ledvance.lat/es/product-datasheet/232595/261282',
    'aplique': 'https://www.assets.signify.com/is/content/Signify/911401847682_EU.en_SA.PROF.FP',
    'downlight': 'https://www.signify.com/global/prof/indoor-luminaires/downlights/philips-coreline-slimdownlight/911401806080_EU/product',
    'panel': 'https://www.signify.com/cs-cz/prof/interierova-svitidla/zapustene/philips-coreline-panel-gen6/911401891585_EU/product',
}


def dimensions():
    result = {
        'L-01': dict(largo_mm=1200, ancho_mm=80, diametro_mm=0, estado='Largo nominal del Excel; ancho aproximado', fuente='Cuadro del usuario: L-01, lineal 1,20 m'),
        'L-01-15': dict(largo_mm=599, ancho_mm=77, diametro_mm=0, estado='Referencia de fabricante', fuente=SOURCES['corta']),
        'L-01-18': dict(largo_mm=600, ancho_mm=80, diametro_mm=0, estado='Largo nominal del Excel; ancho aproximado', fuente='Cuadro del usuario: L-01-18, lineal 0,60 m'),
        'L-02': dict(largo_mm=390, ancho_mm=390, diametro_mm=390, estado='Referencia de fabricante WL140V', fuente=SOURCES['aplique']),
    }
    for code in ['L-03', 'L-03-D', 'L-03A', 'L-03-DA', 'L-03-IP65', 'L-03-90']:
        side = 595 if code == 'L-03-IP65' else 600
        result[code] = dict(largo_mm=side, ancho_mm=side, diametro_mm=0,
                            estado='Referencia de fabricante RC132V' if code == 'L-03-IP65' else 'Módulo nominal del Excel; cuerpo por confirmar',
                            fuente=SOURCES['panel'] if code == 'L-03-IP65' else 'Cuadro del usuario: panel 60 × 60 cm')
    result['L-04B'] = dict(largo_mm=166, ancho_mm=166, diametro_mm=166, estado='Diámetro exterior de fabricante DN145B', fuente=SOURCES['downlight'])
    result['L-04C'] = dict(largo_mm=180, ancho_mm=180, diametro_mm=180, estado='Estimación provisional; modelo no identificado', fuente='Estimación para el tipo de superficie de 11 W; no utilizado en este nivel')
    for code, spec in result.items():
        spec['bloque'] = 'EI_LUM_' + code.replace('-', '_')
        spec['tipo'] = code
    return result


class MeterCanvas(CADCanvas):
    def props(self):
        # Plumas de impresión independientes de la unidad geométrica (metros).
        return dict(layer='0', color=0, lineweight=13 if self.lw >= .3 else 9)


class ProportionalCatalog(Catalog):
    def linear(self, x, y, ww, hh=None, col=BODY, variant=''):
        # El ancho de la carcasa también responde a su medida, no al largo.
        return super().linear(x, y, ww, ww*self.linear_ratio, col, variant)


def rebuild_blocks(doc, specs):
    for name, file in [('OR', 'OpenSans-Regular.ttf'), ('R', 'OpenSans-Regular.ttf'), ('OB', 'OpenSans-Semibold.ttf'), ('B', 'OpenSans-Semibold.ttf')]:
        pdfmetrics.registerFont(TTFont(name, FONT+file))
    for code, spec in specs.items():
        block = doc.blocks.get(spec['bloque'])
        tags = [e.dxf.tag for e in block.query('ATTDEF')]
        for e in list(block):
            block.delete_entity(e)
        block.block_record.dxf.units = 6
        ref = 72 if code == 'L-01' else 47 if code.startswith('L-01-') else 27
        renderer = ProportionalCatalog(MeterCanvas(block, spec['largo_mm']/1000/ref))
        renderer.linear_ratio = spec['ancho_mm']/spec['largo_mm']
        renderer.lamp(code, 0, 0, ref)
        first = list(block)[0]
        if spec['diametro_mm']:
            actual = max(e.dxf.radius*2 for e in block.query('CIRCLE'))*1000
            assert abs(actual-spec['diametro_mm']) < 1e-5
        else:
            body = bbox.extents([first])
            assert abs(body.size.x*1000-spec['largo_mm']) < 1e-5
            assert abs(body.size.y*1000-spec['ancho_mm']) < 1e-5
        for tag in tags + ['LARGO_CUERPO_MM', 'ANCHO_CUERPO_MM', 'DIAMETRO_CUERPO_MM', 'REFERENCIA_DIMENSIONAL']:
            block.add_attdef(tag, insert=(0, 0), height=.025, text='', dxfattribs={'flags': 1, 'style': 'EI_LUM_REGULAR', 'layer': '0'})


def sheet(doc, name, width, height, title):
    p = doc.layouts.new(name)
    p.page_setup(size=(width, height), margins=(0, 0, 0, 0), units='mm')
    p.add_lwpolyline([(8, 8), (width-8, 8), (width-8, height-8), (8, height-8)], close=True, dxfattribs={'layer': 'IE-LAMINA'})

    def text(s, x, y, h=3, w=None):
        return p.add_mtext(s, dxfattribs={'insert': (x, y), 'char_height': h, 'width': w or width-32, 'style': 'EI_LUM_REGULAR', 'layer': 'IE-LAMINA'})

    text(title, 16, height-18, 5)
    return p, text


def viewport(doc, paper, center, size, model_center, view_height):
    v = paper.add_viewport(center=center, size=size, view_center_point=model_center, view_height=view_height)
    v.dxf.layer = 'Defpoints'
    v.dxf.flags = 16384
    for layer in doc.layers:
        if layer.dxf.name.startswith('IE-LUM-'):
            o = layer.get_vp_overrides()
            o.set_rgb(v.dxf.handle, (0, 107, 159))
            o.commit()


def create_sheets(doc, specs, counts):
    catalog, text = sheet(doc, 'IE_MEDIDAS_A2_REV03', 594, 420, 'LUMINARIAS | PROPORCIÓN POR MEDIDAS / REV 03')
    text('Los doce dibujos a la misma escala 1:10. Medidas del cuerpo en mm; referencias aproximadas donde se indica.', 16, 390, 3.2)
    for i, (code, spec) in enumerate(specs.items()):
        x, top = 16+i%4*141, 365-i//4*106
        catalog.add_lwpolyline([(x, top), (x+134, top), (x+134, top-99), (x, top-99)], close=True, dxfattribs={'layer': 'IE-LAMINA', 'lineweight': 9})
        text(code, x+5, top-5, 3.7, 124)
        value = f"Ø{spec['diametro_mm']} mm" if spec['diametro_mm'] else f"{spec['largo_mm']} × {spec['ancho_mm']} mm"
        text(value + f" | {counts.get(code, 0)} en semisótano", x+5, top-15, 2.7, 124)
        # Cuerpo en metros ×100 = milímetros de papel a 1:10.
        catalog.add_blockref(spec['bloque'], (x+67, top-53), dxfattribs={'xscale': 100, 'yscale': 100, 'zscale': 100, 'layer': 'IE-LUM-L-01'})
        text(spec['estado'], x+5, top-87, 2.4, 124)
    text('L-01 y L-01-18: anchos aproximados. L-04C: Ø180 mm provisional, pendiente de modelo. Paneles de 600 mm: módulo nominal.', 16, 30, 2.7)
    text('Se conserva el acabado aprobado y LED interior. Los códigos aparecen en esta leyenda, sin rótulos exteriores en planta.', 16, 19, 2.7)

    general, text = sheet(doc, 'IE_GENERAL_A1_REV03', 841, 594, 'SEMISÓTANO | LUMINARIAS PROPORCIONADAS / REV 03')
    text('162 luminarias | Misma distribución de REV02 | Tamaños según referencias de equipos | Sin recorridos', 16, 562, 3.2)
    viewport(doc, general, (318, 290), (600, 480), (25, 20.2), 48)
    text('MEDIDAS DE REFERENCIA', 641, 518, 4.4, 175)
    for i, code in enumerate(['L-01', 'L-01-15', 'L-02', 'L-04B', 'L-03-IP65']):
        s = specs[code]
        value = f"Ø{s['diametro_mm']} mm" if s['diametro_mm'] else f"{s['largo_mm']} × {s['ancho_mm']} mm"
        text(f'{code} | {counts[code]} unidades', 641, 492-i*37, 3.3, 175)
        text(value, 641, 482-i*37, 3, 175)
    text('PROPORCIÓN', 641, 278, 3.5, 175)
    text('Los bloques están dibujados en metros a tamaño de referencia. En el modelo todas las luminarias se insertan con escala 1.', 641, 265, 3.1, 175)
    text('LECTURA DEL DETALLE', 641, 213, 3.5, 175)
    text('La lámina 1:10 muestra el acabado completo. En planta 1:100 los equipos pequeños conservan su tamaño proporcional.', 641, 200, 3.1, 175)
    text('DISTRIBUCIÓN Y CÁLCULO', 641, 146, 3.5, 175)
    text('69 posiciones propuestas por paños y otras 93 de referencia. Alturas, peraltes y recálculo DIALux siguen pendientes.', 641, 133, 3.1, 175)
    text('Escala 1:100 | Modelo en metros | Dimensiones de referencia, sujetas al equipo definitivo', 16, 27, 2.8)
    text('Se ajustan tamaños; se conservan los 162 puntos, sus giros y sus datos de montaje de REV02.', 16, 18, 2.6)

    detail, text = sheet(doc, 'IE_DETALLE_A3_REV03', 420, 297, 'DETALLE NORTE | RELACIÓN DE TAMAÑOS / REV 03')
    text('Misma escala para circulares y lineales | Sin ampliación individual de símbolos', 16, 266, 3.1)
    viewport(doc, detail, (210, 145), (390, 220), (29.5, 32.55), 5.5)
    text('Escala 1:25 | Aplique Ø390 mm; downlight Ø166 mm; lineal corta 599 × 77 mm', 16, 26, 2.8)
    text('La vista muestra un recorte del plano; no cambia posiciones ni constituye una revisión del montaje.', 16, 17, 2.6)
    return catalog.name, general.name, detail.name


def main(base, output):
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    doc = ezdxf.readfile(base)
    original = ezdxf.readfile(base)
    specs = dimensions()
    refs = [e for e in doc.modelspace().query('INSERT') if e.has_attrib('TIPO')]
    assert len(refs) == 162
    counts = Counter(e.get_attrib_text('TIPO') for e in refs)
    # Eliminar hojas de revisiones previas evita notas antiguas sobre tamaños gráficos.
    for name in list(doc.layouts.names()):
        if name.startswith('IE_'):
            doc.layouts.delete(name)
    rebuild_blocks(doc, specs)
    for ref in refs:
        code = ref.get_attrib_text('TIPO')
        spec = specs[code]
        ref.dxf.xscale = ref.dxf.yscale = ref.dxf.zscale = 1
        for tag, value in {
            'LARGO_CUERPO_MM': spec['largo_mm'], 'ANCHO_CUERPO_MM': spec['ancho_mm'],
            'DIAMETRO_CUERPO_MM': spec['diametro_mm'], 'REFERENCIA_DIMENSIONAL': spec['estado'],
        }.items():
            ref.add_attrib(tag, str(value), insert=ref.dxf.insert, dxfattribs={'flags': 1, 'height': .025, 'style': 'EI_LUM_REGULAR'})
    for e in original.modelspace():
        changed = doc.entitydb[e.dxf.handle]
        if e.dxftype() == 'INSERT' and e.has_attrib('TIPO'):
            assert e.dxf.insert == changed.dxf.insert and e.dxf.rotation == changed.dxf.rotation
            assert [a.dxfattribs() for a in e.attribs] == [a.dxfattribs() for a in changed.attribs[:len(e.attribs)]]
        else:
            assert e.dxfattribs() == changed.dxfattribs()
    sheets = create_sheets(doc, specs, counts)
    target = out/'SEMISOTANO_LUMINARIAS_MEDIDAS_REV03.dxf'
    doc.saveas(target)
    saved = ezdxf.readfile(target)
    audit = saved.audit()
    assert not audit.errors and not audit.fixes
    parking = [e for e in saved.modelspace().query('INSERT') if e.get_attrib_text('AMBIENTE') == ROOM]
    strips = beam_strips(saved.modelspace())
    ducts = projected_ducts(saved)
    assert len(parking) == 69
    assert all(not any(overlap(graphic_box(e), b['rect']) for b in strips+ducts) for e in parking)
    assert all(e.dxf.xscale == e.dxf.yscale == e.dxf.zscale == 1 for e in saved.modelspace().query('INSERT') if e.has_attrib('TIPO'))
    print('DXF: 162 posiciones conservadas, 12 bloques con medidas; estacionamiento sin superposiciones gráficas con las referencias contrastadas.', flush=True)
    pdf = fitz.open()
    for i, (name, size) in enumerate(zip(sheets, [(594, 420), (841, 594), (420, 297)])):
        page = render_sheet(saved, name, *size, '*')
        pdf.insert_pdf(page)
        if i == 0:
            page.save(out/'LUMINARIAS_MISMA_ESCALA_REV03.pdf', garbage=4, deflate=True)
            page[0].get_pixmap(dpi=130).save(out/'LUMINARIAS_MISMA_ESCALA_REV03.png')
        print('Hoja renderizada:', name, flush=True)
    pdf.save(out/'SEMISOTANO_LUMINARIAS_MEDIDAS_REV03_VISTA.pdf', garbage=4, deflate=True)
    pdf[2].get_pixmap(dpi=140).save(out/'DETALLE_PROPORCIONES_REV03.png')
    report = dict(luminarias=162, bloques=12, posiciones_modificadas=0, giros_modificados=0,
                  cantidades_por_tipo=dict(counts), escala_insercion_modelo=1, unidades='metros',
                  auditoria_errores=len(audit.errors), auditoria_correcciones=len(audit.fixes),
                  superposiciones_graficas_estacionamiento_con_franjas_y_proyecciones_contrastadas=0,
                  circular_vs_lineal_corta={'downlight_diametro_mm':166, 'aplique_diametro_mm':390, 'lineal_largo_mm':599, 'lineal_ancho_mm':77},
                  peraltes_alturas_y_recalculo='Pendientes, como en REV02',
                  dxf_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (out/'MEDIDAS_REFERENCIA_REV03.json').write_text(json.dumps(specs, ensure_ascii=False, indent=2))
    (out/'COMPROBACION_REV03.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    with (out/'MEDIDAS_REFERENCIA_REV03.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(next(iter(specs.values()))))
        writer.writeheader()
        writer.writerows(specs.values())
    (out/'LEEME_REV03.md').write_text('''# Luminarias proporcionadas por medidas — REV03

Un único DXF integrado: SEMISOTANO_LUMINARIAS_MEDIDAS_REV03.dxf. Unidades del modelo y de los bloques: metros. Las 162 referencias se insertan a escala 1, manteniendo los puntos, giros, cantidades y atributos anteriores. No se agregan recorridos ni códigos exteriores. Se conservan los trazos aprobados y las marcas LED interiores; la carcasa lineal ahora responde también a su ancho de referencia.

El PDF principal tiene tres páginas: las doce luminarias a escala común 1:10; plano general a 1:100; detalle norte a 1:25. Las luminarias pequeñas se ven pequeñas en el plano porque ya no se amplían individualmente. La lámina común muestra el detalle con proporciones comparables. Medidas del cuerpo, sin incluir salientes gráficos orientativos de presillas o pestañas.

Referencias: L-01 nominal 1.200 × aprox. 80 mm según cuadro; L-01-15 599 × 77 mm según LEDVANCE 4099854146671; L-01-18 nominal 600 × aprox. 80 mm; L-02 Ø390 mm según Philips WL140V; L-04B Ø166 mm exterior según Philips DN145B (no confundir con el corte de techo de 155 mm); L-03-IP65 cuerpo 595 × 595 mm según Philips RC132V. Las otras variantes L-03 mantienen el módulo nominal 600 × 600 mm del cuadro. L-04C: Ø180 mm provisional, estimado sin modelo exacto, no utilizado en este nivel. Consulte los enlaces y el estado de cada medida en MEDIDAS_REFERENCIA_REV03.json.

La corrección es dimensional. Se mantienen las 69 posiciones propuestas del estacionamiento y las otras 93 de referencia. Alturas, peraltes, montaje y cálculo lumínico siguen pendientes. Se conserva la comprobación de ausencia de superposiciones gráficas de los 69 puntos con las franjas y proyecciones de ductos contrastadas en REV02. No equivale a coordinación física 3D ni a validación de lux. Las medidas aproximadas deberán ajustarse al equipo definitivo.

Los campos ocultos LARGO_CUERPO_MM, ANCHO_CUERPO_MM, DIAMETRO_CUERPO_MM y REFERENCIA_DIMENSIONAL permiten consultar el tamaño sin añadir rótulos en planta. Fuentes OpenSans incluidas. DXF guardado, reabierto y auditado sin errores; no se ha abierto en AutoCAD en este entorno.
''', encoding='utf-8')
    for name in ['OpenSans-Regular.ttf', 'OpenSans-Semibold.ttf', 'LICENCIA_OPENSANS.txt']:
        shutil.copy2(Path(base).parent/name, out/name)
    package = out/'SEMISOTANO_LUMINARIAS_MEDIDAS_REV03.zip'
    with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in out.iterdir():
            if f.is_file() and f.suffix != '.zip':
                z.write(f, f.name)
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None and sum(n.endswith('.dxf') for n in z.namelist()) == 1
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
