# Semisótano: distribución propuesta, revisión 01

Abra SEMISOTANO_DISTRIBUCION_SIN_RECORRIDOS.dxf. Contiene arquitectura y 23 puntos dobles en un solo archivo, en metros. La hoja SS_DISTRIBUCION_A1 muestra la propuesta a 1:100. El PDF y PNG son vistas de esa hoja. No se agregaron recorridos, cajas de paso, conductores ni trazos de circuitos.

Rojo: 9 puntos T-01 a +0.40 m NPT. Azul: 14 puntos T-02 estancos a +1.10 m NPT. La numeración 01 a 23 corresponde a PUNTOS_PROPUESTOS.csv. Cada inserción conserva tipo, altura, tablero, circuito, ambiente y fila del Excel como atributos editables. Los circuitos se guardan como datos y no están trazados.

Las coordenadas son una propuesta manual sobre el plano; el Excel no contiene coordenadas del semisótano. Se interpretaron por geometría los sectores vehiculares central/lateral, que no tienen rótulos equivalentes en el DXF. Se requiere revisión de ubicación, especialmente respecto a zonas de maniobra y equipos.

La arquitectura conserva sus entidades, coordenadas y atributos DXF. El archivo original hacía referencia a los tipos de línea ausentes `dash` y `trazo pequeño`; se agregaron patrones provisionales, no recuperados del archivo original. El fondo gris se aplica solo a la visualización PDF/PNG. Ninguna vista valida demanda, protecciones o alimentación de bombas. La propuesta cubre únicamente los tomacorrientes de servicio del cuadro.

La simbología usa la base DGE cotejada de la biblioteca: 09-93-17 y distintivo PA según 09-93-19. T-01/T-02 y la numeración son identificadores de proyecto; cada símbolo es un punto doble, no dos símbolos independientes.

Generación: `python 06_CODIGO_FUENTE/distribuir_semisotano.py arquitectura.dxf cuadro.xlsx carpeta_salida` (desde el repositorio). Dependencias: ezdxf, openpyxl, PyMuPDF. No se ha abierto en AutoCAD en este entorno.
