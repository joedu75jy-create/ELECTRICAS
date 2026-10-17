"""Integra las 162 posiciones DIALux con bloques nativos de la propuesta REV F.
Uso: python instalar_luminarias_semisotano.py base.dxf cuadro.xlsx memoria.pdf salida
No desplaza ni modifica la geometría de arquitectura y no agrega recorridos.
"""
from pathlib import Path
from collections import Counter
import sys,re,json,math,csv,hashlib,shutil,zipfile
import ezdxf,fitz,openpyxl
from ezdxf.addons.drawing import RenderContext,Frontend,layout,pymupdf
from ezdxf.addons.drawing.config import Configuration,BackgroundPolicy,ColorPolicy
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from presentar_todas_luminarias import Catalog,H,FONT

BLUE='#126b94';INK='#243849'
LINEWEIGHTS=[9,13,15,18,20,25,30,35,40,50,53,60,70,80,90,100,106,120,140,158,200,211]
WIDTHS={'L-01':16,'L-01-15':12,'L-01-18':12,'L-02':7,'L-04B':7,'L-04C':7}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class CADCanvas:
 """Adapta los mismos trazos de las láminas aprobadas a entidades nativas DXF."""
 def __init__(self,block,normalization=1):
  self.b=block;self.k=normalization;self.stroke='#000000';self.fill='#000000';self.lw=.2;self.font='OR';self.pt=10
 def point(self,x,y):return (x/mm*self.k,(y/mm-H)*self.k)
 def props(self):
  width=self.lw*self.k*100
  return dict(layer='0',color=0,lineweight=min(LINEWEIGHTS,key=lambda n:abs(n-width)))
 def setStrokeColor(self,c):self.stroke=c.hexval()
 def setFillColor(self,c):self.fill=c.hexval()
 def setLineWidth(self,w):self.lw=w/mm
 def setDash(self,*args):pass
 def setFont(self,name,size):self.font=name;self.pt=size
 def line(self,x,y,x2,y2):self.b.add_line(self.point(x,y),self.point(x2,y2),dxfattribs=self.props())
 def circle(self,x,y,r,stroke=1,fill=0):self.b.add_circle(self.point(x,y),r/mm*self.k,dxfattribs=self.props())
 def clear_rect(self,x,y,w,h):
  # Recortar líneas bajo la etiqueta sin introducir máscaras blancas en AutoCAD.
  x0,y0=self.point(x,y);x1,y1=self.point(x+w,y+h)
  for e in list(self.b.query('LINE')):
   a=e.dxf.start;b=e.dxf.end
   if abs(a.y-b.y)>1e-8 or not y0<a.y<y1:continue
   lo,hi=sorted([a.x,b.x])
   if hi<=x0 or lo>=x1:continue
   attrs=e.dxfattribs(drop={'handle','owner','start','end'})
   self.b.delete_entity(e)
   if lo<x0:self.b.add_line((lo,a.y),(min(x0,hi),a.y),dxfattribs=attrs)
   if hi>x1:self.b.add_line((max(x1,lo),a.y),(hi,a.y),dxfattribs=attrs)
 def rect(self,x,y,w,h,stroke=1,fill=0):
  if fill and self.fill.lower() in ('0xffffff','#ffffff'):
   self.clear_rect(x,y,w,h);return
  a=self.point(x,y);b=self.point(x+w,y+h)
  self.b.add_lwpolyline([a,(b[0],a[1]),b,(a[0],b[1])],close=True,dxfattribs=self.props())
 def roundRect(self,x,y,w,h,r,stroke=1,fill=0):
  xx,yy=self.point(x,y);ww=w/mm*self.k;hh=h/mm*self.k;rr=r/mm*self.k;t=math.tan(math.pi/8)
  pts=[(xx+rr,yy,0),(xx+ww-rr,yy,t),(xx+ww,yy+rr,0),(xx+ww,yy+hh-rr,t),
   (xx+ww-rr,yy+hh,0),(xx+rr,yy+hh,t),(xx,yy+hh-rr,0),(xx,yy+rr,t)]
  self.b.add_lwpolyline(pts,format='xyb',close=True,dxfattribs=self.props())
 def drawString(self,x,y,value):
  bold=self.font in ('B','OB');font=pdfmetrics.getFont(self.font)
  height=self.pt/mm*(font.face.capHeight/1000)*self.k
  self.b.add_text(str(value),dxfattribs={**self.props(),'insert':self.point(x,y),'height':height,
   'style':'EI_LUM_BOLD' if bold else 'EI_LUM_REGULAR'})


