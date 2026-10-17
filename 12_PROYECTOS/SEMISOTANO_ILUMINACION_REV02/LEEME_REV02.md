# Propuesta por paños del estacionamiento — REV 02

Abra SEMISOTANO_LUMINARIAS_PROPUESTA_REV02.dxf: un único modelo en metros con la base y 162 luminarias. Se replantean solo las 69 L-01-15 del estacionamiento vehicular y circulación (1.035 W). Las otras 93 conservan su ubicación anterior y no quedan validadas por esta revisión. Sin recorridos ni códigos exteriores.

El PDF tiene tres páginas: comparación antes/después con las franjas marcadas; detalle de la propuesta a 1:100; plano integrado general a 1:100. El archivo comparativo individual contiene solo la primera página. Azul: estacionamiento revisado; gris: otros puntos. Naranja: caras de franjas contrastadas; rojo en el antes: superposición gráfica.

Se contrastaron 44 franjas de 0,40 m dibujadas como pares de líneas en A-DETL y las proyecciones de ductos registradas en PROYECCIONES_DUCTOS.json. Se identificaron 22 símbolos superpuestos a las franjas en el estacionamiento anterior. La propuesta no superpone su contorno gráfico con esas franjas ni con las proyecciones de ductos contrastadas. No es un certificado de ausencia de interferencias físicas: los símbolos conservan dimensiones gráficas de la propuesta aprobada; faltan dimensiones reales de equipos, estructuras, peraltes y coordinación completa de instalaciones.

La distribución conserva por franja longitudinal 5, 18, 18, 14 y 14 unidades. Se centran las columnas dentro de los anchos libres entre caras de columnas; las filas se reparten dentro de los intervalos libres. La fila norte se separa del ducto y alinea sus seis luminarias a Y=35,45 m. En el paño oriental central se reparten seis puntos en Y=18,05, 20,00 y 21,95 m para evitar los dos bancos de ductos proyectados. Los IDs originales se mantienen mediante asignación de mínimo desplazamiento al nuevo conjunto de puntos por franja. La tabla de cambios registra cada XY anterior y propuesto.

Montaje previsto: adosado a losa, pendiente de verificar por sección. Los 3,89 m de DIALux se guardan solo en ALTURA_REF_DIALUX_M. ALTURA_M queda PENDIENTE para estas 69 unidades. Las nuevas coordenadas se identifican como propuesta, no como coordenadas del cálculo anterior. Z=0 se conserva porque es una representación en planta.

La altura libre, las sombras y los niveles de lux/uniformidad requieren recálculo en DIALux con vigas y demás obstáculos modelados. No se ha hecho ese recálculo ni se heredan sus resultados anteriores. La cantidad de 69 se conserva para comparación, su suficiencia no está confirmada. La identificación estructural de las franjas y sus peraltes debe confirmarse con estructuras.

Los bloques y la arquitectura se conservan. La única intervención en el modelo son las 69 referencias y sus atributos. Auditoría DXF sin errores ni correcciones; guardado y reapertura comprobados. No se dispone de AutoCAD en este entorno. Fuentes OpenSans incluidas.
