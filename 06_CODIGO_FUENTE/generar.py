"""Construye una biblioteca CAD integrada reproducible a partir de catalogo.py.

Uso: python 06_CODIGO_FUENTE/generar.py [--sin-pdf]
DXF AutoCAD 2010, modelo en metros, símbolos unitless dimensionados en mm de papel.
"""
from pathlib import Path
from collections import Counter
from dataclasses import asdict
from zipfile import ZipFile, ZIP_DEFLATED
from math import radians
import argparse
import csv
import io
import json
import shutil
import textwrap
import struct
import zlib
import ezdxf
from ezdxf import colors
from ezdxf.addons import Importer, acadctb
from catalogo import catalogo, rutas, CAPAS
from geometria import crear_bloque

ROOT=Path(__file__).resolve().parents[1]
S=.05                       # metros por mm de papel a escala 1:50
W,H=420,297
VERSION='2.0-DGE'
FAMILIAS={
 '01_ILUMINACION_CONTROLES': ('01','ILUMINACION Y CONTROLES','IE | Electricidad',34),
 '02_TOMACORRIENTES_FUERZA': ('02','TOMACORRIENTES Y FUERZA','IE | Electricidad',34),
 '03_CAJAS_TABLEROS_CIRCUITOS': ('03','CAJAS, TABLEROS Y CIRCUITOS','IE | Electricidad',34),
 '04_DATA_COMUNICACIONES': ('04','DATA Y COMUNICACIONES','IC | Comunicaciones',144),
 '05_DETECCION_ALARMA': ('05','DETECCION Y ALARMA','DACI | Incendios',14),
 '08_BASE_DGE': ('08','BASE NORMATIVA DGE','DGE | Instalaciones en edificaciones',34),
}


def ls(value):
    return '"'+str(value).replace('\\','\\\\').replace('"','\\"').replace('\n',' ')+'"'


def nuevo():
    d=ezdxf.new('R2010',units=6)
    for key,val in {'$INSUNITS':6,'$MEASUREMENT':1,'$LUNITS':2,'$LUPREC':3,
                    '$LTSCALE':1.,'$PSLTSCALE':0,'$TEXTSIZE':.125,
                    '$DIMTXT':.125,'$AUNITS':0,'$AUPREC':0,'$LWDISPLAY':False}.items():
        d.header[key]=val
    d.styles.new('EI_TEXTO',dxfattribs={'font':'arial.ttf','height':0})
    palette={1:14,2:34,3:94,4:144,5:174,6:214}
    for name,(color,weight) in CAPAS.items():
        d.layers.new(name,dxfattribs={'color':palette.get(color,color),'lineweight':weight,'plot':0 if name=='VIEWPORTS' else 1})
    return d


def tipos_linea(doc):
    for unit,fac in [('METROS',1),('MILIMETROS',1000)]:
        lines=[';; ELECTRICAS integrada. Crear estilo EI_TEXTO con Arial, altura fija 0.',
               ';; Convenciones internas. Material, diametro y circuito no sustituyen el calculo.',
               ';; R=0: texto relativo. Para tramos invertidos use EIROTULA o invierta la polilinea.',
               f';; Unidades: {unit}. Referencia 1:50; escala de entidad = escala de impresion / 50.']
        for r in rutas():
            text=r['texto']
            # Hueco conservador en función de la longitud del texto. No contiene SHX externos.
            gap=max(.85,len(text.replace('%%c','D'))*.085+.18)
            definition=(f'A,{.5*fac:g},{-.12*fac:g},["{text}",EI_TEXTO,S={.125*fac:g},'
                        f'R=0.0,X=0.0,Y={-.0625*fac:g}],{-gap*fac:g},{.5*fac:g}')
            lines.extend([f'*{r["nombre"]},{text}',definition])
            if fac==1:
                doc.linetypes.new(r['nombre'],dxfattribs={'description':text,'pattern':definition,
                                                        'length':1.12+gap})
        (ROOT/'03_TIPOS_LINEA'/f'EIC_{unit}.lin').write_text('\n'.join(lines)+'\n',encoding='ascii')


