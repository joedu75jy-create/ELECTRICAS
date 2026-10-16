"""Verificación del DXF guardado y coherencia entre catálogo, LIN, LSP y escalas.

No simula la ejecución de AutoCAD ni declara probado el intérprete AutoLISP.
"""
from pathlib import Path
from collections import Counter
from math import isclose, radians
import json
import re
import ezdxf
from ezdxf.addons import Importer, acadctb
from ezdxf.tools.complex_ltype import lin_compiler
from catalogo import catalogo, rutas
from convertir_unidades import convertir

ROOT=Path(__file__).resolve().parents[1]


def parse_lisp(text):
    tokens=re.findall(r';[^\n]*|"(?:\\.|[^"\\])*"|[()]|\'|[^\s()\'";]+',text)
    tokens=[t for t in tokens if not t.startswith(';')]
    i=0
    def read():
        nonlocal i
        if i>=len(tokens):raise AssertionError('Expresion AutoLISP incompleta')
        token=tokens[i];i+=1
        if token=='(':
            node=[]
            while i<len(tokens) and tokens[i]!=')':node.append(read())
            assert i<len(tokens),'Parentesis sin cerrar'
            i+=1;return node
        if token==')':raise AssertionError('Parentesis de cierre extra')
        if token=="'":return ['quote',read()]
        return token
    result=[]
    while i<len(tokens):result.append(read())
    return result


def check_lisp(path):
    forms=parse_lisp(path.read_text(encoding='utf-8'))
    count=0
    def visit(form):
        nonlocal count
        if not isinstance(form,list) or not form:return
        head=form[0].lower() if isinstance(form[0],str) else ''
        if head=='quote':return
        if head=='if':assert len(form) in (3,4),(path.name,'IF con argumentos incorrectos',form[:2],len(form))
        if head=='setq':assert len(form)>=3 and len(form)%2==1,(path.name,'SETQ incompleto')
        if head=='defun':
            assert len(form)>=4 and isinstance(form[2],list),(path.name,'DEFUN invalido')
            count+=1
        for child in form[1:]:visit(child)
    for form in forms:visit(form)
    return {'archivo':path.name,'expresiones':len(forms),'funciones':count,'estado':'analisis estatico; no ejecutado en AutoCAD'}


def comprobar_dxf(path):
    doc=ezdxf.readfile(path)
    audit=doc.audit()
    assert not audit.errors and not audit.fixes,(str(path),'auditoria',audit.errors,audit.fixes)
    missing=[]
    for e in doc.entitydb.values():
        if not e.is_alive:continue
        if e.dxf.is_supported('layer') and e.dxf.layer not in doc.layers:missing.append(('CAPA',e.dxf.layer))
        if e.dxftype()=='INSERT':
            assert e.dxf.name in doc.blocks,('Bloque ausente',e.dxf.name)
            definitions=[a.dxf.tag for a in doc.blocks[e.dxf.name].attdefs()]
            actual=[a.dxf.tag for a in e.attribs]
            assert len(actual)==len(set(actual)),('Atributos duplicados',e.dxf.name)
            assert set(actual)==set(definitions),('Atributos faltantes',e.dxf.name,set(actual)^set(definitions))
        if e.dxf.is_supported('linetype'):
            name=e.dxf.get('linetype','BYLAYER')
            if name.upper() not in ('BYLAYER','BYBLOCK'):assert name in doc.linetypes,('Tipo de linea ausente',name)
    assert not missing,(str(path),'referencias de capas ausentes',missing)
    for lt in doc.linetypes:
        if not lt.pattern_tags:continue
        tags=lt.pattern_tags.tags
        lengths=[t.value for t in tags if t.code==49]
        total=next((t.value for t in tags if t.code==40),0)
        if lengths:assert isclose(sum(abs(v) for v in lengths),total,rel_tol=1e-8),('Longitud de patron',lt.dxf.name)
        for t in tags:
            if t.code==340:assert t.value in doc.entitydb and doc.entitydb[t.value].dxftype()=='STYLE',('Estilo de linea ausente',lt.dxf.name)
    return doc,{'archivo':str(path.relative_to(ROOT)),'entidades_modelo':len(doc.modelspace()),
                'bloques':len(doc.blocks),'capas':len(doc.layers),'errores':0,'reparaciones':0}


