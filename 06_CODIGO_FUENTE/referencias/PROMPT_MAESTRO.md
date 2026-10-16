# PROMPT MAESTRO PARA CODEX
## DESARROLLO DE PLANTILLA PROFESIONAL DE INSTALACIONES ELÉCTRICAS EN AUTOCAD

### 1. ROL PROFESIONAL

Actúa como un equipo de especialistas conformado por:

- Ingeniero electricista especialista en instalaciones de edificaciones públicas del Perú.
- Proyectista eléctrico con experiencia en expedientes técnicos.
- Dibujante CAD senior especializado en AutoCAD.
- Especialista en simbología eléctrica y normalización gráfica.
- Programador avanzado en Python, AutoLISP, Visual LISP, DXF, DWG y automatización CAD.
- Especialista en bibliotecas de bloques dinámicos y atributos editables.

**OBJETIVO PRINCIPAL**

Desarrollar una PLANTILLA MAESTRA PROFESIONAL DE INSTALACIONES ELÉCTRICAS, reutilizable en AutoCAD, para el diseño de edificios institucionales, judiciales, administrativos, educativos y comerciales.

La plantilla deberá contener simbología, bloques, tuberías, canalizaciones, tipos de líneas, cajas de paso, luminarias, tomacorrientes, interruptores, circuitos y herramientas de automatización.

**NO QUIERO:**

- Dibujos demostrativos sin utilidad CAD.
- Símbolos improvisados.
- Bloques que únicamente parezcan correctos visualmente.
- Archivos DXF vacíos o con elementos ficticios.
- Imágenes en lugar de objetos CAD.
- Explicaciones extensas sin archivos funcionales.
- Trabajos que requieran redibujar manualmente los elementos.

**QUIERO ARCHIVOS CAD REALES, EDITABLES, ORGANIZADOS Y REUTILIZABLES.**

La calidad gráfica deberá corresponder a la de un proyectista CAD profesional que elabora expedientes técnicos para entidades públicas.

---

### 2. ENTORNO DE TRABAJO Y REPOSITORIO

Trabaja directamente en el repositorio GitHub:

**ELECTRICAS**

Utiliza el entorno en la nube de Codex ya configurado.

Inspecciona primero los archivos disponibles en el repositorio.

Puedes utilizar Python y bibliotecas compatibles con DXF, como `ezdxf`, además de AutoLISP y otros recursos técnicos necesarios.

Debes crear los archivos de código fuente, archivos CAD, bibliotecas y resultados dentro del repositorio.

No te limites a proporcionar instrucciones. Implementa, ejecuta y verifica el código.

Si AutoCAD no está instalado en el entorno, genera los DXF mediante bibliotecas compatibles y prepara los scripts necesarios para completar las operaciones dependientes de AutoCAD.

No afirmes que un archivo DWG o un bloque dinámico nativo está terminado si no puedes generarlo o comprobarlo realmente.

### 3. ARCHIVOS DE REFERENCIA

Trabajar con:

1. **SIMBOLOGÍA DE TOMACORRIENTES.DXF**: referencia para los tomacorrientes, cajas de paso, representación gráfica, tipos de línea y distribución del catálogo.
2. **REGISTRO_LUMINARIAS_SIETE_NIVELES.md**: referencia para identificar las 13 luminarias o variantes solicitadas en el proyecto.
3. Archivos complementarios DWG, DXF, PDF, Excel o imágenes que posteriormente se incorporen al repositorio.

Antes de dibujar, realiza un inventario real de los archivos accesibles.

Si el registro contiene menos de 13 modelos identificables, indícalo y no inventes los restantes.

Si las referencias no están disponibles, desarrolla los componentes técnicamente definidos y mantén identificadas las partes que necesitan documentación adicional.

Nunca afirmes haber revisado archivos que no están disponibles.

---

### 4. SIMBOLOGÍA DE LUMINARIAS

Desarrolla una biblioteca de bloques independientes para las luminarias contenidas en el registro original.

Entre las familias conocidas se encuentran:

- L-01: luminaria LED lineal hermética IP65.
- L-02: aplique circular de pared IP65.
- L-03: panel LED de 60 × 60 cm empotrado en falso cielo raso.
- L-04: downlight LED empotrado.

El resto de modelos y variantes deberá identificarse a partir del registro original.

Para cada luminaria:

