"""Láminas de propuesta visual; no crea bloques ni modifica planos/Excel.
Uso: python propuesta_luminarias_pdf.py cuadro.xlsx carpeta_salida
"""
from pathlib import Path
import sys, json
import openpyxl, fitz
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor

W,H=420,297
INK='#172e43';BLUE='#116e95';GREY='#647483';PALE='#edf3f6';EDGE='#cbd7df';BLACK='#12191e'
FONT='/usr/share/fonts/truetype/open-sans/'
SOURCES=[
 ('S1','Cuadro de luminarias recibido','Leyenda, Resumen y hojas por piso. Fuente de códigos, cantidades, potencia, flujo, IP y montaje.',''),
 ('S2','Memoria de iluminación del semisótano, REV1','Páginas 10–15 y planos de situación: cinco modelos de referencia.',''),
 ('S3','LEDVANCE DAMP PROOF PFM 15 W','Artículo 4099854146671. Referencia de carcasa lineal; web consultada: 599 × 77 × 68 mm.','https://www.ledvance.com/pt-br/iluminacao-profissional/produtos/luminarias/luminarias-com-tecnologia-led-para-teto--parede-e-piso/luminarias-hermeticas-com-e-sem-led-integrado-para-uso-profissional-ip65/luminarias-hermeticas-com-led-integrado-c232595?productId=261282'),
 ('S4','Philips WL140V / aplique L-02','Artículo 911401847682. Referencia circular: diámetro 390 mm, espesor 85 mm.','https://www.assets.signify.com/is/content/Signify/911401847682_EU.en_SA.PROF.FP'),
 ('S5','Philips DN145B / downlight L-04B','Artículo 911401806080: diámetro exterior 166 mm; corte 155 mm; altura 28 mm.','https://www.signify.com/global/prof/indoor-luminaires/downlights/philips-coreline-slimdownlight/911401806080_EU/product'),
 ('S6','Philips RC132V / panel L-03-IP65','Artículo 911401891585: cuerpo 595 × 595 × 65 mm; módulo nominal 600 × 600 mm.','https://www.signify.com/cs-cz/prof/interierova-svitidla/zapustene/philips-coreline-panel-gen6/911401891585_EU/product'),
 ('S7','DGE: simbología, sección 9','Figuras 09-93-51/52/53 y 09-93-60. Copia de consulta archivada en el repositorio.','https://www.gob.pe/institucion/minem/normas-legales/108773-0091-2002-mem'),
]