def extract(memoria):
 doc=fitz.open(memoria);r=[]
 for page_index,page in enumerate(doc):
  text=page.get_text()
  if page_index<15 or 'Plano de situación de luminarias' not in text:continue
  room=text.split('Plano de situación')[0].split('·')[-1].strip().replace('\n',' ').split(' - ')[0].strip()
  npt=re.search(r'NPT (-\d+\.\d+)',text)
  for x,y,z,n in re.findall(r'(\d+\.\d+) m\s+(\d+\.\d+) m\s+(\d+\.\d+) m\s+(\d+)\b',text):
   r.append(dict(ambiente=room,x_m=float(x),y_m=float(y),altura_m=float(z),numero_local=int(n),
    pagina_pdf=page_index+1,npt=float(npt[1]) if npt else ''))
 assert len(r)==162 and len({(p['x_m'],p['y_m']) for p in r})==162
 return r


def normalize(t):
 import unicodedata
 return re.sub('[^A-Z0-9]','',unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode().upper())


def build_blocks(d,types):
 for name,file in [('OR','OpenSans-Regular.ttf'),('R','OpenSans-Regular.ttf'),('OB','OpenSans-Semibold.ttf'),('B','OpenSans-Semibold.ttf')]:
  pdfmetrics.registerFont(TTFont(name,FONT+file))
 for name,file in [('EI_LUM_REGULAR','OpenSans-Regular.ttf'),('EI_LUM_BOLD','OpenSans-Semibold.ttf')]:
  if name not in d.styles:d.styles.new(name,dxfattribs={'font':file})
 for code,s in types.items():
  name='EI_LUM_'+code.replace('-','_');s['bloque']=name
  block=d.blocks.new(name);block.block_record.dxf.units=0
  ref_size=72 if code=='L-01' else 47 if code.startswith('L-01-') else 27
  size=WIDTHS.get(code,8);s['tamano_papel_mm']=size
  renderer=Catalog(CADCanvas(block,size/ref_size));renderer.lamp(code,0,0,ref_size)
  for tag in ['ID','TIPO','DESCRIPCION','POTENCIA_W','FLUJO_NOMINAL_LM','FLUJO_CALCULO_LM','IP','MONTAJE',
   'ALTURA_M','NPT_M','AMBIENTE','PAGINA_PDF','NUMERO_LOCAL','FUENTE_XY','GIRO_REFERENCIA','ESTADO']:
   block.add_attdef(tag,insert=(0,0),height=2.5,text='',dxfattribs={'flags':1,'style':'EI_LUM_REGULAR','layer':'0'})


