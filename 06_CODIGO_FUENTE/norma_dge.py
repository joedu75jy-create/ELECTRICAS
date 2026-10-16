"""Símbolos cotejados visualmente con DGE, sección 9, páginas impresas 76 y 78–84.

El PDF de consulta es una copia del documento MINEM recuperada de un espejo;
la resolución aprobatoria se verificó en la ficha oficial de gob.pe.
No convierte dos teclas independientes en un interruptor bipolar.
"""
from math import pi,cos,sin

OFICIAL='https://www.gob.pe/institucion/minem/normas-legales/108773-0091-2002-mem'
ESPEJO='https://github.com/gaelrenzo/instalacion-electricas/blob/3619a7f06e64488628182d915e9d85e87d1515a5/referencias/normativa/pdf/simbologia-dge-seccion-9.pdf'


def aplicar(items,add):
    def setref(s,shape,codes,pag,nota='Simbolo base cotejado visualmente con la lamina DGE'):
        s.forma=shape
        s.fuente=f'DGE seccion 9, p. {pag}; {codes}. {nota}'
        s.datos.update(NORMA='DGE RM 091-2002-EM/VME; '+codes,PAGINA_DGE=str(pag),
                       CLASE_REFERENCIA='BASE DGE + DATOS DE PROYECTO',OBSERVACIONES=nota)
    for s in items:
        if s.nombre.startswith(('IE_TN_','IE_TE_')):
            floor=s.montaje=='PISO';water='EST110' in s.nombre
            code='09-93-17'+(' + 09-93-14' if floor else '')+(' + 09-93-19' if water else '')
            suffix='T'+('/PA' if water else '')+('/E' if s.nombre.startswith('IE_TE_') else '')
            setref(s,'dge_toma_piso' if floor else 'dge_toma',code,79,
                   'T: tierra; PA: prueba de agua; E: alimentacion estabilizada, identificador de proyecto en leyenda. Sin rombo ni tierra exterior.')
            s.datos.update(DISTINTIVO=suffix,NUM_TOMAS='2',CONFIGURACION='2P+T',
                           NOTA_MONTAJE=s.montaje if s.montaje in ('TECHO','MESADA') else '')
        elif s.nombre in ('IE_SIMPLE','IE_DOBLE','IE_TRIPLE'):
            count={'IE_SIMPLE':1,'IE_DOBLE':2,'IE_TRIPLE':3}[s.nombre]
            s.codigo={1:'S_a',2:'S_ab',3:'S_abc'}[count]
            setref(s,'dge_S','09-93-30 (variante S)',80,
                   'S: interruptor unipolar. a/b/c: grupos controlados del proyecto. Dos o tres teclas independientes no equivalen a bipolar S2.')
            s.datos.update(CONTROL={1:'a',2:'a,b',3:'a,b,c'}[count],TECLAS=str(count))
        elif s.nombre=='IE_CONMUTACION':
            s.codigo='S3';setref(s,'dge_S3','09-93-32',81);s.datos['CONTROL']='a'
        elif s.nombre=='IE_CRUCE':
            s.codigo='S4';setref(s,'dge_S4','09-93-33',81);s.datos['CONTROL']='a'
        elif s.nombre=='IE_PULSADOR':setref(s,'dge_43','09-93-43',82)
        elif s.nombre=='IE_REGULADOR':setref(s,'dge_37','09-93-37',81)
        elif s.nombre=='IE_L01':setref(s,'dge_60','09-93-60',83,'Simbolo general de luminaria; LED/IP65 se especifica por codigo y atributos, sin llamarlo fluorescente.')
        elif s.nombre=='IE_L02':setref(s,'dge_52','09-93-52',82,'Salida en pared; LED/IP65 por ficha de tipo L-02.')
        elif s.nombre in ('IE_L03','IE_L04'):
            setref(s,'dge_53','09-93-53',82,'Salida empotrada en techo; codigo L-03/L-04 identifica panel o downlight, no su huella fisica.')
        elif s.nombre.startswith('IE_CAJA_'):
            s.datos['NORMA']='CONTORNO FISICO RECTANGULAR; distinto del simbolo general DGE 09-93-08'
            s.fuente='Contorno fisico solicitado por el usuario. Ver simbolos DGE 09-93-08 y 09-93-09 en catalogo normativo.'
        elif s.nombre in ('IE_TABLERO_GENERAL','IE_TABLERO_DISTRIBUCION'):setref(s,'dge_panel','09-91-16',76)
        elif s.nombre in ('IE_SUBE','IE_BAJA','IE_SUBE_BAJA'):
            num={'IE_SUBE':'05','IE_BAJA':'06','IE_SUBE_BAJA':'07'}[s.nombre]
            setref(s,'dge_'+num,'09-93-'+num,78)
        elif s.nombre in ('IE_FUERZA','IE_MECANICA'):setref(s,'dge_12','09-93-12',78,'Salida de potencia general. Fases y equipo se identifican por atributos; no se inventa una configuracion.')
        elif s.nombre in ('IC_DATA_SIMPLE','IC_DATA_DOBLE','IC_VOZ','IC_VOZ_DATA','IC_FO_SALIDA','IC_FO_INTERCONEXION'):
            setref(s,'dge_27','09-93-27',80,'Base general de telecomunicaciones. D/2D/VD/FO/FI son designaciones del proyecto; TP figura en DGE.')
            s.datos['DISTINTIVO']={'IC_DATA_SIMPLE':'D','IC_DATA_DOBLE':'2D','IC_VOZ':'TP','IC_VOZ_DATA':'VD',
                                    'IC_FO_SALIDA':'FO','IC_FO_INTERCONEXION':'FI'}[s.nombre]
        elif s.nombre=='IC_CERRADURA':setref(s,'dge_72','09-93-72',84,'Cerradura electrica general; tipo electromagnetico en atributos.')
    extras=[
        ('08','Caja, simbolo general','dge_08',78),('09','Caja de conexion / derivacion','dge_09',78),
        ('12','Salida de potencia, simbolo general','dge_12',78),
        ('13','Tomacorriente monofasico','dge_toma',79),('14','Tomacorriente monofasico en piso','dge_toma_piso',79),
        ('15','Tomacorriente trifasico','dge_toma_3f',79),('16','Tomacorriente trifasico en piso','dge_toma_3f_piso',79),
        ('17','Tomacorriente monofasico puesto a tierra','dge_toma',79),
        ('19','Tomacorriente a prueba de agua','dge_toma',79),
        ('27','Salida de telecomunicaciones, general','dge_27',80),
        ('28','Interruptor, simbolo general','dge_28',80),('29','Interruptor con lampara piloto','dge_SL',80),
        ('30','Interruptor unipolar, variante S','dge_S',80),('31','Interruptor bipolar, variante S2','dge_S2',81),
        ('32','Interruptor de tres vias','dge_S3',81),('33','Interruptor de cuatro vias','dge_S4',81),
        ('35','Interruptor unipolar de dos vias','dge_35',81),('36','Conmutador intermedio','dge_36',81),
        ('37','Interruptor graduador','dge_37',81),('38','Interruptor con tirador','dge_ST',81),
        ('39','Interruptor de puerta','dge_SP',81),('42','Pulsador / contactor no de senalizacion','dge_SC',82),
        ('43','Boton de presion','dge_43',82),('44','Boton con lampara indicadora','dge_44',82),
        ('51','Salida de luz adosada en techo','dge_51',82),('52','Salida de luz adosada en pared','dge_52',82),
        ('53','Salida de luz empotrada en techo','dge_53',82),('54','Salida de luz empotrada en pared','dge_54',83),
        ('55','Salida fluorescente en techo','dge_55',83),('56','Salida fluorescente empotrada','dge_56',83),
        ('59','Lampara, simbolo general','dge_59',83),('60','Luminaria, simbolo general','dge_60',83),
        ('61','Luminaria de tres tubos fluorescentes','dge_61',83),
        ('67','Luminaria de emergencia','dge_67',84),('68','Luminaria autonoma de emergencia','dge_68',84),
        ('72','Cerradura electrica','dge_72',84),
    ]
    for num,desc,shape,pag in extras:
        code='09-93-'+num
        add('IE_DGE_'+num,code,desc,'IE','08_BASE_DGE','IE-LEYENDA',shape,
            NORMA='DGE RM 091-2002-EM/VME; '+code,PAGINA_DGE=str(pag),
            CLASE_REFERENCIA='SIMBOLO DGE COTEJADO',DISTINTIVO={'17':'T','19':'PA'}.get(num,''))
        items[-1].fuente=f'DGE seccion 9, pagina impresa {pag}, {code}. Figura cotejada; sin puntos de la reticula auxiliar.'
    for s in items:
        if s.forma.startswith('dge_S'):s.datos['GIRO_GRAFICO']='FIJO_LEGIBLE'
    return items