- Crear un bloque CAD independiente.
- Establecer punto base de inserción apropiado.
- Incorporar atributo editable de código.
- Permitir rotación y cambio de orientación.
- Definir geometría reconocible en planta.
- Diferenciar montaje empotrado, adosado, suspendido y en pared.
- Organizar por tipo de luminaria.
- Utilizar geometría limpia y proporcionada.
- Preparar una biblioteca reutilizable.

Incorporar atributos editables para código, descripción, potencia, montaje y observaciones cuando corresponda.

No confundir una representación simbólica con las dimensiones físicas del equipo.

Las luminarias deberán poder copiarse, insertarse y utilizarse en planos arquitectónicos sin redibujarlas.

### 5. TOMACORRIENTES

Crear bloques para:

**Tomacorrientes normales**

- Doble 220 V, 2P+T.
- A 0.40 m sobre piso terminado.
- A 1.20 m sobre piso terminado.
- Instalación en pared.
- Instalación en piso.
- Instalación en techo, cuando corresponda.

**Tomacorrientes estabilizados**

- Doble 220 V, 2P+T.
- Diferenciación gráfica respecto del normal.
- Montaje en pared, piso o posición aplicable.

**Tomacorrientes especiales**

- Para equipos de fuerza.
- Para equipos mecánicos.
- Salidas eléctricas dedicadas.
- Otras configuraciones justificadas técnicamente.

**REQUISITO FUNDAMENTAL**

La representación de tomacorrientes debe reconocer claramente las tres líneas correspondientes al símbolo 2P+T, incluyendo la puesta a tierra.

No representar tomacorrientes con símbolos genéricos sin correspondencia técnica.

Utilizar la referencia DXF suministrada como base de normalización y mejora.

Incluir código y altura de montaje mediante atributos editables.

### 6. INTERRUPTORES Y CONTROLES

Crear simbología para:

- Interruptor simple.
- Interruptor doble.
- Interruptor triple.
- Interruptor de conmutación.
- Interruptor de cruce.
- Pulsador.
- Sensor de movimiento.
- Sensor de presencia.
- Control de iluminación.

Todos deberán contar con geometría diferenciable, punto de inserción, orientación configurable y atributos editables.

### 7. CAJAS DE PASO

**Las cajas de paso deberán representarse mediante geometría CUADRADA O RECTANGULAR según su función.**

No utilizar círculos genéricos para cajas de paso.

Crear bloques para:

- Cajas de paso de iluminación.
- Cajas de tomacorrientes.
- Cajas de fuerza.
- Cajas de derivación.
- Cajas en pared.
- Cajas en techo.
- Cajas para canalizaciones especiales.

Las cajas deberán tener un código o identificación visible en su interior.

Por ejemplo, CP-01, CP-02 y otras denominaciones organizadas por función.

Incorporar atributos editables para:

- Código.
- Dimensiones.
- Tipo de montaje.
- Sistema.
- Observaciones.

Diferenciar visualmente la función de la caja sin perjudicar la lectura del plano.

### 8. TUBERÍAS Y CANALIZACIONES

Desarrollar una biblioteca de tipos de líneas profesionales.

Considerar:

- Tubería EMT.
- Tubería PVC.
- Tubería corrugada.
- Tubería empotrada.
- Tubería adosada.
- Canalización suspendida.
- Canalización por piso.
- Canalización por pared.
- Canalización por techo.
- Canalización subterránea, cuando corresponda.

**REQUISITO PRINCIPAL**

Las líneas deberán poder identificar el tipo de canalización y su diámetro directamente en el dibujo.

Ejemplos de nomenclatura:

`EMT Ø25 mm`

`PVC Ø20 mm`

`CORR. Ø25 mm`

Crear archivos LIN personalizados y, cuando resulte técnicamente conveniente, rutinas de rotulación automática.

Las etiquetas deben poder colocarse siguiendo la canalización con orientación legible, sin superposiciones.

No emplear arbitrariamente una línea punteada para representar una instalación por piso o una línea continua para una instalación por techo.

Definir convenciones gráficas mediante una leyenda clara y consistente.

Configurar escalas de tipos de línea apropiadas y documentar su utilización.

### 9. BLOQUES DINÁMICOS

Priorizar bloques dinámicos reales de AutoCAD.

Cuando la implementación nativa sea técnicamente viable, incorporar:

- Parámetros de rotación.
- Parámetros de alineación.
- Estados de visibilidad.
- Puntos de inserción.
- Atributos editables.
- Opciones de orientación.
- Posibilidades de estiramiento cuando tengan sentido técnico.

Las cajas, luminarias, interruptores y tomacorrientes deberán facilitar su cambio de posición y orientación.