def texto(space, string, x,y,h=2.5,color=7,origin=(0,0),layer='EIC-CATALOGO'):
    ox,oy=origin
    return space.add_text(string,dxfattribs={'insert':((ox+x)*S,(oy+y)*S),
        'height':h*S,'style':'EI_TEXTO','layer':layer,'color':color})


def linea(space, a,b,origin=(0,0),color=8,weight=13):
    ox,oy=origin
    return space.add_line(((ox+a[0])*S,(oy+a[1])*S),((ox+b[0])*S,(oy+b[1])*S),
                         dxfattribs={'layer':'EIC-MARCO','color':color,'lineweight':weight})


def marco(doc, origin, number,title,subtitle,color=144):
    m=doc.modelspace()
    ox,oy=origin
    pts=[((ox+x)*S,(oy+y)*S) for x,y in [(8,8),(412,8),(412,289),(8,289)]]
    m.add_lwpolyline(pts,close=True,dxfattribs={'layer':'EIC-MARCO'})
    texto(m,'ELECTRICAS / BIBLIOTECA INTEGRADA',15,278,3.0,color,origin)
    texto(m,title,15,266,6.0,7,origin)
    texto(m,subtitle+'  |  BLOQUES EDITABLES  |  MODELO EN METROS',15,256,2.7,7,origin)
    linea(m,(15,250),(405,250),origin,color,35)
    texto(m,number,382,266,8.0,color,origin)
    linea(m,(15,24),(405,24),origin)
    texto(m,'Referencia por bloque en leyenda. El simbolo no representa dimensiones fisicas del equipo.',15,17,2.5,7,origin)
    texto(m,'1:50 | A3 | v'+VERSION+' | '+number,320,12,2.5,7,origin)
    texto(m,'EI: insertar | EIESCALA | EIEDITA | EIGIRA | EINUMERA | EIRUTA',15,12,2.5,7,origin)


def layout_sheet(doc,name,origin):
    layout=doc.layouts.new(name)
    layout.page_setup(size=(W,H),margins=(0,0,0,0),units='mm')
    layout.dxf_layout.dxf.plot_configuration_file='DWG To PDF.pc3'
    layout.dxf_layout.dxf.current_style_sheet='ELECTRICAS_MONO.ctb'
    layout.add_viewport(center=(W/2,H/2),size=(W,H),
                        view_center_point=((origin[0]+W/2)*S,(origin[1]+H/2)*S),
                        view_height=H*S,status=2,dxfattribs={'layer':'VIEWPORTS','flags':16384})
    for vp in layout.query('VIEWPORT'):vp.dxf.layer='VIEWPORTS'
    return layout


def hoja_simbolos(doc,specs,origin,familia,sufijo=''):
    number,title,subtitle,color=FAMILIAS[familia]
    if sufijo:number+='.'+sufijo
    marco(doc,origin,number,title,subtitle,color)
    m=doc.modelspace()
    cols=4;cellw=97.5;cellh=40
    for i,spec in enumerate(specs):
        col=i%cols;row=i//cols
        x=15+col*cellw;y=238-(row+1)*cellh
        for j,s in enumerate(textwrap.wrap(spec.descripcion,width=43)[:2]):
            texto(m,s,x+3,y+cellh-6-j*3.6,2.6,7,origin)
        bx,by=x+12,y+16
        ins=m.add_blockref(spec.nombre,((origin[0]+bx)*S,(origin[1]+by)*S),
                           dxfattribs={'layer':spec.capa,'xscale':S,'yscale':S,'zscale':S})
        ins.add_auto_attribs(spec.atributos())
        for attr in ins.attribs:attr.dxf.color=256
        pending=not spec.datos.get('PAGINA_DGE') and not spec.forma.startswith('caja')
        texto(m,spec.nombre+(' [P]' if pending else ''),x+3,y+3,2.2,8,origin)
        linea(m,(x,y),(x+cellw-3,y),origin)
        if col>0:linea(m,(x-1,y+3),(x-1,y+cellh-2),origin)
    if any(not s.datos.get('PAGINA_DGE') and not s.forma.startswith('caja') for s in specs):
        texto(m,'[P]: referencia grafica especifica pendiente; no se declara simbolo DGE.',18,32,2.5,7,origin)
    if familia=='01_ILUMINACION_CONTROLES':
        texto(m,'L-01 a L-04 definidos por el prompt. Otros 9 modelos pendientes del registro original.',18,39,2.5,7,origin)
    elif familia=='02_TOMACORRIENTES_FUERZA':
        texto(m,'DGE 09-93-17: T = tierra. E = estabilizado (leyenda del proyecto). 3 rayas = trifasico.',18,39,2.5,7,origin)
    elif familia=='03_CAJAS_TABLEROS_CIRCUITOS':
        texto(m,'Cajas rectangulares con codigo interior. Dimensiones y materiales: definir en el proyecto.',18,39,2.5,7,origin)
    elif familia=='04_DATA_COMUNICACIONES':
        texto(m,'D2 = 2 conectores RJ45 Cat 6A. Equipo, cable, montaje y separaciones: segun proyecto.',18,27,2.5,7,origin)
    elif familia=='05_DETECCION_ALARMA':
        texto(m,'SLC: deteccion / direccionamiento. NAC: notificacion. Sin redes hidraulicas contra incendios.',18,39,2.5,7,origin)
    elif familia=='08_BASE_DGE':
        texto(m,'DGE seccion 9: figuras cotejadas con las paginas 78-84. La reticula auxiliar no es parte del simbolo.',18,27,2.5,7,origin)
    return layout_sheet(doc,number.replace('.','_')+'_'+familia[3:],origin)


