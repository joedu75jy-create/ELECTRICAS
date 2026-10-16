"""Correcciones verificables del ZIP aportado. No ejecuta el AutoLISP recibido."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json
import re
import ezdxf

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['01_PLANTILLA_MAESTRA', '02_BIBLIOTECA_BLOQUES', '03_TIPOS_LINEA',
         '04_AUTOLISP', '05_CATALOGOS', '06_CODIGO_FUENTE', '07_PRUEBAS',
         '08_ENTREGA_FINAL', '09_DATA_COMUNICACIONES', '10_ALARMA_CONTRAINCENDIOS',
         '11_PLANTILLA_GENERAL_INTEGRADA']


def main():
    for name in NAMES:
        (ROOT / name).mkdir(parents=True, exist_ok=True)
    ref = ROOT / '06_CODIGO_FUENTE' / 'referencias'
    zippath = ref / 'PLANTILLA_IE_ORIGINAL.zip'
    with ZipFile(zippath) as z:
        original = z.read('PLANTILLA_IE.dxf').decode('utf-8')
        lsp = z.read('JY_CONTROLES.lsp').decode('utf-8')
        lin = z.read('TUBERIAS_TEXTUALES.lin')
    import io
    doc = ezdxf.read(io.StringIO(original))
    doc.layers.new('VIEWPORTS', dxfattribs={'color': 8, 'plot': 0})
    changed_text = 0
    for b in doc.blocks:
        if b.name.startswith(('JY_TN_', 'JY_TE_')):
            for e in b.query('TEXT'):
                if e.dxf.height < .125:
                    e.dxf.height = .125
                    changed_text += 1
    defaults = {}
    for ins in doc.modelspace().query('INSERT'):
        defaults[ins.dxf.name] = {a.dxf.tag: a.dxf.text for a in ins.attribs}
    for name, attrs in defaults.items():
        if not name.startswith(('JY_TN_', 'JY_TE_')):
            continue
        extra = ''.join(f' ("{tag}" . "{attrs.get(tag, "")}")' for tag in ('SISTEMA', 'MONTAJE', 'DGE'))
        pattern = r'(\("' + re.escape(name) + r'"[^\n]*?\(\("TIPO"[^\n]*?\("ALTURA"\s*\.\s*"[^"]*"\))'
        lsp, count = re.subn(pattern, lambda m: m.group(1) + extra, lsp)
        if count != 1:
            raise RuntimeError(f'Entrada AutoLISP no encontrada una vez: {name} ({count})')
    lsp = '; Base corregida; conserva la dependencia Windows/ActiveX. Pendiente de prueba real en AutoCAD.\n' + lsp
    path = ROOT / '01_PLANTILLA_MAESTRA' / 'BASE_IE_CORREGIDA.dxf'
    doc.saveas(path)
    (ROOT / '04_AUTOLISP' / 'JY_CONTROLES_CORREGIDO.lsp').write_text(lsp, encoding='utf-8')
    (ROOT / '03_TIPOS_LINEA' / 'TUBERIAS_BASE_METROS.lin').write_bytes(lin)
    reopened = ezdxf.readfile(path)
    audit = reopened.audit()
    assert not audit.errors and not audit.fixes
    for ent in reopened.entitydb.values():
        if ent.is_alive and ent.dxf.is_supported('layer'):
            assert ent.dxf.layer in reopened.layers, ent.dxf.layer
    result = {'estado': 'base corregida, ampliacion integrada en desarrollo',
              'errores_auditoria': len(audit.errors), 'reparaciones_auditoria': len(audit.fixes),
              'distintivos_ampliados': changed_text, 'entradas_lisp_corregidas': 14,
              'unidades': 'metros', 'escala_base': '1:50',
              'AutoCAD': 'no disponible; AutoLISP no ejecutado',
              'pendientes': ['integracion de las tres especialidades', 'registro de las 13 luminarias',
                             'verificacion grafica normativa de simbolos', 'prueba en AutoCAD']}
    (ROOT / '07_PRUEBAS' / 'BASE_CORREGIDA.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    readme = ('BASE CORREGIDA - PRIMER RESPALDO\n\n'
              'Abra BASE_IE_CORREGIDA.dxf. Unidades: metros. Escala prevista: 1:50.\n'
              'APPLOAD: JY_CONTROLES_CORREGIDO.lsp (Windows/ActiveX; pendiente de probar en AutoCAD).\n'
              'Se corrigio la capa de ventanas graficas y los metadatos SISTEMA/MONTAJE al insertar.\n'
              'La integracion ampliada se encuentra en desarrollo. No es la entrega final.\n'
              'No contiene bloques dinamicos nativos.\n')
    files = {path.name: path, 'JY_CONTROLES_CORREGIDO.lsp': ROOT / '04_AUTOLISP' / 'JY_CONTROLES_CORREGIDO.lsp',
             'TUBERIAS_BASE_METROS.lin': ROOT / '03_TIPOS_LINEA' / 'TUBERIAS_BASE_METROS.lin',
             'PRUEBAS.json': ROOT / '07_PRUEBAS' / 'BASE_CORREGIDA.json',
             '06_CODIGO_FUENTE/corregir_base.py': Path(__file__), '06_CODIGO_FUENTE/referencias/PLANTILLA_IE_ORIGINAL.zip': zippath}
    package = ROOT / '08_ENTREGA_FINAL' / 'ELECTRICAS_PRIMER_RESPALDO.zip'
    with ZipFile(package, 'w', ZIP_DEFLATED) as z:
        for name, src in files.items():
            z.write(src, name)
        z.writestr('LEEME.txt', readme)
    print(json.dumps(result, ensure_ascii=False))
    print(package)


if __name__ == '__main__':
    main()
