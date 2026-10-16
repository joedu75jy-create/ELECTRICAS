# AMPLIACIÓN DEL PROMPT MAESTRO PARA CODEX
## INCORPORACIÓN DE COMUNICACIONES, DATA Y DETECCIÓN Y ALARMA CONTRA INCENDIOS

**INSTRUCCIÓN GENERAL**

Amplía el proyecto ELECTRICAS para incorporar dos bibliotecas profesionales adicionales:

1. Sistema de cableado estructurado y comunicaciones.
2. Sistema de detección y alarma contra incendios (DACI).

Ambas deberán integrarse a la plantilla maestra, conservando los bloques de iluminación, tomacorrientes, interruptores, tuberías, cajas de paso y demás elementos eléctricos.

No sustituir ni eliminar las funcionalidades desarrolladas.

## 19. SISTEMA DE DATA Y COMUNICACIONES

### 19.1 Bloques CAD

Desarrollar bloques independientes para:

- Salida simple de data RJ45.
- Salida doble de data Cat 6A (2 RJ45).
- Salida de voz.
- Salida combinada voz/data.
- Punto de acceso inalámbrico (Wi-Fi / AP).
- Cámara CCTV tipo domo.
- Cámara CCTV tipo bala.
- Cámara CCTV tipo PTZ.
- Punto de control de acceso.
- Lector de tarjetas.
- Cerradura electromagnética.
- Pulsador de salida.
- Rack de comunicaciones.
- Gabinete de comunicaciones.
- Patch panel.
- Switch de comunicaciones.
- Caja de paso de comunicaciones.
- Salida de fibra óptica.
- Punto de interconexión de fibra óptica.

**Criterio principal:** cada puesto de trabajo con computadora tendrá una salida doble de data Cat 6A, compuesta por dos conectores RJ45, cuando así lo requiera el diseño del proyecto.

El bloque deberá permitir editar código, identificación del punto, número de puertos, montaje y demás atributos necesarios.

### 19.2 Canalizaciones de comunicaciones

Crear tipos de línea para:

- Cableado U/FTP o F/UTP Cat 6A, de acuerdo con las especificaciones del proyecto.
- Fibra óptica.
- Canalización EMT.
- Canalización PVC.
- Canalización corrugada.
- Bandeja portacables de comunicaciones.
- Canalización para CCTV.
- Canalización para control de acceso.

El texto de identificación deberá incorporarse mediante rotulación compatible con AutoCAD.

Diferenciar las rutas y sistemas mediante capas, tipos de línea y códigos.

Respetar las separaciones entre cableado de energía y telecomunicaciones.

### 19.3 Normativa de referencia

Considerar, según corresponda:

- ANSI/TIA-568.
- ANSI/TIA-569.
- ANSI/TIA-606.
- ANSI/TIA-607.
- Reglamento Nacional de Edificaciones aplicable.
- Especificaciones técnicas del proyecto.

No confundir un símbolo convencional CAD con un símbolo oficialmente normalizado.

## 20. SISTEMA DE DETECCIÓN Y ALARMA CONTRA INCENDIOS (DACI)

### 20.1 Bloques CAD

Desarrollar una biblioteca con símbolos profesionales para:

- Detector de humo.
- Detector térmico.
- Detector multicriterio.
- Detector de humo para ductos.
- Estación manual de alarma.
- Sirena de alarma.
- Luz estroboscópica.
- Sirena con luz estroboscópica integrada.
- Panel central de alarma contra incendios (FACP).
- Panel repetidor.
- Módulo de monitoreo.
- Módulo de control.
- Módulo aislador.
- Fuente auxiliar de alimentación.
- Caja de paso del sistema DACI.
- Interfaz de supervisión o control de sistemas vinculados.

Cada bloque deberá tener:

- Geometría CAD claramente identificable.
- Punto base de inserción.
- Código de identificación.
- Atributos editables.
- Posibilidad de rotación.
- Representación diferenciada.
- Escala adecuada para planos arquitectónicos.
- Compatibilidad con las capas del sistema DACI.

### 20.2 Canalizaciones y circuitos

Crear tipos de línea específicos para:

- Circuitos SLC.
- Circuitos NAC.
- Circuitos de alimentación.
- Circuitos de supervisión.
- Conexiones a módulos.
- Interconexión de paneles.
- Canalizaciones EMT, PVC o corrugadas, cuando corresponda.

Los símbolos y canalizaciones deberán tener códigos reconocibles, sin confundir los circuitos de detección con los de notificación.

La nomenclatura de cables y circuitos deberá corresponder a los equipos y a la arquitectura del sistema seleccionada en el proyecto.

### 20.3 Normativa

Considerar:

