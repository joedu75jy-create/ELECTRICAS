"""Paquete de uso directo: un DXF principal y herramientas en la misma carpeta."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape
import hashlib
import json
import re
import shutil

ROOT=Path(__file__).resolve().parents[1]


def guia_pdf(md,dest):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    styles=getSampleStyleSheet()
    styles['Normal'].fontName='Helvetica';styles['Normal'].fontSize=9;styles['Normal'].leading=13
    story=[]
    def markup(s):
        s=escape(s)
        return re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
    lines=md.read_text(encoding='utf-8').splitlines();i=0
    while i<len(lines):
        line=lines[i].strip();i+=1
        if not line:
            story.append(Spacer(1,5));continue
        if line.startswith('|'):
            rows=[line]
            while i<len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i].strip());i+=1
            data=[]
            for row in rows:
                cells=[c.strip() for c in row.strip('|').split('|')]
                if all(re.fullmatch(r'[:\- ]+',c) for c in cells):continue
                data.append([Paragraph(markup(c),styles['Normal']) for c in cells])
            table=Table(data,colWidths=[(A4[0]-80)/len(data[0])]*len(data[0]),repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7eef0')),
                ('GRID',(0,0),(-1,-1),.3,colors.HexColor('#bac7cc')),
                ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),
                ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
            story.append(table);continue
        if line.startswith('# '):style=styles['Title'];line=line[2:]
        elif line.startswith('## '):style=styles['Heading2'];line=line[3:]
        else:style=styles['Normal']
        story.append(Paragraph(markup(line),style))
    def footer(canvas,doc):
        canvas.setFont('Helvetica',8);canvas.drawString(40,25,'ELECTRICAS | Biblioteca integrada | '+str(doc.page))
    SimpleDocTemplate(str(dest),pagesize=A4,leftMargin=40,rightMargin=40,topMargin=40,bottomMargin=42,
                      title='Guia de uso ELECTRICAS integrada',author='ELECTRICAS').build(story,onFirstPage=footer,onLaterPages=footer)


def main():
    report=ROOT/'07_PRUEBAS'/'RESULTADOS.json'
    log=json.loads(report.read_text(encoding='utf-8'))
    assert log['resultado'].startswith('CORRECTO')
    stage=ROOT/'08_ENTREGA_FINAL'/'PAQUETE_INTEGRADO'
    stage.mkdir(parents=True,exist_ok=True)
    principal=ROOT/'11_PLANTILLA_GENERAL_INTEGRADA'/'PLANTILLA_GENERAL_INTEGRADA.dxf'
    files={principal.name:principal,
        'CATALOGO_INTEGRADO.pdf':ROOT/'05_CATALOGOS'/'CATALOGO_INTEGRADO.pdf',
        'CATALOGO_MONOCROMO.pdf':ROOT/'05_CATALOGOS'/'CATALOGO_MONOCROMO.pdf',
        'CATALOGO_BLOQUES.csv':ROOT/'05_CATALOGOS'/'CATALOGO_BLOQUES.csv',
        'GUIA_DE_USO.md':ROOT/'05_CATALOGOS'/'GUIA_DE_USO.md',
        'REFERENCIAS_Y_CONVENCIONES.md':ROOT/'05_CATALOGOS'/'REFERENCIAS_Y_CONVENCIONES.md',
        'PROCEDIMIENTO_DINAMICOS_AUTOCAD.md':ROOT/'05_CATALOGOS'/'PROCEDIMIENTO_DINAMICOS_AUTOCAD.md',
        'RESULTADOS_PRUEBAS.json':report}
    regeneration=ROOT/'07_PRUEBAS'/'REGENERACION_DESDE_ZIP.json'
    if regeneration.exists():files['REGENERACION_DESDE_ZIP.json']=regeneration
    trace=ROOT/'07_PRUEBAS'/'TRAZABILIDAD_DGE.json'
    if trace.exists():files['TRAZABILIDAD_DGE.json']=trace
    for name in ('ELECTRICAS.lsp','EI_CATALOGO.lsp','ELECTRICAS.dcl','INICIAR.scr'):
        files[name]=ROOT/'04_AUTOLISP'/name
    for name in ('EIC_METROS.lin','EIC_MILIMETROS.lin','ELECTRICAS_MONO.ctb'):
        files[name]=ROOT/'03_TIPOS_LINEA'/name
    for name,src in files.items():shutil.copyfile(src,stage/name)
    guia_pdf(ROOT/'05_CATALOGOS'/'GUIA_DE_USO.md',stage/'GUIA_DE_USO.pdf')
    quick='''ELECTRICAS INTEGRADA v2.0-DGE - INICIO RAPIDO

1. Descomprima TODO el ZIP en una carpeta local.
2. Abra PLANTILLA_GENERAL_INTEGRADA.dxf y guarde su proyecto como DWG.
3. En AutoCAD: APPLOAD > ELECTRICAS.lsp.
4. EICONFIG configura lineas; EIESCALA establece 50, 75 o 100.
5. EI abre el panel de las tres especialidades. Coloque, gire y asigne el codigo.

Una sola plantilla. Nueve layouts de catalogo dentro del mismo archivo.
Modelo en METROS. Bloques simbolicos con atributos editables.
EIEDITA: atributos | EIGIRA: giro | EINUMERA: numeracion | EIRUTA: canalizaciones.
Mantenga juntos LSP, EI_CATALOGO.lsp y DCL. EIAYUDA muestra todos los comandos.

Incluye biblioteca corregida, 36 simbolos base DGE adicionales y 42 rutas.
Solo L-01 a L-04 estan documentadas; faltan referencias para 9 luminarias.
DGE seccion 9 cotejada por simbolo: consulte referencia y pagina en el CSV y los atributos.
Sensores y dispositivos IC/DACI sin fuente especifica siguen identificados como pendientes.
DXF y pruebas de estructura ejecutadas. AutoLISP, apertura e impresion pendientes de AutoCAD.
No contiene DWG/DWT ni bloques dinamicos nativos generados o verificados.

CATALOGO_INTEGRADO.pdf: vista de los layouts del DXF.
GUIA_DE_USO.pdf: instalacion, escalas, comandos y limitaciones.
RESULTADOS_PRUEBAS.json: pruebas realmente ejecutadas.
FUENTES/: codigo y referencia original para regenerar y continuar el trabajo.
'''
    (stage/'LEEME_PRIMERO.txt').write_text(quick,encoding='utf-8')
    # Código y dependencias en su estructura original para que la regeneración funcione.
    sources=stage/'FUENTES'
    for directory in ('06_CODIGO_FUENTE','04_AUTOLISP'):
        for src in (ROOT/directory).rglob('*'):
            if not src.is_file() or '__pycache__' in src.parts:continue
            target=sources/src.relative_to(ROOT)
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
    native=Path('05_CATALOGOS')/'PROCEDIMIENTO_DINAMICOS_AUTOCAD.md'
    (sources/native).parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/native,sources/native)
    checksums={str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='SHA256.json'}
    (stage/'SHA256.json').write_text(json.dumps(checksums,ensure_ascii=False,indent=2),encoding='utf-8')
    zip_path=ROOT/'08_ENTREGA_FINAL'/'ELECTRICAS_INTEGRADA.zip'
    with ZipFile(zip_path,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(stage.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(stage)))
    with ZipFile(zip_path) as z:
        assert z.testzip() is None
        assert principal.name in z.namelist()
        assert len([n for n in z.namelist() if n.lower().endswith('.dxf')])==1,'El paquete de uso debe tener un solo DXF principal.'
        for name,digest in checksums.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
    if log.get('revision_DGE'):
        shutil.copyfile(zip_path,zip_path.with_name('ELECTRICAS_INTEGRADA_DGE_v2.zip'))
    print(json.dumps({'zip':str(zip_path),'bytes':zip_path.stat().st_size,'archivos':len(checksums)+1,
                      'sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest()},indent=2))


if __name__=='__main__':main()