def probar_escalas(master,specs):
    from generar import nuevo, texto
    d=nuevo();names=['IE_L03','IE_TN_M040','IC_DATA_DOBLE','DACI_HUMO']
    imp=Importer(master,d);imp.import_blocks(names);imp.finalize()
    for i,denom in enumerate((50,75,100)):
        fac=denom/1000
        ox=i*60
        d.modelspace().add_text(f'PRUEBA DE IMPRESION 1:{denom}',dxfattribs={
            'insert':(ox+15*fac,277*fac),'height':5*fac,'style':'EI_TEXTO'})
        for col,angle in enumerate((0,90,180,270)):
            x=20+col*98
            d.modelspace().add_text(f'Giro {angle} grados',dxfattribs={
                'insert':(ox+x*fac,255*fac),'height':3*fac,'style':'EI_TEXTO'})
            for row,name in enumerate(names):
                spec=next(s for s in specs if s.nombre==name)
                pt=(ox+x*fac,(220-row*53)*fac)
                ins=d.modelspace().add_blockref(name,pt,dxfattribs={'layer':spec.capa,
                    'xscale':fac,'yscale':fac,'zscale':fac,'rotation':angle})
                vals=spec.atributos();vals['CODIGO']=f'{spec.codigo}-{col+1}'
                ins.add_auto_attribs(vals)
                defs={a.dxf.tag:a for a in d.blocks[name].attdefs()}
                for a in ins.attribs:
                    off=defs[a.dxf.tag].dxf.insert
                    a.dxf.insert=(pt[0]+off.x*fac,pt[1]+off.y*fac,0)
                    a.dxf.rotation=0
                    assert isclose(a.dxf.height/fac,2.5,rel_tol=1e-8)
                d.modelspace().add_text(name,dxfattribs={'insert':(pt[0]-5*fac,pt[1]-13*fac),
                    'height':2.5*fac,'style':'EI_TEXTO'})
        lay=d.layouts.new(f'ESCALA_{denom:03d}')
        lay.page_setup(size=(420,297),margins=(0,0,0,0),units='mm')
        lay.add_viewport(center=(210,148.5),size=(420,297),
            view_center_point=(ox+210*fac,148.5*fac),view_height=297*fac,status=2,
            dxfattribs={'layer':'VIEWPORTS','flags':16384})
        for vp in lay.query('VIEWPORT'):vp.dxf.layer='VIEWPORTS'
    if 'Layout1' in d.layouts:d.layouts.delete('Layout1')
    dest=ROOT/'07_PRUEBAS'/'PRUEBA_ESCALAS_ROTACIONES.dxf'
    d.saveas(dest)
    comprobar_dxf(dest)
    return {'escalas':[50,75,100],'giros':[0,90,180,270],
            'referencias':48,'altura_texto_impresa_mm':2.5,
            'estado':'geometria DXF comprobada; interaccion EIGIRA pendiente de AutoCAD'}