def dibujar(g,shape):
    if not shape.startswith('dge_'):return False
    def dot(x,y,r=.3):
        pts=[(x+r*cos(i*pi/8),y+r*sin(i*pi/8)) for i in range(16)]
        hatch=g.b.add_hatch(color=0,dxfattribs={'layer':'0'})
        hatch.paths.add_polyline_path(pts,is_closed=True)
    def light(fill=False,wall=False):
        if fill:dot(0,0,2)
        else:g.circle(r=2)
        for a,b in [((-3.5,0),(-2,0)),((2,0),(3.5,0)),((0,-3.5),(0,-2)),((0,2),(0,3.5))]:g.line(a,b)
        if wall:g.line((-4,-2),(-4,2));g.line((-4,0),(-3.5,0))
    if shape.startswith('dge_toma'):
        floor='piso' in shape;three='3f' in shape
        g.circle(r=2)
        for y in ((-.65,0,.65) if three else (-.45,.45)):g.line((-3.4,y),(1.95,y))
        if floor:g.rect(-2.6,-2.6,5.2,5.2)
    elif shape in ('dge_S','dge_S2','dge_S3','dge_S4','dge_SL','dge_ST','dge_SP','dge_SC'):
        dot(-2,-1.2)
        g.text('S',x=.3,y=-1.2,h=3.5)
        suffix=shape.removeprefix('dge_S')
        if suffix:g.text(suffix,x=2.7,y=-2.3,h=2.5)
    elif shape=='dge_28':g.circle(r=1.8);g.line((.9,1.55),(3.7,6.3))
    elif shape=='dge_35':
        g.circle(r=1.8);g.poly([(.9,1.55),(3.7,6.3),(5,5.5)]);g.poly([(-.9,-1.55),(-3.7,-6.3),(-5,-5.5)])
    elif shape=='dge_36':
        g.circle(r=1.8)
        for x,y in ((1,1),(-1,1),(-1,-1),(1,-1)):
            g.poly([(x*1.2,y*1.2),(x*3.7,y*5.5),(x*5,y*4.7)])
    elif shape=='dge_37':
        g.circle(r=1.8);g.line((.9,1.55),(3.7,6.3));g.poly([(1.4,3.8),(4.4,3.8),(4.4,5.8)],True)
    elif shape in ('dge_43','dge_44'):
        g.circle(r=2.6);g.circle(r=1.4)
        if shape=='dge_44':g.line((-1,-1),(1,1));g.line((-1,1),(1,-1))
    elif shape in ('dge_51','dge_52','dge_53','dge_54'):light(shape in ('dge_53','dge_54'),shape in ('dge_52','dge_54'))
    elif shape in ('dge_55','dge_56'):
        g.rect(-6,-2.4,12,4.8)
        if shape=='dge_55':g.circle(r=1.4)
        else:dot(0,0,1.4)
    elif shape=='dge_59':g.circle(r=2.4);g.line((-1.7,-1.7),(1.7,1.7));g.line((-1.7,1.7),(1.7,-1.7))
    elif shape in ('dge_60','dge_61'):
        g.line((-6,-1),(-6,1));g.line((6,-1),(6,1))
        for y in ((0,) if shape=='dge_60' else (-1.5,0,1.5)):g.line((-6,y),(6,y))
        if shape=='dge_61':g.line((-6,-2),(-6,2));g.line((6,-2),(6,2))
    elif shape in ('dge_67','dge_68'):
        g.line((-2.6,-2.6),(2.6,2.6));g.line((-2.6,2.6),(2.6,-2.6));dot(0,0,.45)
        if shape=='dge_68':g.rect(-3,-3,6,6)
    elif shape in ('dge_08','dge_09'):
        g.circle(r=2.6)
        if shape=='dge_09':dot(0,0,.4)
    elif shape=='dge_12':g.arc(0,0,2.4,0,180);g.line((0,2.4),(0,6))
    elif shape=='dge_27':g.poly([(-2.6,-2.8),(-2.6,0),(2.6,0),(2.6,-2.8)]);g.poly([(0,0),(0,5),(-5,5)])
    elif shape=='dge_panel':
        g.rect(-5,-3,10,6)
        h=g.b.add_hatch(color=0,dxfattribs={'layer':'0'})
        h.set_pattern_fill('ANSI31',color=0,scale=.4)
        h.paths.add_polyline_path([(-5,-3),(5,-3),(5,3),(-5,3)],is_closed=True)
    elif shape in ('dge_05','dge_06','dge_07'):
        if shape=='dge_05':g.line((-6,-1),(0,-1));g.arrow((0,-1),(4,3));dot(0,-1)
        elif shape=='dge_06':g.line((-6,2),(2,2));g.arrow((2,2),(-2,-2));dot(2,2)
        else:g.arrow((0,0),(3.8,3.8));g.arrow((0,0),(-3.8,-3.8));dot(0,0)
    elif shape=='dge_72':
        g.rect(-5,-1.5,8,4);g.poly([(3,2.5),(7,-1.5),(3,-1.5)])
        g.arc(-2,0,1,0,180);g.arc(0,0,1,0,180)
    else:raise ValueError('Simbolo DGE sin geometria: '+shape)
    return True