- RNE A.130 y demás disposiciones aplicables.
- NFPA 72, cuando corresponda.
- Normas técnicas nacionales aplicables.
- Requisitos de compatibilidad y supervisión del sistema.

**IMPORTANTE:** Este apartado comprende detección, alarma y notificación de incendios. No incluye automáticamente redes de rociadores, gabinetes de manguera, bombas ni tuberías hidráulicas contra incendios.

## 21. NUEVAS CAPAS CAD

Incorporar las siguientes capas a la estructura del proyecto:

| Capa | Aplicación |
|---|---|
| IC-DATA | Salidas de data |
| IC-VOZ | Comunicaciones de voz |
| IC-WIFI | Puntos inalámbricos |
| IC-CCTV | Videovigilancia |
| IC-ACCESOS | Control de accesos |
| IC-RACK | Racks y gabinetes |
| IC-FIBRA | Fibra óptica |
| IC-CANALIZACIONES | Canalizaciones de comunicaciones |
| IC-CAJAS | Cajas de paso |
| IC-TEXTOS | Identificación y etiquetas |
| DACI-HUMO | Detectores de humo |
| DACI-TERMICO | Detectores térmicos |
| DACI-ESTACIONES | Estaciones manuales |
| DACI-SIRENAS | Dispositivos de notificación |
| DACI-PANELES | Centrales y repetidores |
| DACI-MODULOS | Módulos de control y monitoreo |
| DACI-SLC | Circuitos de detección |
| DACI-NAC | Circuitos de notificación |
| DACI-CANALIZACIONES | Tuberías y canalizaciones |
| DACI-CAJAS | Cajas de paso |
| DACI-TEXTOS | Rotulación |

Asignar propiedades BYLAYER, colores ACI, espesores y tipos de línea compatibles con impresión técnica.

## 22. AMPLIACIÓN DE BLOQUES DINÁMICOS Y AUTOMATIZACIÓN

Los símbolos de DATA, CCTV, Wi-Fi, control de acceso y DACI deberán integrarse al mismo sistema de inserción de bloques.

Implementar, cuando sea técnicamente posible:

- Rotación y alineación.
- Edición de atributos.
- Identificación de dispositivos.
- Numeración y codificación de puntos.
- Rotulación de circuitos.
- Selección de variantes.
- Herramientas de inserción mediante AutoLISP.

Los bloques dinámicos nativos deberán verificarse en AutoCAD; no presentar bloques convencionales como dinámicos.

## 23. ACTUALIZACIÓN DE ENTREGABLES

Ampliar las carpetas del proyecto con:

**09_DATA_COMUNICACIONES**
- Biblioteca DXF.
- Bloques y atributos.
- Simbología normalizada.
- Canalizaciones y tipos de línea.
- Leyenda de comunicaciones.

**10_ALARMA_CONTRAINCENDIOS**
- Biblioteca DACI en DXF.
- Detectores y dispositivos.
- Centrales y módulos.
- Circuitos SLC y NAC.
- Canalizaciones.
- Leyenda DACI.

**11_PLANTILLA_GENERAL_INTEGRADA**
- Plantilla CAD con las tres especialidades.
- Biblioteca maestra ordenada.
- Capas y tipos de línea.
- Catálogo de bloques.
- Scripts de automatización.
- Archivos complementarios necesarios.

Las tres especialidades serán:

1. Instalaciones eléctricas.
2. DATA y comunicaciones.
3. Detección y alarma contra incendios.

## 24. CONTROL DE CALIDAD ADICIONAL

Antes de concluir:

- Verificar que los bloques sean insertables y editables.
- Verificar que cada especialidad tenga capas independientes.
- Comprobar que no existan nombres de bloques duplicados que generen conflictos.
- Verificar códigos, atributos y puntos de inserción.
- Confirmar que los circuitos DACI se diferencien de las rutas de DATA y electricidad.
- Validar los DXF mediante herramientas CAD disponibles.
- Identificar las funcionalidades que requieran pruebas adicionales en AutoCAD.

**INSTRUCCIÓN FINAL**

Incorporar estas dos especialidades al PROMPT MAESTRO ORIGINAL y trabajar sobre un único repositorio ELECTRICAS.

No crear tres proyectos aislados. Desarrollar una sola plantilla profesional con bibliotecas separadas por especialidad.

El resultado deberá permitir insertar símbolos, dibujar canalizaciones, editar atributos, organizar capas y reutilizar la plantilla en futuros expedientes técnicos.

La plantilla debe parecer desarrollada por un dibujante CAD senior especializado en instalaciones de edificaciones públicas.

**GENERA ARCHIVOS CAD REALES. NO ÚNICAMENTE INFORMES, IMÁGENES NI DIBUJOS DEMOSTRATIVOS.**