def main(base,excel,memoria,out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 records=extract(memoria)
 w=openpyxl.load_workbook(excel,data_only=True);legend=w['Leyenda'];ss=w['Semisótano']
 types={legend.cell(r,1).value:dict(descripcion=legend.cell(r,2).value,potencia=legend.cell(r,3).value,
  flujo=legend.cell(r,4).value,ip=legend.cell(r,7).value,montaje=legend.cell(r,8).value) for r in range(5,17)}
 roommap={normalize(ss.cell(r,2).value):(ss.cell(r,3).value,r) for r in range(5,22)}
 d=ezdxf.readfile(base);m=d.modelspace();assert d.header.get('$INSUNITS')==6
 original_handles={e.dxf.handle for e in m};original_count=len(m)
 a=d.audit();assert not a.errors and not a.fixes
 build_blocks(d,types)
 used=Counter()
 for p in records:
  code,row=roommap[normalize(p['ambiente'])];p['tipo']=code;p['fila_excel']=row
  used[code]+=1
  p['potencia_w']=float(str(types[code]['potencia']).replace(',','.'))
  p['giro']=0 if p['ambiente']=='ACCESO VEHICULAR Y RAMPA' or not code.startswith('L-01') else 90
  p['observacion']=''
  if p['ambiente']=='CIRCULACION VEREDA 02' and p['numero_local']==20:
   p['observacion']='Unidad individual pagina 118; equivale a la fila sin local asignado del Excel.'
 assert used=={'L-01':20,'L-01-15':118,'L-02':13,'L-04B':7,'L-03-IP65':4}
 for code in used:
  lay=d.layers.new('IE-LUM-'+code,dxfattribs={'color':5,'lineweight':18})
  lay.dxf.true_color=int(BLUE[1:],16)
 layer=d.layers.new('IE-LAMINA',dxfattribs={'color':5,'lineweight':18});layer.dxf.true_color=int(INK[1:],16)
 for n,p in enumerate(records,1):
  code=p['tipo'];spec=types[code];p['id']=f'SS-L{n:03d}'
  vals=dict(ID=p['id'],TIPO=code,DESCRIPCION=spec['descripcion'],POTENCIA_W=str(p['potencia_w']),
   FLUJO_NOMINAL_LM=str(spec['flujo']),FLUJO_CALCULO_LM='2249' if code=='L-01-15' else str(spec['flujo']),IP=spec['ip'],
   MONTAJE=spec['montaje'],ALTURA_M=str(p['altura_m']),NPT_M=str(p['npt']),AMBIENTE=p['ambiente'],
   PAGINA_PDF=str(p['pagina_pdf']),NUMERO_LOCAL=str(p['numero_local']),FUENTE_XY='Memoria DIALux REV1 del usuario',
   GIRO_REFERENCIA='Lam. situacion; rampa horizontal, otras lineales verticales',ESTADO='DISTRIBUCION PARA REVISION VISUAL')
  ref=m.add_blockref(spec['bloque'],(p['x_m'],p['y_m'],0),dxfattribs={'layer':'IE-LUM-'+code,
   'xscale':.1,'yscale':.1,'zscale':.1,'rotation':p['giro']})
  ref.add_auto_attribs(vals)
  assert len(ref.attribs)==len(vals) and all(a.is_invisible for a in ref.attribs)
 # Conservar cotas, ejes, arquitectura, y estados originales de sus capas.
 # La visualización gris de arquitectura se aplica al PDF, no a la geometría CAD.
 def sheet(name,width,height,center,size,view_center,view_height,title,scale,overview=False):
  p=d.layouts.new(name);p.page_setup(size=(width,height),margins=(0,0,0,0),units='mm')
  vp=p.add_viewport(center=center,size=size,view_center_point=view_center,view_height=view_height)
  vp.dxf.layer='Defpoints';vp.dxf.flags=16384
  def txt(text,x,y,h=3,w=170):
   p.add_mtext(text,dxfattribs={'insert':(x,y),'char_height':h,'width':w,'style':'EI_LUM_REGULAR','layer':'IE-LAMINA'})
  p.add_lwpolyline([(8,8),(width-8,8),(width-8,height-8),(8,height-8)],close=True,dxfattribs={'layer':'IE-LAMINA'})
  txt(title,16,height-19,6 if overview else 4.5,width-32)
  txt('Distribución de luminarias para revisión visual · Sin recorridos',16,height-32,3.2,width-32)
  if overview:
   txt('162 LUMINARIAS',641,518,5,180)
   txt('2.931 W · 5 tipos utilizados',641,507,3.4,180)
   txt('LEYENDA',641,484,3.4)
   names={'L-01':'Lineal larga LED · 36 W','L-01-15':'Lineal corta LED · 15W-A','L-02':'Aplique circular · 20 W',
    'L-04B':'Downlight empotrado · 11 W','L-03-IP65':'Panel hermético · 26 W'}
   for i,code in enumerate(['L-01','L-01-15','L-02','L-04B','L-03-IP65']):
    yy=464-i*42
    q=p.add_blockref(types[code]['bloque'],(650,yy),dxfattribs={'layer':'IE-LUM-'+code})
    txt(f'{code} · {used[code]} unidades',665,yy+5,3.3,156)
    txt(names[code],665,yy-2,2.8,156)
   txt('LECTURA',641,237,3.4)
   txt('Los símbolos en planta no llevan códigos exteriores. Tipo, altura, ambiente y fuente quedan como atributos editables.',641,227,3,175)
   txt('POSICIONES',641,192,3.4)
   txt('Coordenadas y alturas de la memoria DIALux REV1. Se conserva la unidad individual de Vereda 02 (pág. 118).',641,181,3,175)
   txt('ALCANCE',641,144,3.4)
   txt('Dibujo en planta XY. Las alturas se guardan como datos. El tamaño del símbolo es gráfico; no es la huella física del equipo.',641,133,3,175)
  txt(f'Escala {scale} · Modelo en metros · Fuente: arquitectura y memoria del usuario',16,27,2.8,width-32)
  txt('Bloques según propuesta gráfica REV F · Cantidades y montaje sujetos a revisión del proyecto definitivo',16,18,2.6,width-32)
  return p
 sheets=[sheet('IE_LUMINARIAS_A1',841,594,(318,290),(600,480),(25,20.2),48,'SEMISÓTANO | LUMINARIAS INTEGRADAS','1:100',True)]
 sheets.append(sheet('IE_DETALLE_NORTE_A3',420,297,(210,145),(390,235),(21.5,33.5),17.625,'SEMISÓTANO | DETALLE NORTE','1:75'))
 sheets.append(sheet('IE_DETALLE_BOMBAS_A3',420,297,(210,145),(390,235),(21.5,8.5),11.75,'SEMISÓTANO | BOMBAS Y CISTERNAS','1:50'))
 sheets.append(sheet('IE_DETALLE_SUR_A3',420,297,(210,145),(390,235),(40.2,9),11.75,'SEMISÓTANO | ALMACENES Y SERVICIOS','1:50'))
 # Actualizar la vista existente conserva sus objetos asociados (incluido SUN).
 active=d.viewports.get('*Active')[0];active.dxf.height=49;active.dxf.center=(25,20)
 assert len(m)==original_count+162 and original_handles.issubset({e.dxf.handle for e in m})
 target=out/'SEMISOTANO_LUMINARIAS_INTEGRADAS.dxf';d.saveas(target)
 rd=ezdxf.readfile(target);audit=rd.audit();assert not audit.errors and not audit.fixes
 refs=[e for e in rd.modelspace().query('INSERT') if e.dxf.layer.startswith('IE-LUM-')]
 assert len(refs)==162 and Counter(e.get_attrib_text('TIPO') for e in refs)==used
 assert all(all(a.is_invisible for a in e.attribs) for e in refs)
 assert all(e.dxftype()=='INSERT' for e in rd.modelspace() if e.dxf.layer.startswith('IE-'))
 # Revisar coordenadas realmente guardadas, no solo los datos en memoria.
 for p,e in zip(records,refs):
  assert math.dist((p['x_m'],p['y_m']),tuple(e.dxf.insert)[:2])<1e-9
  assert float(e.get_attrib_text('ALTURA_M'))==p['altura_m']
 original=ezdxf.readfile(base)
 for e in original.modelspace():
  new=rd.entitydb[e.dxf.handle]
  assert e.dxftype()==new.dxftype()
  assert e.dxf.all_existing_dxf_attribs()==new.dxf.all_existing_dxf_attribs(),e.dxf.handle
 # PDF de las hojas CAD realmente guardadas.
 pdf=fitz.open()
 for i,source in enumerate(sheets):
  backend=pymupdf.PyMuPdfBackend();front=Frontend(RenderContext(rd),backend,config=Configuration(background_policy=BackgroundPolicy.WHITE,color_policy=ColorPolicy.COLOR))
  def override(entity,props):
   if not props.layer.startswith('IE-') and entity.dxftype()!='VIEWPORT':
    props.color='#7b838b';props.lineweight=.10
  front.push_property_override_function(override)
  front.draw_layout(rd.layouts.get(source.name),finalize=True)
  ww,hh=(841,594) if i==0 else (420,297)
  raw=backend.get_pdf_bytes(layout.Page(ww,hh,layout.Units.mm),settings=layout.Settings(fit_page=False,scale=1))
  page_doc=fitz.open(stream=raw,filetype='pdf');page_doc[0].set_mediabox(fitz.Rect(0,0,ww*mm,hh*mm))
  pdf.insert_pdf(page_doc)
 pdf.save(out/'SEMISOTANO_LUMINARIAS_VISTA.pdf')
 pdf[0].get_pixmap(dpi=110,clip=fitz.Rect(18*mm,64*mm,618*mm,544*mm),alpha=False).save(out/'SEMISOTANO_LUMINARIAS.png')
 for i in range(1,4):pdf[i].get_pixmap(dpi=110,alpha=False).save(out/f'DETALLE_LUMINARIAS_{i:02d}.png')
 with (out/'LUMINARIAS_COLOCADAS.csv').open('w',encoding='utf-8-sig',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(records[0]));wr.writeheader();wr.writerows(records)
 report=dict(luminarias=162,por_tipo=dict(used),potencia_w=sum(p['potencia_w'] for p in records),
  bloques_de_luminarias_disponibles=len(types),entidades_originales_conservadas=original_count,
  auditoria_errores=len(audit.errors),auditoria_correcciones=len(audit.fixes),rotulos_exteriores=0,recorridos=0,
  fuente_xy='Tablas de posiciones, memoria DIALux REV1',unidad_individual_vereda_02='Pagina 118, luminaria 20: X=40.520 Y=15.187 h=2.990',
  arquitectura_sha256=sha(base),excel_sha256=sha(excel),memoria_sha256=sha(memoria),dxf_sha256=sha(target),
  giro='Rampa: horizontal; otras lineales: vertical, segun planos de situacion. Giros leidos visualmente, no de tabla angular.',
  alturas='Atributos en metros, insercion XY en Z=0; no se crea modelo de montaje 3D.',
  validacion_autocad='No disponible en este entorno; DXF guardado/reabierto/auditado y PDF renderizado de sus hojas.')
 assert report['potencia_w']==2931
 (out/'COMPROBACION_LUMINARIAS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 (out/'COORDENADAS_DIALUX.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
 (out/'LEEME.md').write_text('''# Semisótano: luminarias integradas, revisión visual 01

Abra SEMISOTANO_LUMINARIAS_INTEGRADAS.dxf. El modelo está en metros y contiene la base recibida más 162 inserciones de luminarias; no contiene recorridos nuevos ni códigos exteriores junto a los símbolos. La hoja IE_LUMINARIAS_A1 es la vista general a 1:100; otras tres hojas A3 muestran detalles. El PDF procede de estas hojas CAD.

Las doce definiciones de bloques reproducen los trazos de las propuestas aprobadas. En este nivel se utilizan cinco tipos: L-01 (20), L-01-15 / 15W-A (118), L-02 (13), L-04B (7) y L-03-IP65 (4). Total: 162 unidades y 2.931 W. Los símbolos tienen tamaño gráfico para la escala de impresión; no sirven para medir dimensiones físicas de luminarias.

Las 162 coordenadas XY y alturas se extraen de las tablas de la memoria DIALux REV1. La orientación de las lineales se toma visualmente de los planos de situación: rampa horizontal; las otras verticales. La unidad individual de Vereda 02 (página 118, n.º 20) se conserva: corresponde a la unidad que el Excel dejó sin local. En el resto, las cantidades por ambiente coinciden con el Excel.

ID, tipo, altura, ambiente, potencia, flujo, protección y página de la memoria son atributos editables ocultos. Las alturas no se aplican a la coordenada Z: esta entrega es un plano XY. Los L-02 mantienen las posiciones de DIALux y la descripción de pared del Excel; el montaje y las interferencias deben contrastarse con el proyecto definitivo. No se ha recalculado la iluminación ni se ha verificado el diseño definitivo.

La arquitectura conserva geometría, capas y estados originales; mobiliario y cotas que venían apagados siguen incluidos. La representación gris del fondo es un ajuste de visualización del PDF. No se incorporaron los tomacorrientes propuestos en la entrega anterior.

Fuentes OpenSans-Regular.ttf y OpenSans-Semibold.ttf incluidas para conservar el aspecto. Si AutoCAD sustituye las fuentes, instálelas o añada la carpeta a su ruta de fuentes y regenere. No hay referencias externas a imágenes. No se ha abierto en AutoCAD en este entorno.
''',encoding='utf-8')
 for name in ['OpenSans-Regular.ttf','OpenSans-Semibold.ttf']:shutil.copy2(Path(FONT)/name,out/name)
 license_path=Path('/usr/share/doc/fonts-open-sans/copyright')
 if license_path.exists():shutil.copy2(license_path,out/'LICENCIA_OPENSANS.txt')
 files=[p for p in out.iterdir() if p.is_file() and p.suffix!='.zip']
 zip_path=out/'SEMISOTANO_LUMINARIAS_ENTREGA.zip'
 with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
  for p in files:z.write(p,p.name)
 with zipfile.ZipFile(zip_path) as z:
  assert z.testzip() is None and sum(n.endswith('.dxf') for n in z.namelist())==1
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
 if len(sys.argv)!=5:raise SystemExit(__doc__)
 main(*sys.argv[1:])