def hoja_rutas(doc,items,origin,number,title):
    marco(doc,origin,number,title,'CANALIZACIONES | MATERIAL / SISTEMA / CIRCUITO',144)
    m=doc.modelspace()
    for i,r in enumerate(items):
        x=18+(i//12)*196;y=236-(i%12)*17
        texto(m,r['texto'].replace('%%c','Ø'),x,y,2.8,7,origin)
        # Es una polilinea con tipo de linea complejo real, no un dibujo de su apariencia.
        m.add_lwpolyline([((origin[0]+x)*S,(origin[1]+y-6)*S),
                          ((origin[0]+x+170)*S,(origin[1]+y-6)*S)],
                         dxfattribs={'layer':r['capa'],'linetype':r['nombre'],'flags':128})
    texto(m,'MODO / MONTAJE: EMP, ADO, SUSP, PISO, PARED, TECHO, SUBT. Rotule con EIROTULA.',18,32,2.5,7,origin)
    texto(m,'Los diametros son opciones de biblioteca; no constituyen dimensionamiento de circuitos.',18,27,2.5,7,origin)
    return layout_sheet(doc,number+'_CANALIZACIONES',origin)


def exportar_familias(master,specs):
    destinos={
        'IE': ROOT/'02_BIBLIOTECA_BLOQUES'/'BIBLIOTECA_ELECTRICIDAD.dxf',
        'IC': ROOT/'09_DATA_COMUNICACIONES'/'BIBLIOTECA_COMUNICACIONES.dxf',
        'DACI': ROOT/'10_ALARMA_CONTRAINCENDIOS'/'BIBLIOTECA_DACI.dxf'}
    for system,dest in destinos.items():
        d=nuevo();subset=[s for s in specs if s.sistema==system]
        imp=Importer(master,d)
        imp.import_blocks([s.nombre for s in subset]);imp.finalize()
        families=list(dict.fromkeys(s.familia for s in subset))
        index=0
        for f in families:
            group=[s for s in subset if s.familia==f]
            for offset in range(0,len(group),20):
                hoja_simbolos(d,group[offset:offset+20],(index*450,-800),f,str(offset//20+1) if len(group)>20 else '')
                index+=1
        d.set_modelspace_vport(height=H*S,center=(W*S/2,(-800+H/2)*S))
        d.saveas(dest)


def guardar_datos(specs):
    config={'version':VERSION,'unidades_modelo':'m','geometria_bloque':'mm en papel; unidades de bloque=0',
            'factor_insercion_m':'escala / 1000','factor_insercion_mm':'escala',
            'bloques':[asdict(s) for s in specs],'rutas':rutas(),
            'luminarias_pendientes':9,'bloques_dinamicos_nativos':False,
            'estado_normativo':'Cotejo DGE por simbolo; referencias no comprobadas identificadas por separado'}
    (ROOT/'06_CODIGO_FUENTE'/'catalogo_generado.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
    with (ROOT/'05_CATALOGOS'/'CATALOGO_BLOQUES.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f,delimiter=';')
        writer.writerow(['BLOQUE','CLAVE_INSERCION','TIPO','DESCRIPCION','SISTEMA','CAPA','MONTAJE','ORIGEN','REFERENCIA','PAGINA_DGE','CONTROL'])
        for s in specs:writer.writerow([s.nombre,s.sistema+':'+s.codigo,s.codigo,s.descripcion,s.sistema,s.capa,s.montaje,s.fuente,s.atributos()['NORMA'],s.datos.get('PAGINA_DGE',''),s.datos.get('CONTROL','')])
    entries=[]
    for s in specs:
        attrs=' '.join('('+ls(k)+' . '+ls(v)+')' for k,v in s.atributos().items())
        entries.append('  ('+' '.join(ls(v) for v in [s.nombre,s.codigo,s.descripcion,s.sistema,s.familia,s.capa])+' ('+attrs+'))')
    data=';;; Generado desde catalogo.py. No editar manualmente.\n(setq EI:catalogo \'(\n'+'\n'.join(entries)+'\n))\n'
    data+='(setq EI:rutas \'(\n'
    for r in rutas():data+='  ('+' '.join(ls(r[k]) for k in ('nombre','texto','capa','sistema'))+')\n'
    data+='))\n(princ)\n'
    (ROOT/'04_AUTOLISP'/'EI_CATALOGO.lsp').write_text(data,encoding='utf-8')
    (ROOT/'04_AUTOLISP'/'INICIAR.scr').write_text('(load "ELECTRICAS.lsp")\n(c:EICONFIG)\n(c:EIAYUDA)\n',encoding='ascii')
    (ROOT/'06_CODIGO_FUENTE'/'requirements.txt').write_text('ezdxf=='+ezdxf.__version__+'\nPyMuPDF>=1.24,<2\nreportlab>=4,<5\n',encoding='ascii')


def ctb():
    table=acadctb.new_ctb()
    for i in range(1,256):
        table[i].color=(0,0,0)
        table[i].screen=100
    dest=ROOT/'03_TIPOS_LINEA'/'ELECTRICAS_MONO.ctb'
    # El escritor de ezdxf usa unsigned long nativo (8 bytes en Linux).
    # CTB requiere tres enteros little-endian de 32 bits, tambien en Linux.
    body=io.StringIO();table.write_content(body)
    payload=(body.getvalue()+'\0').encode('utf-8')
    compressed=zlib.compress(payload)
    dest.write_bytes(b'PIAFILEVERSION_2.0,CTBVER1,compress\r\npmzlibcodec'+
        struct.pack('<III',zlib.adler32(compressed),len(payload),len(compressed))+compressed)
    loaded=acadctb.load(dest)
    assert loaded[1].color==(0,0,0)


def pdf_catalogo(doc):
    from ezdxf.addons.drawing import RenderContext, Frontend, pymupdf, layout, config
    import fitz
    from vista_linetipos import vista_pdf
    doc=vista_pdf(doc)
    config_color=config.Configuration(background_policy=config.BackgroundPolicy.WHITE,
                                       min_lineweight=.08)
    config_mono=config.Configuration(background_policy=config.BackgroundPolicy.WHITE,
                                      color_policy=config.ColorPolicy.BLACK,min_lineweight=.08)
    for name, conf in [('CATALOGO_INTEGRADO',config_color),('CATALOGO_MONOCROMO',config_mono)]:
        merged=fitz.open()
        for sheet in doc.layouts:
            if sheet.name in ('Model','Layout1'):continue
            backend=pymupdf.PyMuPdfBackend()
            ctx=RenderContext(doc)
            Frontend(ctx,backend,config=conf).draw_layout(sheet,finalize=True)
            page=layout.Page(W,H,layout.Units.mm)
            data=backend.get_pdf_bytes(page,settings=layout.Settings(fit_page=False,scale=1))
            part=fitz.open(stream=data,filetype='pdf')
            # El backend redondea las dimensiones a puntos enteros; conservar A3 exacto.
            for p in part:p.set_mediabox(fitz.Rect(0,0,W/25.4*72,H/25.4*72))
            merged.insert_pdf(part)
            part.close()
        merged.set_metadata({'title':name.replace('_',' '),'author':'ELECTRICAS',
                             'subject':'Renderizado de los layouts del DXF integrado. No es un ploteo de AutoCAD.'})
        dest=ROOT/'05_CATALOGOS'/(name+'.pdf')
        merged.save(dest,garbage=4,deflate=True)
        if name=='CATALOGO_INTEGRADO':
            merged[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(ROOT/'05_CATALOGOS'/'VISTA_ILUMINACION.png')
            merged[3].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(ROOT/'05_CATALOGOS'/'VISTA_COMUNICACIONES.png')
        merged.close()


def documentos(specs):
    counts=Counter(s.sistema for s in specs)
    inventory={
        'repositorio':'ELECTRICAS','archivos_iniciales_repositorio':['README.md'],
        'referencias_disponibles':['PLANTILLA_IE.zip','Prompt maestro (texto)','Ampliacion (texto)'],
        'referencias_no_disponibles':['SIMBOLOGÍA DE TOMACORRIENTES.DXF','REGISTRO_LUMINARIAS_SIETE_NIVELES.md'],
        'AutoCAD':'no instalado','ODAFileConverter':'no instalado',
        'luminarias_documentadas':['L-01','L-02','L-03','L-04'],
        'luminarias_restantes':'9 pendientes, no se crean modelos ficticios',
        'bibliotecas_nuevas':dict(counts),'bloques_dinamicos_nativos':'no generados'}
    (ROOT/'07_PRUEBAS'/'INVENTARIO_REFERENCIAS.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
    guide=f'''# ELECTRICAS — biblioteca integrada v{VERSION}

## Inicio rapido

1. Descomprima todo el paquete en una carpeta local. Abra **PLANTILLA_GENERAL_INTEGRADA.dxf** en AutoCAD.
2. Guarde una copia como DWG de su proyecto mediante GUARDAR COMO. Conserve el original de biblioteca.
3. APPLOAD → ELECTRICAS.lsp. Si AutoCAD lo solicita, autorice esta carpeta de confianza tras revisar las rutinas.
4. Escriba **EICONFIG**, luego **EIESCALA**: 50, 75 o 100. Escriba **EI** para abrir el panel y colocar un simbolo.
5. Mantenga juntos el LSP, EI_CATALOGO.lsp, DCL y LIN. Si guarda el proyecto en otra carpeta, el cargador permite localizar el catalogo una vez.

## Un solo archivo de trabajo

    La plantilla principal contiene electricidad ({counts['IE']} bloques), comunicaciones ({counts['IC']}) y DACI ({counts['DACI']}).
Los nueve layouts A3 son paginas de catalogo dentro del mismo archivo. No necesita cambiar de plantilla.
Las bibliotecas por especialidad son archivos de respaldo para reutilizacion independiente.
El catalogo esta en Modelo, debajo del area de trabajo (Y entre -40 y -25.15 m). Trabaje con la arquitectura cerca de 0,0.
EICATALOGO muestra la primera hoja. Los layouts 01 a 07 permiten consultar el resto.
La base JY_ original queda archivada como referencia; las definiciones anteriores no se insertan en la biblioteca corregida.

## Comandos

| Comando | Funcion |
|---|---|
| EI / EIPANEL | Seleccionar una familia y colocar un bloque |
| EIINSERTA | Insertar por nombre o clave (ejemplo IC:D2, DACI:DH1, IE:L-03) |
| EIESCALA | Escala de impresion para proximas inserciones |
| EICONFIG | Configurar variables de tipos de linea en AutoCAD |
| EIEDITA | Consultar y editar atributos |
| EIGIRA / EIALINEA | Girar / alinear manteniendo etiquetas horizontales |
| EIREORDENAR | Recuperar etiquetas despues de usar ROTATE nativo |
| EITIPO | Cambiar variante; conserva codigo y datos comunes del proyecto |
| EINUMERA | Numerar segun orden de seleccion evitando codigos ya utilizados |
| EICIRCUITO | Asignar circuito o lazo a una seleccion |
| EISELECCIONA | Seleccionar dispositivos por sistema |
| EIRUTA | Trazar una polilinea con tipo de linea textual real |
| EIROTULA | Colocar texto legible siguiendo la direccion elegida |
| EICARGALIN | Cargar tipos de linea compatibles con unidades m o mm |
| EICATALOGO | Mostrar la biblioteca en Modelo |
| EIAYUDA | Ayuda breve en linea de comandos |

Los comandos trabajan en el plano XY de Modelo. No admiten UCS inclinado en 3D.
AutoLISP no se ha ejecutado en AutoCAD: las comprobaciones disponibles son estaticas.
Los cambios hechos por entmake/entmod se pueden revertir con DESHACER; las operaciones compuestas pueden requerir varios pasos.

## Unidades y escalas — evitar errores de factor 1000

La plantilla principal usa **metros (INSUNITS=6)**. Los bloques nuevos son simbolicos, sin unidades, definidos en mm de papel.

| Impresion | Factor de bloque en modelo m | Factor en modelo mm | Texto de 2.5 mm en modelo m |
|---|---:|---:|---:|
| 1:50 | 0.05 | 50 | 0.125 m |
| 1:75 | 0.075 | 75 | 0.1875 m |
| 1:100 | 0.10 | 100 | 0.250 m |

EIESCALA no modifica bloques existentes. COPY y MOVE conservan los atributos. Use EIGIRA para orientar sin desordenar las etiquetas.
Los simbolos no representan el tamano fisico del equipo. DIM_FISICA, DIMENSIONES y POTENCIA son datos independientes.
L-03 tiene dimension nominal 600x600 mm; su contorno sigue siendo simbolico y no sirve para medir el falso cielo raso.
Para convertir un archivo generado de metros a milimetros use el script **convertir_unidades.py**; no cambie solo INSUNITS.
El script transforma Modelo, atributos, vistas y patrones de linea; mantiene las hojas en mm de papel.
Las rutinas JY_ heredadas corresponden a la base en metros. En el archivo convertido use ELECTRICAS.lsp.

## Canalizaciones y circuitos

Se incluyen EMT/PVC/CORR/FMC en diametros nominales 16, 20, 25, 32, 40 y 50 mm, y rutas especificas IC/DACI.
Estos diametros son opciones editables de biblioteca; no son un calculo de capacidad ni una prescripcion.
Use etiquetas EMP (empotrada), ADO (adosada), SUSP, PISO, PARED, TECHO o SUBT segun el proyecto.
No se asigna automaticamente piso/techo a lineas continuas o discontinuas.
Las capas separan especialidad y funcion. Para montajes distintos sobre la misma ruta rotule el montaje.
EICONFIG establece LTSCALE=1, MSLTSCALE=0, PSLTSCALE=0. Para 1:75 use escala de entidad de linea 1.5; para 1:100, 2.
EIRUTA hace ese ajuste en las rutas nuevas. Cargue EIC_METROS.lin para m y EIC_MILIMETROS.lin para mm.
Los tipos complejos usan Arial por medio de EI_TEXTO. En tramos invertidos el texto relativo puede quedar invertido: invierta el tramo o use EIROTULA.
EIROTULA orienta y desplaza el texto; la ubicacion se elige de forma asistida. Revise interferencias en el plano real.
SLC y NAC se distinguen por texto, capa y color. Material, cable y arquitectura deben corresponder al equipo seleccionado.
Las distancias de separacion de energia/data se verifican en cada proyecto; la biblioteca no las calcula.

## Simbologia y alcance

La revision 2.0 coteja los simbolos electricos con las laminas DGE, seccion 9. El CSV y los atributos NORMA/PAGINA_DGE documentan cada referencia. Los dispositivos sin referencia especifica comprobada siguen identificados como convenciones pendientes, especialmente IC/DACI y sensores.
Los tomacorrientes usan el simbolo monofasico con T de 09-93-17. Las tres rayas de 09-93-15 significan trifasico, no 2P+T.
Se retira el rombo de estabilizado y la tierra exterior. E identifica estabilizado en la leyenda, PA se basa en 09-93-19, y el marco de piso en 09-93-14. Techo/mesada se indican con atributos, sin inventar distintivos geometricos.
S con a/b/c corresponde al interruptor unipolar y los grupos controlados; dos o tres teclas independientes no se presentan como bipolar S2. S2, S3 y S4 normativos tienen bloques separados en la base DGE.
Las variantes con letra S permanecen derechas al usar los comandos de esta biblioteca; no necesitan orientar la letra con el muro.
Las cajas tienen contorno rectangular y codigo interior. Sus dimensiones, material e IP se dejan editables para definicion de proyecto.
Solo L-01 a L-04 estan descritas en los textos. Los otros 9 modelos requieren el registro original y no se inventan.
Potencias, alturas no documentadas, corrientes, modelos DACI y direcciones se dejan vacios para evitar datos ficticios.
DACI comprende deteccion, alarma y notificacion; no incluye redes hidraulicas.

## Impresion y comprobaciones pendientes

Instale ELECTRICAS_MONO.ctb mediante STYLESMANAGER y seleccione el dispositivo y papel A3 disponibles en su AutoCAD.
Los layouts usan CTB monocromo y espesores por capa. Las ventanas graficas estan en VIEWPORTS, que no imprime.
El PDF de catalogo se renderiza a partir de los layouts del DXF con ezdxf/PyMuPDF; no acredita un ploteo de AutoCAD.
Los textos de LIN se interpretan desde sus tags DXF en una copia en memoria para la vista PDF; el archivo CAD mantiene los tipos complejos originales. Los ajustes de extremo se comprueban en AutoCAD.
Las diferencias de fuentes, tipos de linea complejos y configuracion de impresora requieren comprobacion en AutoCAD.
No se incluyen DWG/DWT ni bloques dinamicos nativos sin producirlos y probarlos realmente.
Para crear DWT: abra el DXF, configure su impresora y estilos, compruebe las inserciones y use GUARDAR COMO > DWT.

## Regeneracion

En el repositorio o dentro de FUENTES del ZIP:

    python -m pip install -r 06_CODIGO_FUENTE/requirements.txt
    python 06_CODIGO_FUENTE/corregir_base.py
    python 06_CODIGO_FUENTE/generar.py
    python 06_CODIGO_FUENTE/verificar.py
    python 06_CODIGO_FUENTE/empaquetar.py

Los informes en 07_PRUEBAS distinguen pruebas ejecutadas y pendientes. Para regenerar la base se conserva el ZIP original en referencias.
'''
    (ROOT/'05_CATALOGOS'/'GUIA_DE_USO.md').write_text(guide,encoding='utf-8')
    (ROOT/'README.md').write_text('# ELECTRICAS\n\nUna sola biblioteca integrada de electricidad, comunicaciones y DACI.\n\n'
        'Revision 2.0-DGE: interruptores y tomacorrientes corregidos, 36 simbolos DGE adicionales y referencia por figura.\n\n'
        'Archivo principal: `11_PLANTILLA_GENERAL_INTEGRADA/PLANTILLA_GENERAL_INTEGRADA.dxf`.\n\n'
        'Entrega simplificada: `08_ENTREGA_FINAL/ELECTRICAS_INTEGRADA.zip`.\n\n'
        'Uso y limitaciones: [GUIA_DE_USO.md](05_CATALOGOS/GUIA_DE_USO.md).\n\n'
        'Regeneracion: `python 06_CODIGO_FUENTE/generar.py`, `python 06_CODIGO_FUENTE/verificar.py`.\n',encoding='utf-8')
    normas='''# Referencias tecnicas y estado de comprobacion

Se consulto la ficha oficial MINEM de la R.M. 091-2002-EM/VME y una copia de la seccion 9 del documento DGE. La copia de consulta procede de un espejo publico, no de un enlace oficial descargado. Las figuras de paginas 76 y 78-84 se cotejaron visualmente; esto no certifica todo el expediente.

Ficha oficial: https://www.gob.pe/institucion/minem/normas-legales/108773-0091-2002-mem

Copia consultada: https://github.com/gaelrenzo/instalacion-electricas/blob/3619a7f06e64488628182d915e9d85e87d1515a5/referencias/normativa/pdf/simbologia-dge-seccion-9.pdf

| Documento solicitado | Aplicacion a verificar | Estado |
|---|---|---|
| CNE Utilizacion / MINEM | Criterios electricos y simbolos aplicables | Fuente original no disponible |
| DGE seccion 9 | Simbolos de edificaciones indicados en CSV | Figuras cotejadas en copia de consulta y ficha oficial de aprobacion |
| RNE EM.010 | Instalaciones electricas interiores | Fuente original no disponible |
| IEC (simbolos aplicables) | Correspondencia grafica cuando proceda | Edicion y simbolo especifico pendientes |
| ANSI/TIA-568, 569, 606, 607 | Cableado, canalizaciones, administracion y puesta a tierra | Edicion y especificacion de proyecto pendientes |
| RNE A.130 | Deteccion, alarma y seguridad | Fuente original no disponible |
| NFPA 72 | Arquitectura y dispositivos DACI cuando sea exigible | Edicion aplicable y fichas de fabricante pendientes |

NORMA identifica la figura DGE cotejada o la referencia que aun falta. PAGINA_DGE permite ir a la lamina. El CSV distingue simbolo base y datos de proyecto. La base normativa adicional contiene interruptores S/S2/S3/S4, tomas monofasicas/trifasicas, luminarias y dispositivos que faltaban en la primera entrega.
La norma presenta 09-93-08/09 como circulos. Las cajas rectangulares solicitadas se mantienen como contornos fisicos, sin atribuirles esos codigos; los simbolos generales DGE se ofrecen por separado en el mismo archivo.

Esta entrega es una herramienta de representacion CAD. No calcula cargas, protecciones, secciones, cobertura de detectores, inteligibilidad, autonomia ni distancias normativas. Esas decisiones pertenecen al diseno del expediente.
'''
    (ROOT/'05_CATALOGOS'/'REFERENCIAS_Y_CONVENCIONES.md').write_text(normas,encoding='utf-8')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sin-pdf',action='store_true');args=parser.parse_args()
    for folder in ('01_PLANTILLA_MAESTRA','02_BIBLIOTECA_BLOQUES','03_TIPOS_LINEA','04_AUTOLISP',
                   '05_CATALOGOS','06_CODIGO_FUENTE','07_PRUEBAS','08_ENTREGA_FINAL',
                   '09_DATA_COMUNICACIONES','10_ALARMA_CONTRAINCENDIOS','11_PLANTILLA_GENERAL_INTEGRADA'):
        (ROOT/folder).mkdir(parents=True,exist_ok=True)
    specs=catalogo()
    assert len({s.nombre for s in specs})==len(specs)
    doc=nuevo();tipos_linea(doc)
    for spec in specs:crear_bloque(doc,spec)
    # La base anterior se conserva en referencias, no entre los simbolos activos corregidos.
    for i,f in enumerate(k for k in FAMILIAS if k!='08_BASE_DGE'):
        hoja_simbolos(doc,[s for s in specs if s.familia==f],(450*i,-800),f)
    rr=rutas()
    hoja_rutas(doc,rr[:24],(450*5,-800),'06','CANALIZACIONES ELECTRICAS')
    hoja_rutas(doc,rr[24:],(450*6,-800),'07','RUTAS DE COMUNICACIONES Y DACI')
    group=[s for s in specs if s.familia=='08_BASE_DGE']
    for offset in range(0,len(group),20):
        hoja_simbolos(doc,group[offset:offset+20],(450*(7+offset//20),-800),'08_BASE_DGE',str(offset//20+1))
    if 'Layout1' in doc.layouts:doc.layouts.delete('Layout1')
    doc.set_modelspace_vport(height=H*S,center=(W*S/2,(-800+H/2)*S))
    principal=ROOT/'11_PLANTILLA_GENERAL_INTEGRADA'/'PLANTILLA_GENERAL_INTEGRADA.dxf'
    doc.saveas(principal)
    # Volver a leer es obligatorio: la documentacion grafica procede del archivo guardado.
    saved=ezdxf.readfile(principal)
    exportar_familias(saved,specs)
    guardar_datos(specs);documentos(specs);ctb()
    if not args.sin_pdf:pdf_catalogo(saved)
    print(json.dumps({'principal':str(principal),'bloques_nuevos':len(specs),
                      'por_sistema':dict(Counter(s.sistema for s in specs)),
                      'rutas':len(rr),'layouts':len(saved.layouts)-1},ensure_ascii=False))


if __name__=='__main__':main()
