

from PIL import Image ,ImageDraw ,ImageFont 

PAGINA =(1240 ,1754 )
MARGEN =70 
FUENTE ="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FUENTE_B ="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

secciones =[
("Datos del equipo (WSL2: lscpu)","evidencia/01_lscpu.png",
"Dentro de WSL2 lscpu muestra 6 núcleos × 2 hilos: es la vista virtualizada de Hyper-V."),
("Datos del equipo (Windows)","evidencia/01b_cpu_windows.png",
"Vista real: 8 núcleos físicos (4 P con HT + 4 E), 12 hilos lógicos."),
("Compilación (make)","evidencia/02_make.png",""),
("Parte 2a: amdahl fp = 1.00 (para el Ts honesto)","evidencia/03_amdahl_fp100.png",""),
("Parte 2b: ./lab12 suma","evidencia/04_suma.png",""),
("Parte 3: ./lab12 desbalance static","evidencia/05_desb_static.png",""),
("Parte 3: ./lab12 desbalance dynamic","evidencia/05_desb_dynamic.png",""),
("Parte 3: ./lab12 desbalance guided","evidencia/05_desb_guided.png",""),
("Gráfica: suma_speedup.png (graficar.py)","../results/suma_speedup.png",""),
("Gráfica: desbalance_speedup.png (graficar.py)","../results/desbalance_speedup.png",""),
("Gráfica: desbalance_eficiencia.png (graficar.py)","../results/desbalance_eficiencia.png",""),
("Extra: desbalance, mediana de 6 corridas","extra_desbalance_variabilidad.png",""),
("Extra: umbral de N para la suma (pregunta 2.6)","extra_suma_umbral.png",""),
("Reto: 5 corridas del lab12_speedup.c modificado","evidencia/08_reto_5corridas.png",""),
("Reto: eficiencia > 1 (S > p)","extra_reto_superlineal.png",""),
]

f_tit =ImageFont .truetype (FUENTE_B ,30 )
f_txt =ImageFont .truetype (FUENTE ,22 )
ancho_util =PAGINA [0 ]-2 *MARGEN 

paginas ,pagina ,y =[],None ,0 


def nueva ():
    global pagina ,y 
    pagina =Image .new ("RGB",PAGINA ,"white")
    paginas .append (pagina )
    y =MARGEN 


nueva ()
for titulo ,archivo ,nota in secciones :
    img =Image .open (archivo ).convert ("RGB")
    escala =min (1.0 ,ancho_util /img .width )if img .width >ancho_util else min (1.4 ,ancho_util /img .width )
    img =img .resize ((int (img .width *escala ),int (img .height *escala )))
    alto =50 +(35 if nota else 0 )+img .height +50 
    if y +alto >PAGINA [1 ]-MARGEN :
        nueva ()
    d =ImageDraw .Draw (pagina )
    d .text ((MARGEN ,y ),titulo ,font =f_tit ,fill ="#0b0b0b")
    y +=50 
    if nota :
        d .text ((MARGEN ,y ),nota ,font =f_txt ,fill ="#52514e")
        y +=35 
    pagina .paste (img ,(MARGEN ,y ))
    d .rectangle ([MARGEN -1 ,y -1 ,MARGEN +img .width ,y +img .height ],outline ="#c3c2b7")
    y +=img .height +50 

paginas [0 ].save ("evidencia_parte2_3.pdf",save_all =True ,append_images =paginas [1 :],resolution =150 )
print (f"  -> evidencia_parte2_3.pdf ({len (paginas )} páginas)")
