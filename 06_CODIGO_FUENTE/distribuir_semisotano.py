"""Propuesta manual de 23 puntos, sin recorridos; arquitectura y Excel externos.

Uso: python distribuir_semisotano.py arquitectura.dxf cuadro.xlsx carpeta_salida
Los puntos se proponen junto a caras de muros/columnas. No son coordenadas
extraidas del Excel ni un diseno de alimentacion de equipos de bombeo.
"""
from pathlib import Path
from collections import Counter, defaultdict
import sys, json, csv, hashlib, copy
import ezdxf, openpyxl, fitz
from ezdxf.addons.drawing import RenderContext, Frontend, layout, pymupdf
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
from catalogo import catalogo
from geometria import crear_bloque

# Fila de SEMISOTANO, x, y, x/y del rotulo. Unidades: metros del modelo original.
PUNTOS = [
 (8,22.8,32.73,21.7,31.9),(8,30.5,32.73,28.2,31.9),
 (9,17.5,5.20,17.1,5.80),(9,21.73,6.85,19.4,6.30),
 (16,36.8,5.05,34.3,5.65),
 (17,26.7,5.05,26.2,5.65),(17,31.4,5.05,29.3,5.65),
 (18,27,8.22,26.7,8.85),(18,36.8,8.22,34.6,8.85),
 (18,41.27,15.6,38.6,14.4),
 (19,16.38,35.3,16.8,34.6),
 (20,48.6,5.05,45.6,5.65),
 (21,49.07,14.25,46.3,14.85),
 (22,20.72,36.4,20.9,36.9),(22,25.28,35.9,22.8,36.9),
 (25,24.7,8.21,22.0,8.3),
 (26,39.2,3.00,38.7,3.5),(26,43.5,3.00,42.0,3.5),
 (48,26.31,24.38,26.8,24.5),
 (48,32.94,16.6,33.4,16.7),
 (48,38.53,24.38,39.0,24.5),
 (49,49.22,18.7,46.5,18.9),(49,49.22,29.1,46.5,29.3),
]
RED='#bb2738'
BLUE='#1268b2'
INK='#20364d'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main(arq, excel, out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 d=ezdxf.readfile(arq);m=d.modelspace()
 assert d.header.get('$INSUNITS')==6, 'Se esperan metros'
 original_handles={e.dxf.handle for e in m}
 original_count=len(m)
 # Conservar las referencias originales. El DXF recibido no contiene sus
 # patrones: estos dos trazos se reconstruyen de forma provisional, documentada.
 for name,pattern in [('dash',[.6,.4,-.2]),('trazo pequeño',[.3,.2,-.1])]:
  if name not in d.linetypes:
   d.linetypes.new(name,dxfattribs={'description':'Patron provisional: faltaba en DXF recibido','pattern':pattern})
 a=d.audit();assert not a.errors and not a.fixes, (a.errors,a.fixes)
 d.styles.new('EI_TEXTO',dxfattribs={'font':'arial.ttf'})
 for name,col in [('IE-TOMAS-T01',RED),('IE-TOMAS-T02',BLUE),('IE-ROTULOS',INK),('IE-HOJA',INK)]:
  lay=d.layers.new(name,dxfattribs={'color':1 if 'T01' in name else 5,'lineweight':30})
  lay.dxf.true_color=int(col[1:],16)
 specs={s.nombre:copy.deepcopy(s) for s in catalogo() if s.nombre in ('IE_TN_M040','IE_TN_EST110')}
 for s in specs.values():
  s.datos.update(CORRIENTE='16 A',IP='IP20' if s.nombre=='IE_TN_M040' else 'IP55 minimo')
  s.datos.update(ESTADO='PROPUESTA DE UBICACION',FUENTE_CANTIDADES='Excel del usuario, hoja SEMISOTANO')
  crear_bloque(d,s)
 w=openpyxl.load_workbook(excel,data_only=True);s=w['SEMISÓTANO']
 records=[]
 for n,(row,x,y,lx,ly) in enumerate(PUNTOS,1):
  is_water=bool(s.cell(row,15).value)
  tipo='T-02' if is_water else 'T-01'
  spec=specs['IE_TN_EST110' if is_water else 'IE_TN_M040']
  layer='IE-TOMAS-'+('T02' if is_water else 'T01')
  circuit=s.cell(row,18).value.split('/')[-1].strip()
  vals=spec.atributos()
  vals.update(CODIGO=f'{n:02d}  {tipo}',TIPO=tipo,TABLERO='STD-SS',CIRCUITO=circuit,
    AMBIENTE=s.cell(row,2).value,ID=f'SS-{n:02d}',FILA_EXCEL=str(row),
    UBICACION_EXCEL=s.cell(row,19).value,
    OBSERVACIONES='Ubicacion propuesta sobre arquitectura; revisar posicion. Sin recorridos.',
    ORIGEN_COORDENADAS='PROPUESTA MANUAL SOBRE DXF; no coordenadas del Excel')
  ref=m.add_blockref(spec.nombre,(x,y),dxfattribs={'layer':layer,'xscale':.1,'yscale':.1,'zscale':.1})
  ref.add_auto_attribs(vals)
  for at in ref.attribs:
   at.dxf.layer=layer
   if at.dxf.tag=='CODIGO':
    at.is_invisible=False;at.dxf.insert=(lx,ly,0);at.dxf.height=.24;at.dxf.rotation=0
   elif at.dxf.tag=='DISTINTIVO':
    at.is_invisible=False;at.dxf.insert=(x+.26,y-.29,0);at.dxf.height=.18;at.dxf.rotation=0
   else:at.is_invisible=True
  # Campos nuevos, tambien editables, ausentes de la definicion inicial.
  known={at.dxf.tag for at in ref.attribs}
  for tag in vals.keys()-known:
   ref.add_attrib(tag,str(vals[tag]),(x,y),dxfattribs={'height':.24,'flags':1,'layer':layer,'style':'EI_TEXTO'})
  records.append(dict(id=f'SS-{n:02d}',tipo=tipo,ambiente=s.cell(row,2).value,
    x_m=x,y_m=y,altura=spec.datos['ALTURA'],tablero='STD-SS',circuito=circuit,
    cantidad_dobles=1,fila_excel=row,estado='PROPUESTA'))
 # Hoja A1: el modelo conserva la arquitectura 1:1 y unicamente 23 puntos.
 p=d.layouts.new('SS_DISTRIBUCION_A1')
 p.page_setup(size=(841,594),margins=(0,0,0,0),units='mm')
 vp=p.add_viewport(center=(280,296),size=(520,420),view_center_point=(25,20),view_height=42)
 vp.dxf.layer='Defpoints';vp.dxf.flags=16384
 def text(value,x,y,h=3.0,w=240,color=INK):
  return p.add_mtext(value,dxfattribs={'insert':(x,y),'width':w,'char_height':h,'style':'EI_TEXTO',
    'layer':'IE-HOJA','true_color':int(color[1:],16)})
 def line(x1,y1,x2,y2):p.add_line((x1,y1),(x2,y2),dxfattribs={'layer':'IE-HOJA','lineweight':15})
 p.add_lwpolyline([(10,10),(831,10),(831,584),(10,584)],close=True,dxfattribs={'layer':'IE-HOJA'})
 text('SEMISÓTANO | TOMACORRIENTES',22,568,7.0,790)
 text('PROPUESTA DE UBICACIÓN · REVISIÓN 01',22,552,4.0,790,BLUE)
 text('Arquitectura A01 + cuadro de cantidades del usuario',22,539,3.2,790)
 line(22,525,819,525)
 text('23 PUNTOS DOBLES',566,504,5.4)
 text('9 de muro + 14 estancos',566,493,3.8)
 text('SIMBOLOGÍA',566,475,3.4)
 for name,yy,col in [('IE_TN_M040',460,RED),('IE_TN_EST110',439,BLUE)]:
  q=p.add_blockref(name,(572,yy),dxfattribs={'xscale':1,'yscale':1,'zscale':1,'layer':'IE-TOMAS-T01' if col==RED else 'IE-TOMAS-T02'})
  q.add_auto_attribs({'DISTINTIVO':'T' if col==RED else 'T/PA'})
  for at in q.attribs:at.is_invisible=at.dxf.tag!='DISTINTIVO'
 text('T-01 · Doble 2P+T en muro\\P+0.40 m sobre NPT · 9 puntos',586,464,3.0,224,RED)
 text('T-02 · Doble 2P+T estanco\\P+1.10 m sobre NPT · 14 puntos',586,443,3.0,224,BLUE)
 text('RELACIÓN DE UBICACIONES',566,418,3.4)
 groups=defaultdict(list)
 for r in records:groups[r['ambiente']].append(r)
 names={8:'Vereda 01',9:'Cuarto de bombas',16:'Almacén general 01',17:'Almacén general 02',
  18:'Vereda 02',19:'Bombas de agua pluvial',20:'Cuarto de máquinas',21:'Cuarto de subtableros',
  22:'Depósito',25:'Hall de tanque cisterna',26:'Mantenimiento de ducto',48:'Circulación vehicular central',49:'Circulación vehicular lateral'}
 yy=405
 for rs in groups.values():
  ids=' / '.join(r['id'][-2:] for r in rs)
  text(ids,566,yy,3.0,38,BLUE if rs[0]['tipo']=='T-02' else RED)
  text(names[rs[0]['fila_excel']],604,yy,3.0,215)
  yy-=11
 line(566,yy,819,yy)
 text('LECTURA DEL PLANO',566,yy-10,3.4)
 text('Cada símbolo representa un punto doble.\\PEl número identifica su registro; T-01/T-02 indica el tipo.\\PAlturas referidas al nivel de piso terminado (NPT).',566,yy-23,3.0,248)
 text('ALCANCE DE ESTA REVISIÓN',566,yy-62,3.4)
 text('Ubicaciones propuestas para revisión sobre arquitectura.\\PLos sectores central y lateral se interpretan por geometría.\\PCircuitos del Excel guardados en atributos editables.\\PSin circuitos trazados ni canalizaciones.',566,yy-75,3.0,248)
 line(22,60,819,60)
 text('DISTRIBUCIÓN DE PUNTOS · PARA REVISIÓN',22,47,4.2,790)
 text('Modelo en metros · Escala de la ventana 1:100 en hoja A1 (841 × 594 mm) · SS-01',22,33,3.0,790)
 text('Base gráfica DGE 09-93-17; PA según 09-93-19. Cantidades y alturas: Excel recibido.',22,23,2.8,790)
 d.set_modelspace_vport(height=44,center=(25,20))
 assert len(m)==original_count+23 and original_handles.issubset({e.dxf.handle for e in m})
 fn=out/'SEMISOTANO_DISTRIBUCION_SIN_RECORRIDOS.dxf';d.saveas(fn)
 # Validar archivo realmente guardado.
 rd=ezdxf.readfile(fn);au=rd.audit();assert not au.errors and not au.fixes
 refs=list(rd.modelspace().query('INSERT'))
 assert len(refs)==23 and Counter(r.get_attrib_text('TIPO') for r in refs)=={'T-01':9,'T-02':14}
 assert Counter(r.get_attrib_text('CIRCUITO') for r in refs)=={'C-01':8,'C-02':7,'C-03':8}
 assert Counter(r['fila_excel'] for r in records)=={r:int(s.cell(r,12).value) for r in range(7,53) if s.cell(r,12).value}
 assert all(not e.dxf.layer.startswith('IE-') for e in rd.modelspace() if e.dxftype()!='INSERT')
 # Comprobar la geometria original sin depender de la representacion de linea.
 original_doc=ezdxf.readfile(arq)
 for old in original_doc.modelspace():
  new=rd.entitydb[old.dxf.handle]
  assert old.dxftype()==new.dxftype()
  assert old.dxf.all_existing_dxf_attribs()==new.dxf.all_existing_dxf_attribs(),old.dxf.handle
 # PDF vectorial de la hoja y PNG de vista previa.
 ctx=RenderContext(rd);backend=pymupdf.PyMuPdfBackend()
 front=Frontend(ctx,backend,config=Configuration(background_policy=BackgroundPolicy.WHITE,color_policy=ColorPolicy.COLOR))
 def override(entity,props):
  if not props.layer.startswith('IE-') and entity.dxftype()!='VIEWPORT':
   props.color='#4f5a66';props.lineweight=.16
 front.push_property_override_function(override)
 front.draw_layout(rd.layouts.get('SS_DISTRIBUCION_A1'),finalize=True)
 pdfraw=backend.get_pdf_bytes(layout.Page(841,594,layout.Units.mm),settings=layout.Settings(fit_page=False,scale=1))
 pd=fitz.open(stream=pdfraw,filetype='pdf')
 pd[0].set_mediabox(fitz.Rect(0,0,841*72/25.4,594*72/25.4))
 pd.save(out/'SEMISOTANO_DISTRIBUCION_SIN_RECORRIDOS.pdf')
 pd[0].get_pixmap(dpi=90,alpha=False).save(out/'SEMISOTANO_VISTA_PREVIA.png')
 clip=fitz.Rect(20*72/25.4,88*72/25.4,540*72/25.4,508*72/25.4)
 pd[0].get_pixmap(dpi=140,clip=clip,alpha=False).save(out/'SEMISOTANO_PUNTOS.png')
 with (out/'PUNTOS_PROPUESTOS.csv').open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
 report=dict(puntos=23,por_tipo={'T-01':9,'T-02':14},por_circuito={'C-01':8,'C-02':7,'C-03':8},
  entidades_arquitectura_conservadas=original_count,geometria_y_atributos_dxf_originales_conservados=True,
  auditoria_errores=0,auditoria_correcciones=0,recorridos_agregados=0,origen_coordenadas='Propuesta manual sobre arquitectura',
  coordenadas_del_excel_para_semisotano=False,patrones_arquitectura_reconstruidos_provisionalmente=['dash','trazo pequeño'],
  arquitectura_sha256=sha(arq),excel_sha256=sha(excel),dxf_sha256=sha(fn))
 (out/'COMPROBACION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 (out/'LEEME.md').write_text('''# Semisótano: distribución propuesta, revisión 01

Abra SEMISOTANO_DISTRIBUCION_SIN_RECORRIDOS.dxf. Contiene arquitectura y 23 puntos dobles en un solo archivo, en metros. La hoja SS_DISTRIBUCION_A1 muestra la propuesta a 1:100. El PDF y PNG son vistas de esa hoja. No se agregaron recorridos, cajas de paso, conductores ni trazos de circuitos.

Rojo: 9 puntos T-01 a +0.40 m NPT. Azul: 14 puntos T-02 estancos a +1.10 m NPT. La numeración 01 a 23 corresponde a PUNTOS_PROPUESTOS.csv. Cada inserción conserva tipo, altura, tablero, circuito, ambiente y fila del Excel como atributos editables. Los circuitos se guardan como datos y no están trazados.

Las coordenadas son una propuesta manual sobre el plano; el Excel no contiene coordenadas del semisótano. Se interpretaron por geometría los sectores vehiculares central/lateral, que no tienen rótulos equivalentes en el DXF. Se requiere revisión de ubicación, especialmente respecto a zonas de maniobra y equipos.

La arquitectura conserva sus entidades, coordenadas y atributos DXF. El archivo original hacía referencia a los tipos de línea ausentes `dash` y `trazo pequeño`; se agregaron patrones provisionales, no recuperados del archivo original. El fondo gris se aplica solo a la visualización PDF/PNG. Ninguna vista valida demanda, protecciones o alimentación de bombas. La propuesta cubre únicamente los tomacorrientes de servicio del cuadro.

La simbología usa la base DGE cotejada de la biblioteca: 09-93-17 y distintivo PA según 09-93-19. T-01/T-02 y la numeración son identificadores de proyecto; cada símbolo es un punto doble, no dos símbolos independientes.

Generación: `python 06_CODIGO_FUENTE/distribuir_semisotano.py arquitectura.dxf cuadro.xlsx carpeta_salida` (desde el repositorio). Dependencias: ezdxf, openpyxl, PyMuPDF. No se ha abierto en AutoCAD en este entorno.
''',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
 if len(sys.argv)!=4:raise SystemExit(__doc__)
 main(*sys.argv[1:])