**IMPORTANTE:** Un bloque ordinario con atributos no debe presentarse como si fuera un bloque dinámico nativo.

Si el entorno no permite generar directamente las definiciones dinámicas de AutoCAD, preparar los archivos y procedimientos AutoLISP o de AutoCAD necesarios para completarlas, identificando expresamente qué operaciones requieren AutoCAD.

No falsificar características dinámicas.

### 10. CAPAS NORMALIZADAS

Crear una estructura profesional de capas.

Propuesta inicial:

| Capa | Aplicación |
|---|---|
| IE-LUMINARIAS | Luminarias |
| IE-ILUMINACION-CIRCUITOS | Circuitos de iluminación |
| IE-INTERRUPTORES | Interruptores |
| IE-TOMAS-NORMALES | Tomacorrientes normales |
| IE-TOMAS-ESTABILIZADOS | Tomacorrientes estabilizados |
| IE-FUERZA | Salidas de fuerza |
| IE-CAJAS-PASO | Cajas de paso |
| IE-TUBERIA-EMT | Canalizaciones EMT |
| IE-TUBERIA-PVC | Canalizaciones PVC |
| IE-TUBERIA-CORRUGADA | Tuberías corrugadas |
| IE-TABLERO | Tableros |
| IE-TEXTOS | Rotulación |
| IE-CODIGOS | Códigos |
| IE-COTAS | Dimensiones |
| IE-LEYENDA | Leyendas y simbología |

Establecer colores ACI, espesores, tipos de línea y propiedades por capa de forma coherente.

Garantizar adecuada impresión en blanco y negro.

Evitar colores innecesarios o una organización excesivamente complicada.

### 11. NORMALIZACIÓN TÉCNICA

Aplicar criterios gráficos compatibles con la normativa peruana que resulte pertinente, incluyendo:

- Código Nacional de Electricidad – Utilización.
- Reglamento Nacional de Edificaciones, EM.010.
- Simbología oficial MINEM que resulte aplicable.
- Normas IEC de simbología eléctrica cuando corresponda.
- Buenas prácticas internacionales de representación CAD.

No inventar símbolos supuestamente oficiales.

Distinguir la simbología normalizada de las convenciones internas de proyecto.

Si se utiliza un símbolo convencional no recogido expresamente por una norma, identificarlo correctamente en la leyenda.

### 12. ORGANIZACIÓN DE LA PLANTILLA

Crear una lámina maestra de biblioteca CAD.

Distribuir los elementos por familias:

1. Luminarias.
2. Interruptores.
3. Tomacorrientes normales.
4. Tomacorrientes estabilizados.
5. Tomacorrientes especiales.
6. Cajas de paso.
7. Tuberías y canalizaciones.
8. Circuitos.
9. Tableros.
10. Simbología complementaria.

Cada familia deberá estar ordenada, identificada y separada gráficamente.

El catálogo servirá para visualizar los símbolos y copiar o insertar los bloques en proyectos posteriores.

Los elementos no deben ser simples líneas sueltas cuando corresponde utilizar una referencia de bloque.

### 13. CONFIGURACIÓN Y ESCALAS

Configurar las unidades del archivo y comprobar su compatibilidad con planos arquitectónicos.

Preparar los símbolos para escalas usuales de edificación, como 1:50, 1:75 y 1:100.

Considerar que algunos planos arquitectónicos utilizan metros y otros milímetros.

Definir una unidad base explícita y proporcionar un procedimiento seguro de adaptación entre ambos sistemas.

Configurar tamaños de textos, códigos y simbología para asegurar legibilidad en impresión.

Evitar que los símbolos queden exageradamente grandes o pequeños respecto de la arquitectura.

Preparar una configuración de impresión adecuada para planos técnicos.

### 14. HERRAMIENTAS DE AUTOMATIZACIÓN

Crear herramientas AutoLISP y, cuando corresponda, Python para:

- Insertar símbolos mediante código.
- Seleccionar familias de elementos.
- Cambiar orientación.
- Editar atributos.
- Insertar cajas de paso.
- Dibujar canalizaciones.
- Rotular diámetros de tuberías.
- Identificar circuitos.
- Cambiar estados o variantes de bloques.
- Cargar automáticamente capas y tipos de línea.
- Construir o reconstruir la plantilla maestra.

Los scripts deben ser reutilizables y comprensibles.

Documentar los comandos necesarios para utilizarlos desde AutoCAD.

### 15. ENTREGABLES OBLIGATORIOS

Generar dentro del repositorio las carpetas correspondientes a:

**01_PLANTILLA_MAESTRA**

