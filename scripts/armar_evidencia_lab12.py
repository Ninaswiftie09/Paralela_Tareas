"""Arma evidencia_lab12.pdf (entregable) con las capturas de los dos equipos y las 7 gráficas.

Uso (desde la raíz del repo, en Windows o WSL):
    python scripts/armar_evidencia_lab12.py

Las capturas de Partes 1 y 4 (Nina) se leen de evidencia/nina/ con estos nombres:
    nina_01_equipo.png       datos del CPU (núcleos físicos/lógicos, HT)
    nina_02_make.png         compilación
    nina_03_amdahl*.png      ejecución de amdahl (una o varias capturas, se ordenan por nombre)
    nina_04_gustafson*.png   ejecución de gustafson
Si falta alguna, el PDF se genera igual con un recuadro "PENDIENTE" en su lugar y el script
lo avisa al final. Las capturas de Partes 2 y 3 (Luis) están en parte2_3/evidencia/.
Requiere: Pillow (viene con matplotlib).
"""
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
NINA = ROOT / 'evidencia' / 'nina'
LUIS = ROOT / 'parte2_3' / 'evidencia'
RES = ROOT / 'results'
SALIDA = ROOT / 'evidencia_lab12.pdf'

PAGINA = (1240, 1754)  # A4 a 150 dpi
MARGEN = 80
TINTA, GRIS, BORDE, PENDIENTE = '#0b0b0b', '#52514e', '#c3c2b7', '#b3261e'


def fuente(tam, negrita=False):
    nombres = (['DejaVuSans-Bold.ttf', 'arialbd.ttf', 'segoeuib.ttf'] if negrita
               else ['DejaVuSans.ttf', 'arial.ttf', 'segoeui.ttf'])
    carpetas = ['/usr/share/fonts/truetype/dejavu', 'C:/Windows/Fonts', '']
    for n in nombres:
        for c in carpetas:
            try:
                return ImageFont.truetype(str(Path(c) / n) if c else n, tam)
            except OSError:
                pass
    return ImageFont.load_default()


F_PORTADA, F_SECCION, F_TITULO, F_TEXTO = fuente(44, True), fuente(34, True), fuente(26, True), fuente(21)


def capturas_nina(patron):
    # amdahl: de fp100 a fp50 (por número, de mayor a menor), no en orden alfabético
    def clave(p):
        digitos = ''.join(c for c in p.stem.split('_')[-1] if c.isdigit())
        return (-int(digitos) if digitos else 0, p.name)
    return sorted(NINA.glob(patron), key=clave) if NINA.is_dir() else []


# Cada elemento: (sección, título, ruta o None si falta, nota, nombre esperado si falta)
def contenido():
    items = []

    def agregar(seccion, titulo, rutas, nota='', esperado=''):
        if rutas:
            for r in rutas:
                sufijo = f' — {r.stem.split("_")[-1]}' if len(rutas) > 1 else ''
                items.append((seccion, titulo + sufijo, r, nota, ''))
        else:
            items.append((seccion, titulo, None, nota, esperado))

    s = '1. Datos de los equipos'
    agregar(s, 'Nina — Partes 1 y 4 (i7-1165G7, Windows nativo)', capturas_nina('nina_01_equipo*.png'),
            'Datos del CPU: núcleos físicos y lógicos, Hyper-Threading.', 'evidencia/nina/nina_01_equipo.png')
    agregar(s, 'Luis — Partes 2 y 3 (lscpu en WSL2)', [LUIS / '01_lscpu.png'],
            'WSL2 muestra 6 núcleos × 2 hilos: es la vista virtualizada de Hyper-V.')
    agregar(s, 'Luis — Partes 2 y 3 (Windows)', [LUIS / '01b_cpu_windows.png'],
            'Vista real del i5-12450H: 8 núcleos físicos (4 P con HT + 4 E), 12 hilos lógicos.')

    s = '2. Compilación'
    agregar(s, 'Nina — compilación', capturas_nina('nina_02_make*.png'), '',
            'evidencia/nina/nina_02_make.png')
    agregar(s, 'Luis — make', [LUIS / '02_make.png'])

    s = '3. Ejecución de los 4 modos'
    agregar(s, 'amdahl (Parte 1, Nina)', capturas_nina('nina_03_amdahl*.png'),
            'Ejecución en el equipo de Nina; los CSV oficiales (results/) son de la corrida original.',
            'evidencia/nina/nina_03_amdahl*.png')
    agregar(s, 'suma (Parte 2, Luis)', [LUIS / '04_suma.png'])
    for k in ('static', 'dynamic', 'guided'):
        agregar(s, f'desbalance {k} (Parte 3, Luis)', [LUIS / f'05_desb_{k}.png'])
    agregar(s, 'gustafson (Parte 4, Nina)', capturas_nina('nina_04_gustafson*.png'),
            'Ejecución en el equipo de Nina; los CSV oficiales (results/) son de la corrida original.',
            'evidencia/nina/nina_04_gustafson*.png')
    agregar(s, 'amdahl fp = 1.00 en el equipo de Luis (solo para la pregunta 2a)', [LUIS / '03_amdahl_fp100.png'],
            'No es el CSV oficial de la Parte 1: se usa para comparar Ts con Tp(p=1) en el mismo equipo que la suma.')

    s = '4. Gráficas de graficar.py'
    for nombre in ('amdahl_speedup', 'amdahl_eficiencia', 'suma_speedup', 'desbalance_speedup',
                   'desbalance_eficiencia', 'gustafson_speedup', 'gustafson_eficiencia'):
        ruta = RES / f'{nombre}.png'
        agregar(s, f'{nombre}.png', [ruta] if ruta.is_file() else [], '', f'results/{nombre}.png')

    s = 'Anexo — Reto opcional (S > p)'
    agregar(s, '5 corridas del lab12_speedup.c modificado (parte2_3/reto/)', [LUIS / '08_reto_5corridas.png'],
            'N = 262 144 doubles (2 MB): S > p con p = 2 y p = 4 en las 5 corridas.')
    agregar(s, 'Eficiencia del reto (mediana de 5 corridas)', [ROOT / 'parte2_3' / 'extra_reto_superlineal.png'])
    return items


