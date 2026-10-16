"""Geometrías vectoriales simbólicas. Unidades de bloque: mm en papel, sin unidades CAD."""
from math import sin, cos, pi


class Icono:
    def __init__(self, block):
        self.b = block
        self.props = {'layer':'0','color':0,'lineweight':-2}

    def line(self, a, b):
        self.b.add_line(a, b, dxfattribs=self.props)

    def poly(self, pts, closed=False):
        return self.b.add_lwpolyline(pts, close=closed, dxfattribs=self.props)

    def rect(self, x, y, w, h):
        return self.poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)], True)

    def circle(self, x=0, y=0, r=3):
        self.b.add_circle((x,y), r, dxfattribs=self.props)

    def arc(self, x, y, r, start, end):
        self.b.add_arc((x,y), r, start, end, dxfattribs=self.props)

    def text(self, value, x=0, y=-1.1, h=2.5):
        from ezdxf.enums import TextEntityAlignment
        self.b.add_text(value,dxfattribs={**self.props,'height':h,'style':'EI_TEXTO'}).set_placement(
            (x,y),align=TextEntityAlignment.CENTER)

    def star(self, x=0, y=0, r=3.3, count=8):
        for i in range(count):
            a=2*pi*i/count
            self.line((x+1.2*cos(a),y+1.2*sin(a)),(x+r*cos(a),y+r*sin(a)))

    def arrow(self, a, b):
        from math import atan2
        self.line(a,b)
        t=atan2(b[1]-a[1],b[0]-a[0])
        self.poly([(b[0]-1.5*cos(t-.45),b[1]-1.5*sin(t-.45)), b,
                   (b[0]-1.5*cos(t+.45),b[1]-1.5*sin(t+.45))])

    def earth(self, y=-2):
        self.line((0,y),(0,y-1.4))
        for width,dy in ((1.8,1.4),(1.2,2.2),(.6,3)):
            self.line((-width,y-dy),(width,y-dy))


