;;; ELECTRICAS v1 - Biblioteca integrada IE / IC / DACI.
;;; Bloques convencionales con atributos. No crea dinamicos nativos.
;;; AutoLISP sin dependencia ActiveX; pendiente de ejecucion real en AutoCAD.
;;; Archivo UTF-8. Abra primero PLANTILLA_GENERAL_INTEGRADA.dxf.

(setq EI:escala 50.0)
(setq EI:base nil)

(defun EI:archivo (nombre / p)
  (or (findfile nombre)
      (and EI:base (findfile (strcat EI:base nombre)))
      (findfile (strcat (getvar "DWGPREFIX") nombre))))

(defun EI:iniciar (/ p)
  (if (not (boundp 'EI:catalogo))
    (progn
      (setq p (EI:archivo "EI_CATALOGO.lsp"))
      (if (not p)
        (setq p (getfiled "Seleccione EI_CATALOGO.lsp de la entrega" "" "lsp" 0)))
      (if p
        (progn
          (setq EI:base (strcat (vl-filename-directory p) "/"))
          (load p)))))
  (if (boundp 'EI:catalogo) T
    (progn (princ "\nNo se cargo el catalogo. Mantenga juntos los archivos de la entrega.") nil)))

(defun EI:modelo ()
  (if (> (getvar "CVPORT") 1) T
    (progn (princ "\nTrabaje en Modelo o dentro de una ventana de Modelo.") nil)))

(defun EI:factor (/ u)
  (setq u (getvar "INSUNITS"))
  (cond ((= u 6) (/ EI:escala 1000.0))
        ((= u 4) EI:escala)
        (T (princ "\nUnidades sin definir: configure INSUNITS=6 (m) o 4 (mm).") nil)))

(defun EI:valor (tag vals defecto / item)
  (if (setq item (assoc tag vals)) (cdr item) defecto))

(defun EI:props (en / a d out)
  (setq out nil a (entnext en))
  (while (and a (/= (cdr (assoc 0 (setq d (entget a)))) "SEQEND"))
    (if (= (cdr (assoc 0 d)) "ATTRIB")
      (setq out (cons (cons (strcase (cdr (assoc 2 d))) (cdr (assoc 1 d))) out)))
    (setq a (entnext a)))
  out)

(defun EI:set (en tag val / a d done)
  (setq a (entnext en) done nil)
  (while (and a (not done) (/= (cdr (assoc 0 (setq d (entget a)))) "SEQEND"))
    (if (and (= (cdr (assoc 0 d)) "ATTRIB") (= (strcase (cdr (assoc 2 d))) tag))
      (progn
        (setq d (subst (cons 1 val) (assoc 1 d) d))
        (if (and (= tag "CODIGO") (wcmatch (cdr (assoc 2 (entget en))) "*CAJA*"))
          (setq d (subst (cons 41 (min 1.0 (/ 6.2 (max 1.0 (* (strlen val) 1.6))))) (assoc 41 d) d)))
        (entmod d) (setq done T)))
    (setq a (entnext a)))
  (entupd en) done)

(defun EI:seleccionar (/ pick en d)
  (setq pick (entsel "\nSeleccione un bloque IE / IC / DACI: "))
  (if pick
    (progn
      (setq en (car pick) d (entget en))
      (if (and (= (cdr (assoc 0 d)) "INSERT")
               (wcmatch (strcase (cdr (assoc 2 d))) "IE_*,IC_*,DACI_*")) en
        (progn (princ "\nSeleccione una referencia de la biblioteca integrada.") nil)))))

(defun EI:entrada (nombre)
  (car (vl-remove-if-not '(lambda (e) (= (car e) nombre)) EI:catalogo)))

(defun EI:prefijo (s / n)
  (setq n (strlen s))
  (while (and (> n 0) (wcmatch (substr s n 1) "#")) (setq n (1- n)))
  (if (> n 0) (substr s 1 n) "EQ-"))

(defun EI:pad (n / s)
  (setq s (itoa n))
  (while (< (strlen s) 3) (setq s (strcat "0" s))) s)

(defun EI:codigos (excluir / ss i en vals out)
  (setq ss (ssget "_X" '((0 . "INSERT") (2 . "IE_*,IC_*,DACI_*"))) i 0 out nil)
  (if ss
    (repeat (sslength ss)
      (setq en (ssname ss i) i (1+ i))
      (if (not (and excluir (ssmemb en excluir)))
        (if (setq vals (assoc "CODIGO" (EI:props en)))
          (setq out (cons (strcase (cdr vals)) out)))))) out)

(defun EI:siguiente (codigo / prefix n usado candidate)
  (setq prefix (EI:prefijo codigo) n 1 usado (EI:codigos nil))
  (while (member (strcase (setq candidate (strcat prefix (EI:pad n)))) usado)
    (setq n (1+ n))) candidate)

(defun EI:crear (entry pt sc ang vals / name def d tag p a en flags txt width failed)
  (setq name (car entry))
  (if (= (EI:valor "GIRO_GRAFICO" vals "") "FIJO_LEGIBLE") (setq ang 0.0))
  (if (not (tblsearch "BLOCK" name))
    (progn (princ "\nBloque ausente: abra la plantilla integrada o copie el bloque a este dibujo.") nil)
    (progn
      (if (not (tblsearch "LAYER" (nth 5 entry)))
        (entmake (list '(0 . "LAYER") '(100 . "AcDbSymbolTableRecord")
                       '(100 . "AcDbLayerTableRecord") (cons 2 (nth 5 entry)) '(70 . 0) '(62 . 7))))
      (if (entmake (list '(0 . "INSERT") '(100 . "AcDbEntity") (cons 8 (nth 5 entry))
                         '(100 . "AcDbBlockReference") (cons 2 name) '(66 . 1)
                         (cons 10 pt) (cons 41 sc) (cons 42 sc) (cons 43 sc) (cons 50 ang)))
        (progn
          (setq en (entlast) def (entnext (tblobjname "BLOCK" name)) failed nil)
          (while (and def (/= (cdr (assoc 0 (setq d (entget def)))) "ENDBLK"))
            (if (= (cdr (assoc 0 d)) "ATTDEF")
              (progn
                (setq tag (strcase (cdr (assoc 2 d)))
                      txt (EI:valor tag vals (cdr (assoc 1 d)))
                      a (cdr (assoc 10 d))
                      p (list (+ (car pt) (* sc (car a))) (+ (cadr pt) (* sc (cadr a))) (caddr pt))
                      flags (logand 1 (cdr (assoc 70 d)))
                      width (cond ((assoc 41 d) (cdr (assoc 41 d))) (T 1.0)))
                ;; Rotacion del icono independiente: las etiquetas permanecen ordenadas y horizontales.
                (if (and (= tag "CODIGO") (< (car a) 0))
                  (setq width (min 1.0 (/ 6.2 (max 1.0 (* (strlen txt) 1.6))))))
                (if (not (entmake (list '(0 . "ATTRIB") '(100 . "AcDbEntity") (cons 8 (nth 5 entry))
                  '(100 . "AcDbText") (cons 10 p) (cons 40 (* sc (cdr (assoc 40 d))))
                  (cons 1 txt) '(50 . 0.0) (cons 41 width) (cons 7 (cdr (assoc 7 d)))
                  '(100 . "AcDbAttribute") (cons 2 tag) (cons 70 flags) '(74 . 0))))
                  (setq failed T))))
            (setq def (entnext def)))
          (entmake '((0 . "SEQEND")))
          (if failed
            (progn (entdel en) (princ "\nNo se pudo crear un atributo. Se retiro la insercion incompleta.") nil)
            (progn (entupd en) en)))
        (progn (princ "\nNo se pudo insertar el bloque.") nil)))))

(defun EI:familias (/ out)
  (setq out nil)
  (foreach e EI:catalogo (if (not (member (nth 4 e) out)) (setq out (append out (list (nth 4 e)))))) out)

(defun EI:lista (indice / fam)
  (setq fam (nth indice (EI:familias)))
  (setq EI:opciones (vl-remove-if-not '(lambda (e) (= (nth 4 e) fam)) EI:catalogo))
  (start_list "simbolos")
  (foreach e EI:opciones (add_list (strcat (nth 3 e) ":" (cadr e) "  |  " (nth 2 e))))
  (end_list) (set_tile "simbolos" "0")
  (set_tile "detalle" (car (car EI:opciones))) (setq EI:indice 0))

(defun EI:dialogo (/ file id result entry)
  (if (and (EI:iniciar) (setq file (EI:archivo "ELECTRICAS.dcl")))
    (progn
      (setq id (load_dialog file))
      (if (and (>= id 0) (new_dialog "electrica" id))
        (progn
          (start_list "familia") (foreach f (EI:familias) (add_list f)) (end_list)
          (set_tile "familia" "0") (EI:lista 0)
          (action_tile "familia" "(EI:lista (atoi $value))")
          (action_tile "simbolos" "(setq EI:indice (atoi $value)) (set_tile \"detalle\" (car (nth EI:indice EI:opciones)))")
          (action_tile "accept" "(done_dialog 1)")
          (action_tile "cancel" "(done_dialog 0)")
          (setq result (start_dialog))
          (if (= result 1) (setq entry (nth EI:indice EI:opciones)))))
      (if (and id (>= id 0)) (unload_dialog id)) entry)
    (progn (princ "\nPanel no disponible. Use EIINSERTA con nombre de bloque o codigo SISTEMA:TIPO.") nil)))

(defun EI:colocar (entry / sc pt ang vals cod default used)
  (if (and entry (EI:modelo) (setq sc (EI:factor)))
    (progn
      (setq pt (getpoint "\nPunto de insercion: "))
      (if pt
        (progn
          (setq ang (getangle pt "\nGiro del simbolo <0>: "))
          (if (not ang) (setq ang 0.0))
          (setq ang (angle '(0.0 0.0 0.0) (trans (polar '(0.0 0.0 0.0) ang 1.0) 1 0 T))
                default (EI:siguiente (cadr entry)) used (EI:codigos nil))
          (setq cod (strcase (getstring T (strcat "\nCodigo <" default ">: "))))
          (if (= cod "") (setq cod default))
          (while (member cod used)
            (setq cod (strcase (getstring T "\nCodigo existente. Escriba otro codigo: "))))
          (if (= cod "") (setq cod default))
          (setq vals (cons (cons "CODIGO" cod) (nth 6 entry)) EI:sistema (nth 3 entry))
          (EI:crear entry (trans pt 1 0) sc ang vals))))))

(defun c:EIPANEL () (EI:colocar (EI:dialogo)) (princ))
(defun c:EI () (c:EIPANEL))

(defun c:EIINSERTA (/ code matches)
  (if (EI:iniciar)
    (progn
      (setq code (strcase (getstring T "\nNombre de bloque o clave (ejemplo IC:D2): ")))
      (setq matches (vl-remove-if-not
        '(lambda (e) (or (= code (car e)) (= code (strcat (nth 3 e) ":" (cadr e))) (= code (cadr e)))) EI:catalogo))
      (cond ((= (length matches) 1) (EI:colocar (car matches)))
            ((> (length matches) 1) (princ "\nCodigo ambiguo. Use el prefijo IE:, IC: o DACI:."))
            (T (princ "\nCodigo desconocido. Use EIPANEL para consultar el catalogo."))))) (princ))

(defun c:EIESCALA (/ s)
  (initget 6) (setq s (getreal "\nEscala de impresion: 50, 75, 100 u otra <50>: "))
  (if s (setq EI:escala s))
  (princ (strcat "\nProximas inserciones a 1:" (rtos EI:escala 2 0) ". Las existentes conservan su escala.")) (princ))

(defun c:EIEDITA (/ en vals choice val)
  (if (setq en (EI:seleccionar))
    (progn
      (setq vals (EI:props en))
      (foreach item vals (princ (strcat "\n" (car item) " = " (cdr item))))
      (setq choice (strcase (getstring "\nAtributo que desea editar <CODIGO>: ")))
      (if (= choice "") (setq choice "CODIGO"))
      (if (assoc choice vals)
        (progn (setq val (getstring T "\nNuevo valor (vacio borra el contenido): "))
          (EI:set en choice val))
        (princ "\nAtributo inexistente.")))) (princ))

(defun EI:recrear (en entry angle vals / d new)
  (setq d (entget en))
  (if (< (abs (- (cdr (assoc 41 d)) (cdr (assoc 42 d)))) .000001)
    (if (setq new (EI:crear entry (cdr (assoc 10 d)) (cdr (assoc 41 d)) angle vals))
      (progn (entdel en) new))
    (progn (princ "\nBloque con escala no uniforme. Normalice la escala antes de esta operacion.") nil)))

(defun c:EIGIRA (/ en d a)
  (if (and (EI:iniciar) (setq en (EI:seleccionar)))
    (progn
      (setq d (entget en) a (getangle "\nNuevo giro absoluto en UCS: "))
      (if a
        (EI:recrear en (EI:entrada (cdr (assoc 2 d)))
          (angle '(0.0 0.0 0.0) (trans (polar '(0.0 0.0 0.0) a 1.0) 1 0 T)) (EI:props en))))) (princ))

(defun c:EIALINEA (/ en d a b)
  (if (and (EI:iniciar) (setq en (EI:seleccionar)) (setq a (getpoint "\nPrimer punto de alineacion: "))
           (setq b (getpoint a "\nSegundo punto de alineacion: ")))
    (progn (setq d (entget en))
      (EI:recrear en (EI:entrada (cdr (assoc 2 d))) (angle (trans a 1 0) (trans b 1 0)) (EI:props en)))) (princ))

(defun c:EIREORDENAR (/ en d)
  (if (and (EI:iniciar) (setq en (EI:seleccionar)))
    (progn (setq d (entget en))
      (EI:recrear en (EI:entrada (cdr (assoc 2 d))) (cdr (assoc 50 d)) (EI:props en)))) (princ))

(defun c:EITIPO (/ en entry vals old keep)
  (if (and (EI:iniciar) (setq en (EI:seleccionar)) (setq entry (EI:dialogo)))
    (progn
      (setq old (EI:props en) vals (nth 6 entry))
      (foreach pair old
        (if (not (member (car pair) '("TIPO" "DESCRIPCION" "SISTEMA" "MONTAJE" "NORMA" "ALTURA" "PUERTOS" "CATEGORIA" "FUNCION")))
          (if (assoc (car pair) vals) (setq vals (subst pair (assoc (car pair) vals) vals)))))
      (EI:recrear en entry (cdr (assoc 50 (entget en))) vals))) (princ))

(defun c:EINUMERA (/ ss prefix start i en code reserved n)
  (if (setq ss (ssget '((0 . "INSERT") (2 . "IE_*,IC_*,DACI_*"))))
    (progn
      (setq prefix (strcase (getstring T "\nPrefijo de identificacion (ejemplo D-): ")))
      (initget 6) (setq start (getint "\nPrimer numero <1>: "))
      (setq n (if start start 1) reserved (EI:codigos ss) i 0)
      (repeat (sslength ss)
        (while (member (setq code (strcat prefix (EI:pad n))) reserved) (setq n (1+ n)))
        (setq en (ssname ss i)) (EI:set en "CODIGO" code)
        (setq reserved (cons code reserved) n (1+ n) i (1+ i)))
      (princ "\nNumeracion aplicada en orden de seleccion; se evitaron codigos ya utilizados."))) (princ))

(defun EI:seleccionruta (/ i n)
  (setq i 0)
  (foreach r EI:rutas (setq i (1+ i)) (princ (strcat "\n" (itoa i) ". " (cadr r))))
  (initget 6) (setq n (getint "\nNumero de tipo de ruta: "))
  (if (and n (<= n (length EI:rutas))) (nth (1- n) EI:rutas)
    (progn (princ "\nNumero fuera de lista.") nil)))

(defun c:EIRUTA (/ r fact p pts q ent)
  (if (and (EI:iniciar) (EI:modelo) (setq fact (EI:factor)) (setq r (EI:seleccionruta)))
    (if (tblsearch "LTYPE" (car r))
      (progn
        (setq EI:sistema (nth 3 r))
        (setq p (getpoint "\nInicio de canalizacion: ") pts nil)
        (if p
          (progn
            (setq pts (list (trans p 1 0)))
            (while (setq q (getpoint p "\nSiguiente vertice <terminar>: "))
              (setq pts (append pts (list (trans q 1 0))) p q))
            (if (> (length pts) 1)
              (progn
                (entmake (append (list '(0 . "LWPOLYLINE") '(100 . "AcDbEntity")
                  (cons 8 (nth 2 r)) (cons 6 (car r)) (cons 48 (/ EI:escala 50.0))
                  '(100 . "AcDbPolyline") (cons 90 (length pts)) '(70 . 128) (cons 38 (caddr (car pts))))
                  (mapcar '(lambda (v) (cons 10 (list (car v) (cadr v)))) pts)))
                (princ "\nRuta creada. Use EIROTULA para circuito, montaje y diametro adicional."))))))
      (princ "\nTipo de linea ausente: ejecute EICARGALIN o abra la plantilla integrada."))) (princ))

(defun c:EIROTULA (/ p q ang txt fact sys default layer)
  (setq default (if (boundp 'EI:sistema) EI:sistema "IE"))
  (initget "IE IC DACI")
  (setq sys (getkword (strcat "\nSistema [IE/IC/DACI] <" default ">: ")))
  (if (not sys) (setq sys default))
  (setq layer (cond ((= sys "IC") "IC-TEXTOS") ((= sys "DACI") "DACI-TEXTOS") (T "IE-TEXTOS")))
  (if (and (EI:modelo) (setq fact (EI:factor))
           (setq p (getpoint "\nPunto de rotulo sobre la ruta: "))
           (setq q (getpoint p "\nDireccion del tramo: ")))
    (progn
      (setq ang (angle (trans p 1 0) (trans q 1 0)))
      (if (and (> ang (/ pi 2)) (< ang (* 1.5 pi))) (setq ang (+ ang pi)))
      (setq txt (getstring T "\nTexto (ej. EMT D25 mm | C-01 | TECHO): "))
      (if (/= txt "")
        (entmake (list '(0 . "TEXT") '(100 . "AcDbEntity") (cons 8 layer)
          '(100 . "AcDbText") (cons 10 (polar (trans p 1 0) (+ ang (/ pi 2)) (* 2 fact)))
          (cons 40 (* 2.5 fact)) (cons 1 txt) '(7 . "EI_TEXTO") (cons 50 ang)))))) (princ))

(defun c:EICIRCUITO (/ ss code i en)
  (setq code (getstring T "\nIdentificacion de circuito o lazo: "))
  (if (setq ss (ssget '((0 . "INSERT") (2 . "IE_*,IC_*,DACI_*"))))
    (progn (setq i 0)
      (repeat (sslength ss) (EI:set (ssname ss i) "CIRCUITO" code) (setq i (1+ i))))) (princ))

(defun c:EISELECCIONA (/ system pattern ss)
  (initget "IE IC DACI") (setq system (getkword "\nSistema [IE/IC/DACI] <IE>: "))
  (if (not system) (setq system "IE"))
  (setq pattern (strcat system "_*") ss (ssget "_X" (list '(0 . "INSERT") (cons 2 pattern))))
  (sssetfirst nil ss) (princ))

(defun c:EICARGALIN (/ file old err)
  (if (and (EI:iniciar)
           (setq file (EI:archivo (if (= (getvar "INSUNITS") 4) "EIC_MILIMETROS.lin" "EIC_METROS.lin"))))
    (progn
      (setq old (getvar "CMDECHO") err *error*)
      (defun *error* (msg) (setvar "CMDECHO" old) (setq *error* err) (princ))
      (setvar "CMDECHO" 0)
      (if (not (tblsearch "STYLE" "EI_TEXTO"))
        (entmake '((0 . "STYLE") (100 . "AcDbSymbolTableRecord") (100 . "AcDbTextStyleTableRecord")
          (2 . "EI_TEXTO") (70 . 0) (40 . 0.0) (41 . 1.0) (3 . "arial.ttf"))))
      (foreach r EI:rutas
        (if (not (tblsearch "LTYPE" (car r))) (command "_.-LINETYPE" "_Load" (car r) file "")))
      (setvar "CMDECHO" old) (setq *error* err)
      (princ "\nTipos de linea cargados segun INSUNITS."))) (princ))

(defun c:EICATALOGO (/ f)
  (setvar "TILEMODE" 1)
  (setq f (if (= (getvar "INSUNITS") 4) 1000.0 1.0))
  (command "_.ZOOM" "_Window" (trans (list 0.0 (* -40.0 f) 0.0) 0 1)
    (trans (list (* 21.0 f) (* -25.15 f) 0.0) 0 1)) (princ))

(defun c:EICONFIG ()
  (setvar "LTSCALE" 1.0) (setvar "MSLTSCALE" 0) (setvar "PSLTSCALE" 0)
  (princ "\nLTSCALE=1, MSLTSCALE=0, PSLTSCALE=0. Use EIESCALA para las nuevas inserciones.") (princ))

(defun c:EIAYUDA ()
  (princ "\nEI / EIPANEL: catalogo e insercion. EIINSERTA: insertar por codigo.")
  (princ "\nEIESCALA: 50/75/100. EIEDITA: atributos. EIGIRA / EIALINEA: orientar.")
  (princ "\nEITIPO: variante. EINUMERA: codigos. EICIRCUITO: circuito por seleccion.")
  (princ "\nEIRUTA / EIROTULA: canalizacion y rotulos. EISELECCIONA: sistema. EICONFIG: lineas.")
  (princ "\nEIREORDENAR: recuperar etiquetas horizontales. EICATALOGO: zoom biblioteca.")
  (princ "\nLos bloques son convencionales. Rutinas pendientes de prueba en AutoCAD.") (princ))

(princ "\nELECTRICAS integrada cargada. EIAYUDA muestra comandos; EI abre el panel.")
(princ)