class Sheet:
 def __init__(self,c):self.c=c;self.n=0
 def txt(self,x,y,t,size=10,bold=False,col=INK):
  self.c.setFillColor(HexColor(col));self.c.setFont('OB' if bold else 'OR',size)
  self.c.drawString(x*mm,(H-y)*mm,str(t))
 def para(self,x,y,width,t,size=9,col=INK):
  style=ParagraphStyle('p',fontName='OR',fontSize=size,leading=size*1.42,textColor=HexColor(col))
  obj=Paragraph(t,style);_,hh=obj.wrap(width*mm,240*mm)
  obj.drawOn(self.c,x*mm,(H-y)*mm-hh)
  return hh/mm
 def line(self,x,y,x2,y2,col=INK,lw=.25,dash=None):
  self.c.setStrokeColor(HexColor(col));self.c.setLineWidth(lw*mm)
  self.c.setDash([z*mm for z in dash] if dash else [])
  self.c.line(x*mm,(H-y)*mm,x2*mm,(H-y2)*mm);self.c.setDash([])
 def rect(self,x,y,w,h,fill=None,col=EDGE,lw=.25,r=0):
  self.c.setStrokeColor(HexColor(col));self.c.setLineWidth(lw*mm)
  if fill:self.c.setFillColor(HexColor(fill))
  if r:self.c.roundRect(x*mm,(H-y-h)*mm,w*mm,h*mm,r*mm,stroke=1,fill=bool(fill))
  else:self.c.rect(x*mm,(H-y-h)*mm,w*mm,h*mm,stroke=1,fill=bool(fill))
 def circle(self,x,y,r,fill=None,col=BLACK,lw=.3):
  self.c.setStrokeColor(HexColor(col));self.c.setLineWidth(lw*mm)
  if fill:self.c.setFillColor(HexColor(fill))
  self.c.circle(x*mm,(H-y)*mm,r*mm,stroke=1,fill=bool(fill))
 def header(self,title,sub):
  self.n+=1
  self.txt(16,15,'MCF PIURA / PROPUESTA GRÁFICA DE LUMINARIAS',9,True,BLUE)
  self.txt(16,29,title,23,True)
  self.txt(16,40,sub,10,col=GREY)
  self.line(16,47,404,47,EDGE)
 def footer(self,note='CONTORNOS PROPUESTOS PARA REVISIÓN · No modifica el cuadro ni la distribución.'):
  self.line(16,280,404,280,EDGE)
  self.txt(16,287,note,8,col=GREY)
  self.txt(367,287,f'REV A / {self.n:02d}',8,True,BLUE)
  self.c.showPage()
 def anchor(self,x,y):
  self.line(x-1.5,y,x+1.5,y,BLUE,.18);self.line(x,y-1.5,x,y+1.5,BLUE,.18)
 def physical(self,kind,x,y,size=22,anchor=False):
  if kind in ('linear_long','linear_short'):
   ww=size;hh=max(2.8,ww/15.5)
   self.rect(x-ww/2,y-hh/2,ww,hh,'#ffffff',BLACK,.32,.6)
   self.rect(x-ww/2+1.5,y-hh/2+.65,ww-3,hh-1.3,None,GREY,.18,.35)
   self.line(x-ww/2+2,y-hh/2,x-ww/2+2,y+hh/2,BLACK,.2)
   self.line(x+ww/2-2,y-hh/2,x+ww/2-2,y+hh/2,BLACK,.2)
  elif kind=='panel':
   self.rect(x-size/2,y-size/2,size,size,'#ffffff',BLACK,.35)
   self.rect(x-size/2+1,y-size/2+1,size-2,size-2,None,GREY,.18)
  else:
   self.circle(x,y,size/2,'#ffffff',BLACK,.35)
   self.circle(x,y,size/2-(.8 if kind=='down_recess' else 1.2),None,GREY,.18)
  if anchor:self.anchor(x,y)
 def norm(self,kind,x,y,k=1):
  if kind=='linear':
   self.line(x-6*k,y,x+6*k,y,BLACK,.35)
   for xx in [x-6*k,x+6*k]:self.line(xx,y-k,xx,y+k,BLACK,.35)
  else:
   self.circle(x,y,2*k,BLACK if kind=='recess' else '#ffffff',BLACK,.3)
   for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
    self.line(x+2*k*dx,y+2*k*dy,x+3.5*k*dx,y+3.5*k*dy,BLACK,.3)
   if kind=='wall':
    self.line(x-4*k,y-2*k,x-4*k,y+2*k,BLACK,.3)
    self.line(x-4*k,y,x-3.5*k,y,BLACK,.3)


