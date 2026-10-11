"""Arma entrega/ con los 4 archivos que pide el laboratorio:

    reporte_lab12.pdf       copia de docs/Laboratorio_Speed_Up_Paralela.pdf
    evidencia_lab12.pdf     scripts/armar_evidencia_lab12.py (capturas de los dos equipos + 7 gráficas)
    resultados_lab12.zip    scripts/armar_resultados_zip.py (10 CSV + *_con_S_E.csv y demás resultados)
    lab12_speedup.c         reto: docs/reto/lab12_speedup.c, la versión medida, con sus comentarios

Uso (desde la raíz del repo):  python scripts/armar_entrega.py
Si faltan capturas de evidencia, igual arma todo pero termina con error y dice cuáles faltan.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ENTREGA = ROOT / 'entrega'
ENTREGA.mkdir(exist_ok=True)

evidencia = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'armar_evidencia_lab12.py')],
                           cwd=ROOT, capture_output=True, text=True, check=True)
print(evidencia.stdout.strip())
subprocess.run([sys.executable, str(ROOT / 'scripts' / 'armar_resultados_zip.py')], cwd=ROOT, check=True)

shutil.copy2(ROOT / 'docs' / 'Laboratorio_Speed_Up_Paralela.pdf', ENTREGA / 'reporte_lab12.pdf')
shutil.move(str(ROOT / 'evidencia_lab12.pdf'), ENTREGA / 'evidencia_lab12.pdf')
shutil.move(str(ROOT / 'resultados_lab12.zip'), ENTREGA / 'resultados_lab12.zip')
shutil.copy2(ROOT / 'docs' / 'reto' / 'lab12_speedup.c', ENTREGA / 'lab12_speedup.c')

# Comprobaciones de lo que pide la entrega
problemas = []
nombres = zipfile.ZipFile(ENTREGA / 'resultados_lab12.zip').namelist()
originales = [f'results/amdahl_fp{fp}.csv' for fp in (100, 95, 90, 75, 50)] + \
             [f'results/{n}.csv' for n in ('suma', 'desb_static', 'desb_dynamic', 'desb_guided', 'gustafson')]
con_s_e = [n for n in nombres if n.startswith('results/') and n.endswith('_con_S_E.csv')]
problemas += [f'falta en el zip: {n}' for n in originales if n not in nombres]
if len(con_s_e) != 4:
    problemas.append(f'el zip tiene {len(con_s_e)} *_con_S_E.csv (se esperaban 4)')
reto = (ENTREGA / 'lab12_speedup.c').read_text(encoding='utf-8')
if 'RETO' not in reto or '/*' not in reto:
    problemas.append('lab12_speedup.c del reto no tiene los comentarios que explican los cambios')
if 'PENDIENTE' in evidencia.stdout or 'Faltan' in evidencia.stdout:
    problemas.append('evidencia_lab12.pdf tiene capturas PENDIENTES (ver arriba)')

print()
for f in sorted(ENTREGA.iterdir()):
    print(f'  entrega/{f.name:24s} {f.stat().st_size / 1024:8.0f} KB')
if problemas:
    print('\nNO está listo para entregar:')
    for p in problemas:
        print('  -', p)
    sys.exit(1)
print('\nListo para entregar: los 4 archivos están en entrega/')