def main():
    specs=catalogo();log={}
    log['dxf']=[]
    mainpath=ROOT/'11_PLANTILLA_GENERAL_INTEGRADA'/'PLANTILLA_GENERAL_INTEGRADA.dxf'
    master=None
    paths=[mainpath, ROOT/'01_PLANTILLA_MAESTRA'/'BASE_IE_CORREGIDA.dxf',
           ROOT/'02_BIBLIOTECA_BLOQUES'/'BIBLIOTECA_ELECTRICIDAD.dxf',
           ROOT/'09_DATA_COMUNICACIONES'/'BIBLIOTECA_COMUNICACIONES.dxf',
           ROOT/'10_ALARMA_CONTRAINCENDIOS'/'BIBLIOTECA_DACI.dxf']
    for path in paths:
        doc,item=comprobar_dxf(path);log['dxf'].append(item)
        if path==mainpath:master=doc
    assert master.header['$INSUNITS']==6
    assert len(master.layouts)==8,('Layouts',list(master.layout_names()))
    for s in specs:
        assert s.nombre in master.blocks
        b=master.blocks[s.nombre]
        assert tuple(b.base_point)==(0,0,0) and b.block_record.dxf.units==0
        attrs={a.dxf.tag:a for a in b.attdefs()}
        assert set(attrs)==set(s.atributos())
        assert all(not a.is_const for a in attrs.values()),('Atributo constante',s.nombre)
        assert all(isclose(a.dxf.height,2.5) for a in attrs.values())
        if s.forma.startswith('caja'):
            outlines=list(b.query('LWPOLYLINE'))
            assert len(outlines)==2 and not list(b.query('CIRCLE'))
            for poly in outlines:
                pts=list(poly.get_points('xy'))
                assert poly.closed and len(pts)==4
                assert len({round(float(p[0]),5) for p in pts})==2
                assert len({round(float(p[1]),5) for p in pts})==2
            assert -4<attrs['CODIGO'].dxf.insert.x<4
        if s.forma.startswith('toma_'):
            assert len(list(b.query('LINE')))>=6,('Puesta a tierra incompleta',s.nombre)
            assert s.atributos()['CONFIGURACION']=='2P+T'
        refs=[i for i in master.modelspace().query('INSERT') if i.dxf.name==s.nombre]
        assert len(refs)==1
        assert {a.dxf.tag:a.dxf.text for a in refs[0].attribs}==s.atributos()
    from ezdxf.tools.text_size import text_size
    for t in master.modelspace().query('TEXT'):
        if isclose(t.dxf.height,.13):
            assert text_size(t).width/.05<88,('Descripcion invade la siguiente celda',t.dxf.text)
    log['biblioteca']={'bloques_nuevos':len(specs),'bloques_heredados_JY':len([b for b in master.blocks if b.name.startswith('JY_')]),
                       'por_sistema':dict(Counter(s.sistema for s in specs)),
                       'cajas_rectangulares':len([s for s in specs if s.forma.startswith('caja')]),
                       'luminarias':4,'luminarias_pendientes':9}
    log['autolisp']=[check_lisp(p) for p in (ROOT/'04_AUTOLISP').glob('*.lsp')]
    assert any(v['archivo']=='ELECTRICAS.lsp' for v in log['autolisp'])
    for unit in ('METROS','MILIMETROS'):
        lines=(ROOT/'03_TIPOS_LINEA'/f'EIC_{unit}.lin').read_text().splitlines()
        defs=[line for line in lines if line.startswith('A,')]
        assert len(defs)==len(rutas())
        for line in defs:assert lin_compiler(line)
    log['tipos_linea']={'definiciones_por_unidad':len(rutas()),'unidades':['m','mm'],'compilacion':'correcta'}
    ctb=acadctb.load(ROOT/'03_TIPOS_LINEA'/'ELECTRICAS_MONO.ctb')
    assert all(ctb[i].color==(0,0,0) for i in range(1,256))
    log['ctb']={'colores_aci_negros':255,'lectura_binaria':'correcta'}
    log['escalas']=probar_escalas(master,specs)
    mm=ROOT/'07_PRUEBAS'/'PRUEBA_CONVERSION_MM.dxf'
    volver=ROOT/'07_PRUEBAS'/'PRUEBA_RETORNO_METROS.dxf'
    convertir(mainpath,mm,'mm');converted,_=comprobar_dxf(mm)
    original=list(master.modelspace().query('INSERT'))[0]
    other=converted.entitydb[original.dxf.handle]
    assert isclose(other.dxf.xscale,original.dxf.xscale*1000)
    assert isclose(other.attribs[0].dxf.height,original.attribs[0].dxf.height*1000)
    convertir(mm,volver,'m');returned,_=comprobar_dxf(volver)
    assert isclose(returned.entitydb[original.dxf.handle].dxf.xscale,original.dxf.xscale)
    for a,b in zip(master.modelspace(),returned.modelspace()):
        if a.dxf.is_supported('insert') and a.dxf.hasattr('insert'):
            assert a.dxf.insert.isclose(b.dxf.insert),('Retorno de coordenadas',a.dxf.handle)
    log['conversion']={'metros_a_mm':1000,'mm_a_m':.001,'retorno_coordenadas':'correcto','retorno_atributos':'correcto'}
    import fitz
    log['pdf']=[]
    for name in ('CATALOGO_INTEGRADO.pdf','CATALOGO_MONOCROMO.pdf'):
        path=ROOT/'05_CATALOGOS'/name
        if path.exists():
            with fitz.open(path) as pdf:
                assert len(pdf)==7
                for page in pdf:
                    assert abs(page.rect.width/72*25.4-420)<.1
                    pix=page.get_pixmap(matrix=fitz.Matrix(.25,.25),colorspace=fitz.csGRAY)
                    assert sum(v<240 for v in pix.samples)>100,('Pagina vacia',name,page.number)
                log['pdf'].append({'archivo':name,'paginas':len(pdf),'formato':'A3','paginas_no_vacias':True})
    log['pendientes']=['Apertura y ploteo en AutoCAD','Ejecucion real de rutinas AutoLISP y panel DCL',
                      'Verificacion normativa con fuentes originales y proyecto',
                      'Identificacion de 9 luminarias del registro no aportado',
                      'DWG/DWT y dinamicos nativos: no generados']
    log['resultado']='CORRECTO EN LAS PRUEBAS EJECUTADAS; pendientes detallados por separado'
    (ROOT/'07_PRUEBAS'/'RESULTADOS.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(log,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