def main():
    items = contenido()
    faltan = [it for it in items if it[2] is None]
    paginas = []
    ancho_util = PAGINA[0] - 2 * MARGEN

    # Portada
    p = Image.new('RGB', PAGINA, 'white')
    d = ImageDraw.Draw(p)
    y = 300
    d.text((MARGEN, y), 'Lab 12 — Speedup y eficiencia', font=F_PORTADA, fill=TINTA)
    y += 70
    d.text((MARGEN, y), 'Evidencia', font=F_SECCION, fill=GRIS)
    y += 90
    for linea in ['Computación Paralela y Distribuida (CC3069)',
                  'Nina Nájera Marakovits — 231088 (Partes 1 y 4)',
                  'Luis Palacios (Partes 2, 3 y reto)',
                  date.today().isoformat()]:
        d.text((MARGEN, y), linea, font=F_TEXTO, fill=TINTA)
        y += 38
    y += 60
    d.text((MARGEN, y), 'Contenido', font=F_TITULO, fill=TINTA)
    y += 50
    for seccion in dict.fromkeys(it[0] for it in items):
        n_falta = sum(1 for it in faltan if it[0] == seccion)
        estado = f'   (faltan {n_falta})' if n_falta else ''
        d.text((MARGEN + 20, y), seccion + estado, font=F_TEXTO, fill=PENDIENTE if n_falta else TINTA)
        y += 36
    paginas.append(p)

    # Contenido
    pagina, y, seccion_actual = None, 0, None

    def nueva():
        nonlocal pagina, y
        pagina = Image.new('RGB', PAGINA, 'white')
        paginas.append(pagina)
        y = MARGEN

    nueva()
    for seccion, titulo, ruta, nota, esperado in items:
        if ruta is not None:
            img = Image.open(ruta).convert('RGB')
            escala = min(ancho_util / img.width, 1.4)
            img = img.resize((int(img.width * escala), int(img.height * escala)))
            alto_img = img.height
        else:
            img, alto_img = None, 160
        alto = (60 if seccion != seccion_actual else 0) + 45 + (34 if nota else 0) + alto_img + 50
        if y + alto > PAGINA[1] - MARGEN and y > MARGEN:
            nueva()
        d = ImageDraw.Draw(pagina)
        if seccion != seccion_actual:
            d.text((MARGEN, y), seccion, font=F_SECCION, fill=TINTA)
            y += 60
            seccion_actual = seccion
        d.text((MARGEN, y), titulo, font=F_TITULO, fill=TINTA)
        y += 45
        if nota:
            d.text((MARGEN, y), nota, font=F_TEXTO, fill=GRIS)
            y += 34
        if img is not None:
            pagina.paste(img, (MARGEN, y))
            d.rectangle([MARGEN - 1, y - 1, MARGEN + img.width, y + img.height], outline=BORDE)
        else:
            d.rectangle([MARGEN, y, MARGEN + ancho_util, y + alto_img], outline=PENDIENTE, width=3)
            d.text((MARGEN + 30, y + 45), 'PENDIENTE — falta la captura', font=F_TITULO, fill=PENDIENTE)
            d.text((MARGEN + 30, y + 95), f'Guardarla como: {esperado}', font=F_TEXTO, fill=PENDIENTE)
        y += alto_img + 50

    for i, pg in enumerate(paginas[1:], start=2):
        ImageDraw.Draw(pg).text((PAGINA[0] - MARGEN - 60, PAGINA[1] - 50), f'{i}', font=F_TEXTO, fill=GRIS)
    paginas[0].save(SALIDA, save_all=True, append_images=paginas[1:], resolution=150)
    print(f'{SALIDA.name}: {len(paginas)} paginas')
    if faltan:
        print(f'Faltan {len(faltan)} capturas (aparecen como PENDIENTE en el PDF):')
        for it in faltan:
            print('  -', it[4])


if __name__ == '__main__':
    main()
