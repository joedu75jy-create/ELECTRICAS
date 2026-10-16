# Preparacion de bloques dinamicos nativos en AutoCAD

**Estado: procedimiento preparado; operaciones no ejecutadas.** Los bloques entregados son convencionales con atributos. EITIPO cambia entre definiciones y no constituye un estado de visibilidad nativo.

1. Abra el DXF integrado en AutoCAD de escritorio y guarde una copia de trabajo DWG. Pruebe INSERT, EATTEDIT y las escalas antes de editar definiciones.
2. En BEDIT abra, por ejemplo, IE_TN_M040. Use BSAVEAS para conservar una copia con prefijo DIN_. El archivo original debe permanecer sin cambios.
3. Para giro, agregue un parametro de rotacion con centro en 0,0 y una accion de rotacion asociada. Incluya la geometria del icono; excluya las definiciones de atributos que deban mantenerse horizontales. Compruebe en BTESTBLOCK que el codigo no gira ni se superpone al icono.
4. Para alineacion al muro, agregue un parametro de alineacion en el punto base, con direccion de referencia coherente con el plano. Pruebe el comportamiento con referencias verticales, horizontales y oblicuas.
5. Para variantes, trabaje en una definicion nueva: copie la geometria de las variantes compatibles, conserve un origen comun y cree un parametro de visibilidad con estados claramente nombrados. Use una sola definicion por atributo comun, evitando etiquetas duplicadas. Las propiedades MONTAJE, ALTURA y TIPO deben actualizarse de forma coherente; un cambio de visibilidad por si solo no cambia los atributos.
6. En cajas, puede emplear variantes de tamano mediante visibilidad. Si se decide usar estiramiento, defina un parametro lineal y una accion que seleccione solo los vertices correspondientes; compruebe el marco, codigo interior y punto base. No aplique estiramiento indiscriminado a los simbolos de dispositivos.
7. En BTESTBLOCK pruebe cada estado, giro y alineacion; copie referencias, edite atributos y pruebe en 1:50, 1:75 y 1:100. Use ATTSYNC tras cambios de definicion cuando proceda y revise los valores existentes antes y despues.
8. Cierre con guardar, inserte referencias nuevas y existentes, reabra el DWG y verifique sus propiedades dinamicas. Registre la version exacta de AutoCAD y los resultados. Solo despues identifique el bloque como dinamico nativo verificado.

Los comandos EIGIRA, EITIPO y EIINSERTA de esta entrega estan destinados a las definiciones IE_, IC_ y DACI_ originales. No los aplique automaticamente a las nuevas definiciones DIN_: las acciones dinamicas deben probarse y utilizarse mediante sus pinzamientos y propiedades propias.

Para finalizar una DWT, configure unidades, capas, fuentes, CTB, dispositivo y tamanos de papel; purgue solo elementos comprobados como innecesarios y use GUARDAR COMO > Plantilla de dibujo AutoCAD (*.dwt). Reabra la DWT creando un dibujo nuevo y repita una insercion por especialidad. El cambio de extension de DXF a DWG o DWT no convierte el formato.
