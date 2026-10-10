#include <stdio.h>
#include <omp.h>

int main() {

    // No permitir que OpenMP reduzca
    // automáticamente la cantidad de hilos
    omp_set_dynamic(0);

    // Permitir 2 niveles activos
    omp_set_max_active_levels(2);

    // Activar explícitamente paralelismo anidado.
    // Esta función es antigua, pero nos sirve
    // para probar este runtime de TDM-GCC.
    omp_set_nested(1);

    #pragma omp parallel num_threads(4)
    {
        int thread_id = omp_get_thread_num();

        printf("Nivel 1 - Hilo %d\n", thread_id);

        #pragma omp parallel num_threads(2)
        {
            int nested_thread_id = omp_get_thread_num();

            printf(
                "Nivel 2 - Hilo %d.%d | equipo interno = %d\n",
                thread_id,
                nested_thread_id,
                omp_get_num_threads()
            );
        }
    }

    return 0;
}


// salida en la terminal.
// PS C:\Users\ninan\OneDrive\Documentos\Escritorio\UVG\VIII SEMESTRE\Computación Paralela\Paralela_Tareas> gcc ejercicio1.c -fopenmp -o ejercicio1.exe
// PS C:\Users\ninan\OneDrive\Documentos\Escritorio\UVG\VIII SEMESTRE\Computación Paralela\Paralela_Tareas> ./ejercicio1                               
// Nivel 1 - Hilo 3
// Nivel 1 - Hilo 1
// Nivel 1 - Hilo 0
// Nivel 1 - Hilo 2
// Nivel 2 - Hilo 3.1 | equipo interno = 2
// Nivel 2 - Hilo 3.0 | equipo interno = 2
// Nivel 2 - Hilo 1.0 | equipo interno = 2
// Nivel 2 - Hilo 1.1 | equipo interno = 2
// Nivel 2 - Hilo 0.0 | equipo interno = 2
// Nivel 2 - Hilo 0.1 | equipo interno = 2
// Nivel 2 - Hilo 2.0 | equipo interno = 2
// Nivel 2 - Hilo 2.1 | equipo interno = 2