def dibujar(block, shape):
    g=Icono(block)
    if shape.startswith('toma_'):
        stable=shape.endswith('_est')
        kind=shape.removeprefix('toma_').removesuffix('_est')
        g.circle(r=2)
        for y in (-.65,.65):g.line((-3.3,y),(1.6,y))
        g.earth()
        if stable:g.poly([(0,3.7),(3.7,0),(0,-3.7),(-3.7,0)],True)
        if kind in ('piso','dedicado'):g.rect(-3,-3,6,6)
        if kind=='pared':g.line((-4,-2),(-4,2))
        if kind=='mesada':g.line((-4,3),(4,3))
        if kind=='techo':g.poly([(-2.2,3),(0,5),(2.2,3)])
        if kind=='estanco':g.circle(r=3.2)
        if kind=='dedicado':g.line((-3,3),(3,-3))
    elif shape=='luz_lineal':
        g.rect(-7,-1.8,14,3.6)
        g.line((-5.8,0),(5.8,0))
        for x in (-5.8,5.8):g.line((x,-1.8),(x,1.8))
    elif shape=='luz_aplique':
        g.circle(r=3)
        g.line((-4,-3.8),(4,-3.8))
        g.line((-2,-2),(2,2));g.line((-2,2),(2,-2))
    elif shape=='luz_panel':
        g.rect(-4,-4,8,8);g.rect(-3.3,-3.3,6.6,6.6)
        g.line((-3.3,-3.3),(3.3,3.3));g.line((-3.3,3.3),(3.3,-3.3))
    elif shape=='luz_downlight':
        g.circle(r=3);g.circle(r=2.1)
        g.line((-1.3,0),(1.3,0));g.line((0,-1.3),(0,1.3))
    elif shape.startswith('control_'):
        g.circle(r=1.4)
        if shape[-1:] in ('1','2','3'):
            for i in range(int(shape[-1])):g.line((.8,1),(3+i*1.1,4))
        elif shape=='control_conmuta':
            g.poly([(-3,4),(0,1.4),(3,4)]);g.circle(-3,4,.4);g.circle(3,4,.4)
        else:
            g.poly([(-3,4),(3,-3)]);g.poly([(-3,-3),(3,4)])
    elif shape in ('pulsador','pulsador_salida','estacion'):
        g.rect(-3,-3,6,6)
        if shape=='pulsador':g.circle(r=1.6);g.line((-3,4),(3,4))
        elif shape=='pulsador_salida':g.arrow((-2,0),(2,0))
        else:g.rect(-2.3,-2.3,4.6,4.6);g.text('M')
    elif shape=='sensor_movimiento':
        g.circle(r=2)
        for radius in (3.2,4.4):g.arc(0,0,radius,25,155)
        g.text('M',h=2.5)
    elif shape=='sensor_presencia':
        g.circle(r=3.6);g.circle(r=2.8);g.text('P')
    elif shape=='regulador':
        g.circle(r=3);g.arrow((-3.5,-3.5),(3.5,3.5))
    elif shape in ('caja','caja_rect'):
        w=10 if shape=='caja_rect' else 8
        g.rect(-w/2,-4,w,8);g.rect(-w/2+.5,-3.5,w-1,7)
    elif shape.startswith('tablero_'):
        g.rect(-4,-5,8,10);g.rect(-3.2,-4.2,6.4,8.4)
        code={'tablero_general':'TG','tablero_distribucion':'TD','tablero_ups':'UPS'}[shape]
        g.text(code)
    elif shape in ('fuerza','mecanica'):
        g.circle(r=3.3)
        g.text('F' if shape=='fuerza' else 'M')
        if shape=='fuerza':g.poly([(-2,-3.5),(0,-5),(2,-3.5)])
        else:g.rect(-4,-4,8,8)
    elif shape in ('sube','baja','sube_baja'):
        g.circle(-3,-2,.65)
        if shape in ('sube','sube_baja'):g.arrow((-2.5,-1.5),(3.5,4.5))
        if shape in ('baja','sube_baja'):g.arrow((2.5,3.5),(-3.5,-2.5))
    elif shape=='tierra':g.earth(3)
    elif shape=='circuito':g.circle(r=3.5);g.line((-5.5,0),(-3.5,0))
    elif shape in ('data_1','data_2','voz_data'):
        count=1 if shape=='data_1' else 2
        for i in range(count):
            x=-3 if count==1 else -5+i*5.2
            g.rect(x,-2.5,4.2,5);g.rect(x+1,-2.5,2.2,1.1)
            for j in range(3):g.line((x+1+j*.7,1.2),(x+1+j*.7,2.2))
        if shape=='voz_data':g.line((-5,-3.6),(-.8,-3.6))
    elif shape=='voz':
        g.rect(-3,-3,6,6)
        g.poly([(-1.8,1.7),(-1.8,-.8),(-.8,-1.8),(1.7,-1.8)])
        g.line((-2.2,1.7),(-.7,1.7));g.line((1.7,-2.2),(1.7,-.7))
    elif shape=='ap':
        g.circle(r=2.5);g.text('AP',h=2.5)
        g.arc(0,0,3.5,30,150);g.arc(0,0,4.6,30,150)
    elif shape=='cam_domo':
        g.arc(0,0,3.2,180,360);g.line((-4,0),(4,0));g.circle(0,-1.4,.65)
        g.line((-4,.8),(4,.8))
    elif shape=='cam_bala':
        g.poly([(-4,-1.7),(2,-1.7),(2,1.7),(-4,1.7)],True)
        g.poly([(2,-1.4),(4,-2.2),(4,2.2),(2,1.4)])
        g.poly([(-1,-1.7),(-1,-3.5),(-4,-3.5)])
    elif shape=='cam_ptz':
        g.circle(r=2)
        for a,b in [((-4,0),(-2.7,0)),((2.7,0),(4,0)),((0,-4),(0,-2.7)),((0,2.7),(0,4))]:g.arrow(a,b)
    elif shape=='acceso':
        g.rect(-3,-4,6,8);g.line((-3,-4),(2,3));g.circle(1.5,0,.35)
    elif shape=='lector':
        g.rect(-2,-3.5,4,7);g.line((-1,1),(1,1))
        g.arc(-1.5,0,4,-45,45);g.arc(-1.5,0,5,-45,45)
    elif shape=='cerradura':
        g.rect(-4,-1.2,8,2.4);g.rect(-3.2,1.8,6.4,1.2)
        for x in (-2,0,2):g.line((x,-1.2),(x,1.2))
    elif shape in ('rack','gabinete'):
        g.rect(-4,-5,8,10);g.rect(-3,-4,6,8)
        if shape=='rack':
            for y in (-2.7,-.9,.9,2.7):
                g.line((-3,y),(3,y));g.circle(-2.3,y+.4,.15)
        else:
            for y in (-2,-1,0,1,2):g.line((-1.8,y),(1.8,y))
            g.circle(2.3,0,.25)
    elif shape in ('patch','switch'):
        g.rect(-6,-2,12,4)
        for i in range(6):g.rect(-4.8+i*1.6,-.6,1,1.2)
        if shape=='switch':g.circle(5,1,.3);g.line((-5,3),(5,3))
        else:g.line((-6,-3),(6,-3))
    elif shape in ('fibra','fibra_interconexion'):
        g.poly([(0,3),(4,0),(0,-3),(-4,0)],True)
        if shape=='fibra':g.arrow((-3,0),(3,0))
        else:
            g.arrow((-3,.8),(3,.8));g.arrow((3,-.8),(-3,-.8))
    elif shape.startswith('detector_'):
        if shape=='detector_ducto':g.rect(-4,-3.5,8,7)
        g.circle(r=3)
        label={'detector_humo':'H','detector_termico':'T','detector_multi':'MC','detector_ducto':'H'}[shape]
        g.text(label)
        if shape=='detector_multi':g.circle(r=3.7)
    elif shape in ('sirena','sirena_estrobo'):
        g.poly([(-3,-1.5),(-1,-1.5),(2,-3),(2,3),(-1,1.5),(-3,1.5)],True)
        g.arc(0,0,4.3,-40,40)
        if shape=='sirena_estrobo':g.star(-1,5,2.1,6)
    elif shape=='estrobo':g.rect(-2,-2,4,4);g.star(r=4.5)
    elif shape in ('facp','repetidor'):
        g.rect(-5,-4,10,8);g.rect(-3.7,.1,7.4,2.7)
        for x in (-3,-1,1,3):g.circle(x,-1.8,.45)
        if shape=='facp':g.line((-5,4.8),(5,4.8))
    elif shape.startswith('modulo_'):
        g.rect(-3.7,-3.7,7.4,7.4)
        g.text({'modulo_monitoreo':'MM','modulo_control':'MC','modulo_aislador':'AI'}[shape])
        g.line((-5,0),(-3.7,0));g.line((3.7,0),(5,0))
    elif shape=='fuente':
        g.rect(-3.5,-3.5,7,7);g.line((-2,1),(0,1));g.line((-1,0),(-1,2));g.line((1,-1),(3,-1))
    elif shape=='interfaz':
        g.poly([(0,4),(4,0),(0,-4),(-4,0)],True);g.text('IF')
        g.line((-6,0),(-4,0));g.line((4,0),(6,0))
    else:
        raise ValueError('Geometria sin implementar: '+shape)


def crear_bloque(doc, spec):
    block=doc.blocks.new(spec.nombre, base_point=(0,0,0))
    block.block_record.dxf.units=0
    dibujar(block,spec.forma)
    for tag,value in spec.atributos().items():
        visible=tag in ('CODIGO','CIRCUITO','ALTURA')
        pos={'CODIGO':(10,.5),'CIRCUITO':(10,-3),'ALTURA':(10,-6.5)}.get(tag,(0,0))
        width=1.0
        if tag=='CODIGO' and spec.forma.startswith('caja'):
            pos=(-3.1,-1.1)
            width=min(1.0,6.2/max(1,len(value)*1.6))
        block.add_attdef(tag,insert=pos,text=value,height=2.5,
            dxfattribs={'layer':'0','color':0,'style':'EI_TEXTO','flags':0 if visible else 1,'width':width})
    return block
