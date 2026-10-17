"""Revisión C del panel L-03: propuesta gráfica sin código exterior.
Uso: python propuesta_l03_sin_rotulo.py carpeta_salida
Genera una lámina PDF y un PNG vectorial renderizado; no modifica planos.
"""
from pathlib import Path
import sys
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT='/usr/share/fonts/truetype/open-sans/'
INK='#203549';BLUE='#187b9f';GREY='#62727e'


class Drawing:
 def __init__(self,c,height):self.c=c;self.h=height
 def text(self,x,y,t,pt=10,color=INK,bold=False):
  self.c.setFillColor(HexColor(color));self.c.setFont('B' if bold else 'R',pt)
  self.c.drawString(x*mm,(self.h-y)*mm,t)
 def line(self,x,y,x2,y2,color,lw):
  self.c.setStrokeColor(HexColor(color));self.c.setLineWidth(lw*mm)
  self.c.line(x*mm,(self.h-y)*mm,x2*mm,(self.h-y2)*mm)
 def panel(self,x,y,s,color='#10161a'):
  # x/y = esquina superior izquierda. Tres trazos con espacio real entre ellos.
  for inset,weight in [(0,.017),(.036,.009),(.085,.012)]:
   self.c.setStrokeColor(HexColor(color));self.c.setLineWidth(max(.075,min(.48,s*weight))*mm)
   self.c.rect((x+s*inset)*mm,(self.h-y-s+s*inset)*mm,s*(1-2*inset)*mm,s*(1-2*inset)*mm,stroke=1,fill=0)
  for endpoint in [.29,.35]:
   self.line(x+s*.085,y+s*endpoint,x+s*endpoint,y+s*.085,color,max(.075,min(.26,s*.011)))
  cx=x+s*.5;cy=y+s*.48;r=s*.115
  self.c.setStrokeColor(HexColor(color));self.c.setLineWidth(max(.075,min(.28,s*.012))*mm)
  self.c.circle(cx*mm,(self.h-cy)*mm,r*mm,stroke=1,fill=0)
  self.line(cx-s*.157,cy,cx+s*.157,cy,color,max(.07,min(.20,s*.009)))
  self.line(cx,cy-s*.157,cx,cy+s*.157,color,max(.07,min(.20,s*.009)))
  # LED se conserva dentro; todo el perímetro exterior queda libre de rótulos.
  size=s*.17*mm
  self.c.setFont('R',size)
  tw=pdfmetrics.stringWidth('LED','R',size)/mm
  self.text(x+s*.86-tw,y+s*.84,'LED',size,color)


def main(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 pdfmetrics.registerFont(TTFont('R',FONT+'OpenSans-Regular.ttf'))
 pdfmetrics.registerFont(TTFont('B',FONT+'OpenSans-Semibold.ttf'))
 # Imagen de un único símbolo: sin título, código ni leyenda alrededor.
 scratch=out/'L03_ICONO_VECTORIAL.pdf'
 c=canvas.Canvas(str(scratch),pagesize=(100*mm,100*mm));d=Drawing(c,100)
 d.panel(12,12,76)
 c.save()
 doc=fitz.open(scratch)
 assert 'L-03' not in doc[0].get_text() and doc[0].get_text().strip()=='LED'
 doc[0].get_pixmap(dpi=180,alpha=False).save(out/'L03_SIN_CODIGO_REV_C.png')
 # Lámina de revisión independiente, sin implementar la biblioteca definitiva.
 pdf=out/'L03_SIN_CODIGO_REV_C.pdf'
 c=canvas.Canvas(str(pdf),pagesize=(297*mm,210*mm));d=Drawing(c,210)
 c.setTitle('Panel LED · Propuesta L-03 sin código exterior · REV C')
 d.text(15,17,'PANEL LED / REVISIÓN DEL DIBUJO',10,BLUE,True)
 d.text(15,31,'El símbolo, sin rótulo exterior',21,INK,True)
 d.text(15,41,'Propuesta para el tipo L-03 · El código se consulta en la leyenda y en los datos del futuro bloque.',9,GREY)
 d.line(15,48,282,48,'#c9d5dd',.2)
 d.panel(34,62,86)
 for yy,title,note in [(70,'MARCO MÁS DEFINIDO','Tres trazos separados y grosores jerarquizados.'),
   (94,'ESQUINA CONSERVADA','Doble diagonal fina como en tu referencia.'),
   (118,'CENTRO MÁS LIGERO','Círculo y ejes proporcionados, con más espacio libre.'),
   (142,'LED INTERIOR','Letra más pequeña y margen uniforme al borde.')]:
  d.text(151,yy,title,10,BLUE,True)
  d.text(151,yy+7,note,8.6,GREY)
 d.line(15,163,282,163,'#c9d5dd',.2)
 d.text(18,173,'PRUEBA DE TAMAÑO IMPRESO',8.5,INK,True)
 for x,s in [(150,8),(200,10),(251,12)]:
  d.panel(x-s/2,170,s)
  d.text(x-5,190,f'{s} mm',8,GREY)
 d.text(18,184,'Ejemplos con el marco y el centro conservados.',8.5,GREY)
 d.text(18,192,'El tamaño final del símbolo se ajusta a la escala del plano.',8.5,GREY)
 d.line(15,199,282,199,'#c9d5dd',.2)
 d.text(15,205,'Propuesta gráfica de proyecto · REV C · No modifica bloques ni distribución.',7.5,GREY)
 c.save()
 check=fitz.open(pdf);assert len(check)==1
 check[0].get_pixmap(dpi=120,alpha=False).save(out/'L03_LAMINA_REV_C.png')
 print({'pdf':str(pdf),'png':str(out/'L03_SIN_CODIGO_REV_C.png'),'paginas':1,'texto_del_simbolo':'LED'})


if __name__=='__main__':main(sys.argv[1])