def main(excel,out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 pdfmetrics.registerFont(TTFont('OR',FONT+'OpenSans-Regular.ttf'))
 pdfmetrics.registerFont(TTFont('OB',FONT+'OpenSans-Semibold.ttf'))
 w=openpyxl.load_workbook(excel,data_only=True);leg=w['Leyenda'];summ=w['Resumen']
 def numeric(v):return float(str(v).replace(' ','').replace(',','.'))
 def f(v):return str(int(v)) if float(v).is_integer() else str(v).replace('.',',')
 specs=[]
 for r in range(5,17):
  code=leg.cell(r,1).value
  kind='linear_long' if code=='L-01' else 'linear_short' if code.startswith('L-01-') else 'wall' if code=='L-02' else 'panel' if code.startswith('L-03') else 'down_recess' if code=='L-04B' else 'down_surface'
  specs.append(dict(code=code,desc=leg.cell(r,2).value,power=numeric(leg.cell(r,3).value),lm=numeric(leg.cell(r,4).value),
    ip=leg.cell(r,7).value,mount=leg.cell(r,8).value,qty=summ.cell(r,9).value,kind=kind))
 assert len(specs)==12 and sum(s['qty'] for s in specs)==1625
 by={s['code']:s for s in specs}
 path=out/'PROPUESTA_BLOQUES_LUMINARIAS_REV_A.pdf'
 c=canvas.Canvas(str(path),pagesize=(W*mm,H*mm),pageCompression=1)
 c.setTitle('MCF Piura · Propuesta visual de 12 bloques de luminarias · Rev A')
 c.setAuthor('ELECTRICAS · propuesta para revisión del usuario')
 sh=Sheet(c)

 # 1: presentación de todos los tipos, sin convertir atributos en símbolos inventados.
 sh.header('Así podrían verse los 12 tipos','Contorno físico simplificado + código visible · Dibujos ampliados, sin escala común · Revisión previa a crear los bloques')
 titles={'L-01':'Lineal larga · 1,20 m nominal','L-01-15':'Lineal corta · aprox. 0,60 m','L-01-18':'Lineal corta · 0,60 m nominal','L-02':'Aplique circular · vista frontal',
  'L-03':'Panel empotrado · módulo 60 × 60','L-03-D':'Panel empotrado · DALI','L-03A':'Panel · flujo reducido','L-03-DA':'Panel · flujo reducido + DALI',
  'L-03-IP65':'Panel · variante hermética','L-03-90':'Panel · IRC ≥ 90','L-04B':'Downlight empotrable','L-04C':'Downlight de superficie'}
 for i,s in enumerate(specs):
  x=16+(i%4)*98;y=55+(i//4)*71
  sh.rect(x,y,94,66,'#ffffff',EDGE,.2,1.8)
  sh.txt(x+5,y+8,s['code'],13,True)
  sh.txt(x+5,y+15,titles[s['code']],8.3,col=GREY)
  size=65 if s['kind']=='linear_long' else 34 if s['kind']=='linear_short' else 22 if s['kind']=='panel' else 19
  sh.physical(s['kind'],x+47,y+34,size)
  sh.txt(x+5,y+52,f"{f(s['power'])} W · {f(s['lm'])} lm · {s['ip']}",8.3)
  sh.txt(x+5,y+60,f"{s['qty']} unidades en el cuadro",8,col=GREY)
 sh.para(18,270,380,'Las seis variantes de panel comparten forma; el código conserva la diferencia de driver, flujo, IRC e IP. La simbología eléctrica DGE se compara en la lámina 5.',8)
 sh.footer()

 # 2: familia lineal.
 sh.header('01 / Lineales herméticas','Idea: carcasa alargada, difusor continuo y extremos simples. Geometría ligera para repetirse en planta.')
 lines=[('L-01','1,20 m nominal','Ancho orientativo: aprox. 0,08 m','Referencia del modelo de 36 W: memoria, pág. 12. El cuadro define largo nominal de 1,20 m.'),
  ('L-01-15','Aprox. 0,60 m','Referencia web: 599 × 77 × 68 mm','Modelo 4099854146671 identificado en la memoria. El flujo del cálculo es 2.249 lm; la leyenda lo redondea a 2.250 lm.'),
  ('L-01-18','0,60 m nominal','Ancho y espesor por confirmar','La leyenda especifica 15 W / 1.800 lm. Se propone la forma corta de la familia; falta el modelo exacto de esta variante.')]
 for i,(code,dim,sub,note) in enumerate(lines):
  x=16+i*132;s=by[code]
  sh.rect(x,56,124,211,None,EDGE,.2,1.5)
  sh.txt(x+6,68,code,18,True)
  sh.txt(x+6,78,f"{f(s['power'])} W / {f(s['lm'])} lm / IP65",10,col=BLUE)
  sh.txt(x+6,93,'FORMA VISTA DESDE ABAJO',8.5,True,GREY)
  ww=96 if i==0 else 48
  sh.physical(s['kind'],x+62,111,ww)
  sh.txt(x+6,129,dim,10,True)
  sh.txt(x+6,137,sub,8.5,col=GREY)
  sh.txt(x+6,154,'BLOQUE PROPUESTO EN PLANTA',8.5,True,GREY)
  sh.physical(s['kind'],x+52,174,68 if i==0 else 34,True)
  sh.txt(x+8,189,code,10,True)
  sh.para(x+6,202,112,note,9)
  sh.para(x+6,245,112,'Cruz azul: punto de inserción propuesto en el centro; es una guía de esta lámina.',8,col=BLUE)
 sh.footer('El largo de L-01 procede del cuadro; los demás anchos no verificados se muestran como aproximaciones. Fuentes S1–S3.')

 # 3: familia de paneles.
 sh.header('02 / Paneles de 60 × 60 cm','Un contorno cuadrado con borde y difusor. La etiqueta distingue las seis versiones sin alterar su forma.')
 panels=[s for s in specs if s['kind']=='panel']
 for i,s in enumerate(panels):
  x=16+i%3*132;y=56+i//3*108
  sh.rect(x,y,124,102,None,EDGE,.2,1.5)
  sh.txt(x+6,y+12,s['code'],16,True)
  sh.txt(x+6,y+21,f"{f(s['power'])} W · {f(s['lm'])} lm · {s['ip']}",9.5,col=BLUE)
  sh.physical('panel',x+30,y+52,32,True)
  sh.txt(x+53,y+41,'60 × 60 cm nominal',9,True)
  note=('Driver regulable DALI' if s['code'] in ('L-03-D','L-03-DA') else 'Versión hermética' if s['code']=='L-03-IP65' else 'IRC ≥ 90' if s['code']=='L-03-90' else 'Flujo reducido' if s['code']=='L-03A' else 'Versión estándar')
  sh.para(x+53,y+47,64,note+'<br/>Empotrado en FCR<br/>Código junto al contorno',9)
  sh.para(x+6,y+78,111,'Referencia dimensional comprobada para L-03-IP65: 595 × 595 mm de cuerpo. Las otras variantes conservan el módulo nominal del Excel.',8,col=GREY)
 sh.footer('DALI, IP e IRC se identifican mediante código y atributos. El contorno es una representación física de proyecto. Fuentes S1, S2 y S6.')

 # 4: elementos circulares, distinguiendo frontal de planta del aplique de muro.
 sh.header('03 / Aplique y downlights','La cara circular ayuda a reconocer el equipo. El montaje determina cómo se presenta en planta y en detalle.')
 codes=['L-02','L-04B','L-04C']
 for i,code in enumerate(codes):
  x=16+i*132;s=by[code]
  sh.rect(x,56,124,211,None,EDGE,.2,1.5)
  sh.txt(x+6,68,code,18,True)
  sh.txt(x+6,78,f"{f(s['power'])} W / {f(s['lm'])} lm",10,col=BLUE)
  sh.txt(x+6,93,'CARA DEL EQUIPO · ESQUEMA',8.5,True,GREY)
  sh.physical(s['kind'],x+62,117,32)
  if i==0:
   sh.txt(x+6,144,'Ø 390 mm de referencia [S4]',9,True)
   sh.txt(x+6,157,'PLANTA DE MONTAJE EN MURO',8.5,True,GREY)
   sh.line(x+29,174,x+95,174,INK,.65)
   sh.rect(x+46,175,32,7,None,BLACK,.3,1)
   sh.para(x+6,194,112,'Se propone un cuerpo delgado junto al muro en planta y el círculo en elevación. El símbolo DGE de pared se muestra en la lámina 5.',9)
   sh.para(x+6,238,112,'La orientación del montaje del modelo DIALux se revisará al integrar el definitivo.',8,col=GREY)
  elif i==1:
   sh.txt(x+6,144,'Ø exterior 166 mm / corte 155 mm',9,True)
   sh.txt(x+6,157,'SECCIÓN ESQUEMÁTICA · FCR',8.5,True,GREY)
   sh.line(x+23,178,x+101,178,GREY,.3,[2,1])
   sh.rect(x+43,168,38,10,None,BLACK,.3)
   sh.line(x+39,179,x+85,179,INK,.65)
   sh.para(x+6,194,112,'Borde fino y difusor central. La sección muestra el cuerpo sobre el falso cielo raso; sirve para reconocer el empotramiento.',9)
   sh.para(x+6,238,112,'Medidas del modelo DN145B de la memoria; la ilustración está ampliada. Fuente S5.',8,col=GREY)
  else:
   sh.txt(x+6,144,'Diámetro del equipo por confirmar',9,True)
   sh.txt(x+6,157,'SECCIÓN ESQUEMÁTICA · LOSA',8.5,True,GREY)
   sh.line(x+23,170,x+101,170,INK,.65)
   sh.rect(x+42,171,40,12,None,BLACK,.3,1)
   sh.para(x+6,194,112,'Cuerpo circular adosado bajo la losa. En planta puede compartir el círculo de familia; el código L-04C identifica la versión de superficie.',9)
   sh.para(x+6,238,112,'Silueta aproximada del tipo descrito en Excel. No se dispone del modelo exacto ni de su diámetro.',8,col=GREY)
 sh.footer('Las secciones son dibujos explicativos de montaje y no detalles constructivos. Fuentes S1, S2, S4 y S5.')

 # 5: conservar la distinción entre forma y simbología normativa.
 sh.header('Dos lecturas para elegir el bloque','A: contorno físico de proyecto · B: símbolo eléctrico base DGE + código del tipo. Ambas opciones se presentan para revisión.')
 sh.txt(21,61,'FAMILIA',10,True)
 sh.txt(123,61,'A / CONTORNO PROPUESTO',10,True)
 sh.txt(234,61,'B / REFERENCIA DGE',10,True)
 sh.txt(333,61,'FIGURA DE REFERENCIA',10,True)
 rows=[('Lineal LED','linear_long','linear','09-93-60','L-01',50),
  ('Panel empotrado','panel','recess','09-93-53','L-03',22),
  ('Aplique de pared','wall','wall','09-93-52','L-02',18),
  ('Downlight empotrado','down_recess','recess','09-93-53','L-04B',16),
  ('Downlight adosado','down_surface','ceiling','09-93-51','L-04C',16)]
 for j,(label,kind,norm,ref,code,size) in enumerate(rows):
  yy=82+j*32
  sh.line(19,yy+20,401,yy+20,EDGE,.2)
  sh.txt(21,yy+2,label,10,True)
  if kind=='wall':
   sh.line(138,yy-5,172,yy-5,INK,.65);sh.rect(144,yy-4,22,5,None,BLACK,.3,1)
  else:sh.physical(kind,155,yy,size)
  sh.txt(185,yy+2,code,9)
  sh.norm(norm,261,yy,1.4)
  sh.txt(278,yy+2,code,9)
  sh.txt(333,yy+2,ref,10,True,BLUE)
 sh.para(21,250,377,'A expresa la forma aproximada del equipo y facilita revisar su distribución. B expresa la salida o luminaria mediante la figura DGE indicada. Un panel y un downlight empotrados comparten la base 09-93-53; el código identifica el tipo. El código DALI/IP corresponde al proyecto.',9)
 sh.footer('Los contornos A no se presentan como símbolos normativos. Las figuras B se basan en la copia DGE consultada de la biblioteca. Fuente S7.')

 # 6: lectura a escalas reales de impresión.
 sh.header('Prueba de lectura al imprimir','Mismo ambiente de ejemplo y paneles de 0,60 m. Etiquetas de 2,5 mm impresos en las tres escalas.')
 for j,den in enumerate([50,75,100]):
  x=16+j*132
  sh.txt(x+5,63,f'ESCALA 1:{den}',15,True,BLUE)
  rw=5600/den;rh=3700/den;xx=x+(124-rw)/2;yy=81
  sh.rect(xx,yy,rw,rh,None,BLACK,.25)
  for cx,cy,code in [(1400,1100,'L-03'),(4200,1100,'L-03-D'),(1400,2600,'L-03-IP65'),(4200,2600,'L-03-DA')]:
   px=xx+cx/den;py=yy+cy/den
   # Borde físico de 15 mm ilustrativo para la prueba; no es un dato de catálogo.
   side=600/den;sh.rect(px-side/2,py-side/2,side,side,None,BLACK,.25)
   sh.rect(px-side/2+.3,py-side/2+.3,side-.6,side-.6,None,GREY,.12)
   sh.txt(px-side/2,py+side/2+3.5,code,2.5*mm)
  sh.txt(x+5,172,f'Panel en papel: {f(600/den)} × {f(600/den)} mm',9)
  sh.para(x+5,180,115,'La geometría física reduce su tamaño con la escala. La etiqueta mantiene el tamaño de impresión.',8.5,col=GREY)
 sh.line(21,207,399,207,EDGE)
 sh.txt(21,221,'DOWNLIGHT REAL A 1:100',10,True)
 sh.circle(100,235,.83,None,BLACK,.25)
 sh.txt(107,237,'Ø 166 mm = 1,66 mm en papel',9)
 sh.txt(230,221,'SÍMBOLO BASE PARA LECTURA',10,True)
 sh.norm('recess',252,235,1)
 sh.txt(263,237,'Salida empotrada + L-04B',9)
 sh.para(21,251,377,'Recomendación para revisar la distribución: contornos simples con código. Para los equipos pequeños, usar el símbolo eléctrico a tamaño legible en la presentación del plano. Las dimensiones físicas quedarían como datos del tipo y detalle de equipo.',9)
 sh.footer('La prueba respeta las escalas indicadas al imprimir el PDF al 100 % en A3. El ambiente mostrado es un ejemplo, no el plano del proyecto.')

 # 7: referencias y decisión concreta.
 sh.header('Referencias y criterio para continuar','La propuesta usa 12 códigos existentes del Excel. Las formas todavía pueden ajustarse antes de construir los bloques.')
 for i,(key,title,note,url) in enumerate(SOURCES):
  yy=57+i*23
  sh.txt(19,yy+3,key,10,True,BLUE)
  sh.txt(32,yy+3,title,10,True)
  sh.para(32,yy+6,363,note,8.5,col=GREY)
  if url:
   # Enlace sobre el título, sin URL larga que entorpezca la lámina.
   c.linkURL(url,(32*mm,(H-yy-4)*mm,398*mm,(H-yy+4)*mm),relative=0,thickness=0)
 sh.line(19,222,401,222,EDGE)
 sh.txt(21,234,'PARA TU REVISIÓN',12,True,BLUE)
 sh.para(21,239,370,'Puedes aprobar la forma por familia o indicar cambios: lineales, paneles, aplique y downlights. También puedes elegir la lectura A o B de la lámina 5. Con esa decisión se crearán los 12 bloques con códigos y datos editables dentro de la plantilla integrada.',10)
 sh.footer('Referencias web de fabricante consultadas el 17/10/2026. Dibujos vectoriales originales de propuesta, sin fotografías de producto.')
 c.save()
 pd=fitz.open(path);assert len(pd)==7
 for i,p in enumerate(pd):
  assert abs(p.rect.width-420*mm)<.1 and abs(p.rect.height-297*mm)<.1
  assert len(p.get_text())>300
  p.get_pixmap(dpi=100,alpha=False).save(out/f'PROPUESTA_LUMINARIAS_LAMINA_{i+1:02d}.png')
 content='\n'.join(p.get_text() for p in pd)
 for s in specs:assert s['code'] in content
 (out/'PROPUESTA_LUMINARIAS_REFERENCIAS.json').write_text(json.dumps({'revision':'A','tipos':specs,'fuentes':SOURCES,'bloques_creados':False,'planos_modificados':False},ensure_ascii=False,indent=2))
 print(json.dumps({'pdf':str(path),'paginas':len(pd),'tipos':len(specs),'cantidad_referencial':sum(s['qty'] for s in specs),'dxf_modificados':0},ensure_ascii=False))


if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit(__doc__)
 main(*sys.argv[1:])