- Plantilla eléctrica principal en DXF.
- Archivo DWT cuando sea posible producirlo realmente mediante AutoCAD.
- Configuración general de unidades y capas.

**02_BIBLIOTECA_BLOQUES**

- Bibliotecas DXF por familias.
- Bloques con atributos editables.
- Archivos de creación de bloques.

**03_TIPOS_LINEA**

- Archivo LIN personalizado.
- Definiciones de canalizaciones.
- Recursos de rotulación.

**04_AUTOLISP**

- Rutinas LSP funcionales.
- Comandos de inserción.
- Herramientas de edición y automatización.

**05_CATALOGOS**

- Lámina CAD de simbología general.
- Leyenda completa.
- Relación de códigos y descripción de símbolos.

**06_CODIGO_FUENTE**

- Scripts Python.
- Configuraciones.
- Archivos necesarios para regenerar los entregables.

**07_PRUEBAS**

- Comprobación de estructura DXF.
- Revisión de capas y referencias de bloques.
- Validación de atributos.
- Registro de pruebas de generación.
- Resultado de las comprobaciones de compatibilidad que realmente hayan podido ejecutarse.

**08_ENTREGA_FINAL**

- Archivos CAD principales.
- Archivos complementarios.
- Paquete ZIP con los entregables reales.
- Instrucciones breves de instalación y uso.

No crear archivos vacíos o falsos para completar la lista.

### 16. CONTROL DE CALIDAD

Antes de presentar el resultado:

1. Comprobar que los DXF puedan leerse mediante una biblioteca compatible.
2. Verificar que los bloques realmente existan en las tablas de bloques.
3. Confirmar que los atributos sean editables.
4. Verificar geometría, coordenadas y puntos base.
5. Comprobar que las capas tengan propiedades correctas.
6. Detectar referencias de bloques inexistentes.
7. Comprobar la validez de los tipos de línea.
8. Verificar que las cajas sean cuadradas o rectangulares, no círculos genéricos.
9. Revisar que los tomacorrientes incluyan correctamente la representación de puesta a tierra.
10. Confirmar que las luminarias registradas coincidan con las referencias disponibles.
11. Verificar que las rutinas de generación se ejecuten sin errores.
12. Diferenciar las pruebas automatizadas de las verificaciones que requieren abrir los archivos en AutoCAD.

**No declarar completado un archivo que no se haya generado correctamente.**

### 17. FORMA DE TRABAJO

Trabajar mediante fases técnicas:

**FASE 1 — INSPECCIÓN**

Analizar los archivos disponibles, el repositorio y las herramientas del entorno.

**FASE 2 — ARQUITECTURA CAD**

Definir unidades, capas, estructura de bloques, atributos, tipos de línea y convenciones.

**FASE 3 — DESARROLLO REAL**

Programar la generación de símbolos, bloques, canalizaciones y catálogo.

**FASE 4 — AUTOMATIZACIÓN**

Implementar rutinas AutoLISP y herramientas complementarias.

**FASE 5 — VERIFICACIÓN**

Ejecutar pruebas técnicas, corregir errores y validar archivos generados.

**FASE 6 — ENTREGA**

Organizar los entregables dentro del repositorio y presentar los archivos para revisión.

No solicitar aprobación por cada decisión técnica menor. Adoptar criterios profesionales coherentes y documentar las decisiones relevantes.

Si existen datos faltantes que impidan definir fielmente un símbolo, identificar la limitación y continuar con los componentes que sí puedan implementarse.

No reducir la calidad técnica para terminar más rápido.

### 18. INSTRUCCIÓN FINAL

**COMIENZA A TRABAJAR AHORA SOBRE EL REPOSITORIO ELECTRICAS.**

Inspecciona primero los archivos existentes y verifica qué referencias están disponibles.

Después implementa la estructura del proyecto y empieza a generar archivos CAD reales.

No te limites a describir cómo podría hacerse.

Escribe el código, ejecútalo, comprueba los resultados, corrige los errores y conserva los entregables en el repositorio.

El objetivo es obtener una BIBLIOTECA MAESTRA PROFESIONAL DE INSTALACIONES ELÉCTRICAS PARA AUTOCAD, preparada para utilizarse en expedientes técnicos reales y ampliarse posteriormente.

Al finalizar, presenta un resumen de archivos generados, pruebas realizadas, funcionalidades disponibles y limitaciones reales que requieran intervención de AutoCAD.

**La prioridad absoluta es la calidad técnica, la funcionalidad CAD y la reutilización profesional.**