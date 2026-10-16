"""Conversión física m <-> mm del DXF generado, sin redefinir los bloques simbólicos.

python convertir_unidades.py entrada.dxf salida.dxf --unidad mm
Mantiene papel, grosores y geometrías unitless de los bloques; escala sus referencias.
"""
from pathlib import Path
import argparse
import ezdxf
from ezdxf.math import Matrix44
from ezdxf.lldxf.types import DXFTag


def convertir(entrada, salida, unidad='mm'):
    entrada=Path(entrada);salida=Path(salida)
    if entrada.resolve()==salida.resolve():raise ValueError('Use un archivo de salida distinto.')
    doc=ezdxf.readfile(entrada)
    actual=doc.header.get('$INSUNITS',0);destino={'m':6,'mm':4}[unidad]
    if actual not in (4,6):raise ValueError('Solo se admiten origenes en metros o milimetros.')
    if actual==destino:raise ValueError('El archivo ya utiliza la unidad solicitada.')
    factor=1000.0 if actual==6 else .001
    matrix=Matrix44.scale(factor,factor,factor)
    for ent in doc.modelspace():
        ent.transform(matrix)
        if ent.dxftype()=='TEXT':
            ent.dxf.text=ent.dxf.text.replace('MODELO EN METROS','MODELO EN MILIMETROS') if destino==4 else ent.dxf.text.replace('MODELO EN MILIMETROS','MODELO EN METROS')
    for lt in doc.linetypes:
        if lt.pattern_tags:
            lt.pattern_tags.tags[:]=[DXFTag(t.code,t.value*factor) if t.code in (40,49,46,44,45) else t
                                    for t in lt.pattern_tags.tags]
    for layout in doc.layouts:
        if layout.name=='Model':continue
        for vp in layout.query('VIEWPORT'):
            if vp.dxf.id==1:continue
            vp.dxf.view_center_point=tuple(v*factor for v in vp.dxf.view_center_point)
            vp.dxf.view_height*=factor
            vp.dxf.view_target_point=tuple(v*factor for v in vp.dxf.view_target_point)
    for vp in doc.viewports:
        if vp.dxf.hasattr('center'):vp.dxf.center=tuple(v*factor for v in vp.dxf.center)
        vp.dxf.height*=factor
    for name in ('$TEXTSIZE','$DIMTXT','$DIMASZ','$DIMGAP'):
        if name in doc.header:doc.header[name]*=factor
    doc.header['$INSBASE']=tuple(v*factor for v in doc.header.get('$INSBASE',(0,0,0)))
    doc.header['$INSUNITS']=destino
    doc.saveas(salida)
    check=ezdxf.readfile(salida).audit()
    if check.errors or check.fixes:raise RuntimeError('La conversion no paso la auditoria DXF.')
    return factor


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('entrada');parser.add_argument('salida')
    parser.add_argument('--unidad',choices=('m','mm'),default='mm')
    args=parser.parse_args()
    if Path(args.salida).exists():parser.error('El archivo de salida ya existe; use otro nombre.')
    print('Factor aplicado:',convertir(args.entrada,args.salida,args.unidad))
