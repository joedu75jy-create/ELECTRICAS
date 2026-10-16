# ELECTRICAS — biblioteca integrada v2.0-DGE

## Inicio rapido

1. Descomprima todo el paquete en una carpeta local. Abra **PLANTILLA_GENERAL_INTEGRADA.dxf** en AutoCAD.
2. Guarde una copia como DWG de su proyecto mediante GUARDAR COMO. Conserve el original de biblioteca.
3. APPLOAD → ELECTRICAS.lsp. Si AutoCAD lo solicita, autorice esta carpeta de confianza tras revisar las rutinas.
4. Escriba **EICONFIG**, luego **EIESCALA**: 50, 75 o 100. Escriba **EI** para abrir el panel y colocar un simbolo.
5. Mantenga juntos el LSP, EI_CATALOGO.lsp, DCL y LIN. Si guarda el proyecto en otra carpeta, el cargador permite localizar el catalogo una vez.

## Un solo archivo de trabajo

    La plantilla principal contiene electricidad (80 bloques), comunicaciones (19) y DACI (16).
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
