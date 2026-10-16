"""Vista vectorial de LIN textuales para el renderizador PDF de ezdxf.

El frontend no dibuja textos de tipos complejos. Esta función interpreta sus tags
en una copia en memoria para las muestras rectas; el DXF entregado no se modifica.
No reproduce los ajustes de extremo y sustituciones de fuentes de AutoCAD.
"""
import io
from math import atan2,cos,sin,degrees,hypot
import ezdxf


def vista_pdf(original):
    stream=io.StringIO();original.write(stream)
    doc=ezdxf.read(io.StringIO(stream.getvalue()))
    model=doc.modelspace()
    for entity in list(model.query('LWPOLYLINE')):
        name=entity.dxf.get('linetype','Continuous')
        if not name.startswith('EIC_'):continue
        points=list(entity.get_points('xy'))
        if len(points)!=2:continue
        lt=doc.linetypes.get(name)
        parts=[]
        for tag in lt.pattern_tags.tags:
            if tag.code==49:parts.append({'length':tag.value})
            elif parts and tag.code in (9,340,46,50,44,45):parts[-1][tag.code]=tag.value
        if not any(9 in p for p in parts):continue
        a,b=points;theta=atan2(b[1]-a[1],b[0]-a[0])
        length=hypot(b[0]-a[0],b[1]-a[1])
        factor=entity.dxf.get('ltscale',1)*doc.header.get('$LTSCALE',1)
        def point(distance,x=0,y=0):
            return (a[0]+(distance+x)*cos(theta)-y*sin(theta),
                    a[1]+(distance+x)*sin(theta)+y*cos(theta))
        props={'layer':entity.dxf.layer,'color':entity.dxf.get('color',256),'linetype':'Continuous'}
        pos=0
        while pos<length-1e-9:
            for part in parts:
                step=abs(part['length'])*factor
                if part['length']>0 and pos<length:
                    model.add_line(point(pos),point(min(pos+step,length)),dxfattribs=props)
                pos+=step
                if 9 in part and pos<length:
                    height=part.get(46,.125)*factor
                    # No dibujar una etiqueta cortada al final de la muestra.
                    approximate_width=len(part[9].replace('%%c','D'))*height*.75
                    if pos+approximate_width<length:
                        font=doc.entitydb[part[340]].dxf.name
                        model.add_text(part[9],dxfattribs={**props,'style':font,'height':height,
                            'insert':point(pos,part.get(44,0)*factor,part.get(45,0)*factor),
                            'rotation':degrees(theta+part.get(50,0))})
                if pos>=length:break
        model.delete_entity(entity)
    return doc
