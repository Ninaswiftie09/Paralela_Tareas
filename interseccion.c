#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

#ifdef _WIN32
    #include <windows.h>
#else
    #include <unistd.h>
#endif

#define MAX_VEHICLES 100
#define NUM_LIGHTS 4


// ==========================================
// PROTOTIPOS
// ==========================================

// Se declara aquí porque simulate_traffic()
// utiliza esta función antes de su definición.
void adjust_threads(int num_vehicles);


// ==========================================
// PASO 1: ESTRUCTURAS DE DATOS
// ==========================================

// Estructura de un vehículo
typedef struct {

    int id;
    // Identificador único del carro

    int position;
    // Posición actual del carro

} Vehicle;


// Estructura de un semáforo
typedef struct {

    int state;
    // 0 = rojo
    // 1 = verde
    // 2 = amarillo

    int timer;
    // Tiempo que falta antes de cambiar de estado

} TrafficLight;


// Estructura de una intersección
typedef struct {

    Vehicle vehicles[MAX_VEHICLES];
    // Arreglo de carros

    int vehicle_count;
    // Cantidad actual de carros

    TrafficLight lights[NUM_LIGHTS];
    // Arreglo de los 4 semáforos

    int id;
    // Identificador de la intersección

} Intersection;



// ==========================================
// PASO 2: INICIALIZAR DATOS
// ==========================================

// Inicializa todos los vehículos
void initialize_vehicles(
    Vehicle *vehicles,
    int num_vehicles
) {

    for (int i = 0; i < num_vehicles; i++) {

        // Cada carro recibe un ID diferente
        vehicles[i].id = i;

        // Todos empiezan en posición 0
        vehicles[i].position = 0;
    }
}


// Inicializa todos los semáforos
void initialize_traffic_lights(
    TrafficLight *lights,
    int num_lights
) {

    for (int i = 0; i < num_lights; i++) {

        // Todos empiezan en rojo
        lights[i].state = 0;

        // Timer aleatorio entre 1 y 10
        lights[i].timer = rand() % 10 + 1;
    }
}



// ==========================================
// PASO 3: ACTUALIZAR LOS SEMÁFOROS
// ==========================================

void update_traffic_lights(
    TrafficLight *lights,
    int num_lights
) {

    // OpenMP reparte los semáforos
    // entre varios hilos.
    #pragma omp parallel for
    for (int i = 0; i < num_lights; i++) {

        // Pasa una unidad de tiempo
        lights[i].timer--;


        // Si el timer llega a 0,
        // el semáforo cambia de estado.
        if (lights[i].timer <= 0) {

            // Los estados cambian así:
            //
            // 0 rojo
            //   ↓
            // 1 verde
            //   ↓
            // 2 amarillo
            //   ↓
            // 0 rojo

            lights[i].state =
                (lights[i].state + 1) % 3;


            // Reiniciamos el timer
            lights[i].timer = 5;
        }
    }
}



// ==========================================
// PASO 4: MOVER LOS VEHÍCULOS
// ==========================================

void move_vehicles(
    Vehicle *vehicles,
    int num_vehicles,
    TrafficLight *lights,
    int num_lights
) {

    // OpenMP reparte los vehículos
    // entre varios hilos.
    #pragma omp parallel for
    for (int i = 0; i < num_vehicles; i++) {

        // Asignamos un semáforo a cada vehículo.
        //
        // carro 0 -> semáforo 0
        // carro 1 -> semáforo 1
        // carro 2 -> semáforo 2
        // carro 3 -> semáforo 3
        // carro 4 -> semáforo 0
        // etc.

        int light_index = i % num_lights;


        // Si el semáforo está verde,
        // el carro avanza.
        if (lights[light_index].state == 1) {

            vehicles[i].position++;
        }


        // Si está rojo o amarillo,
        // simplemente no se mueve.
    }
}



// ==========================================
// PASO 5: SIMULACIÓN DEL TRÁFICO
// ==========================================

void simulate_traffic(
    int num_iterations,
    Vehicle *vehicles,
    int num_vehicles,
    TrafficLight *lights,
    int num_lights
) {

    // Este for controla los ciclos
    // principales de la simulación.
    for (int i = 0; i < num_iterations; i++) {


        // ==================================
        // PASO 6
        // ==================================

        // Antes de cada ciclo ajustamos
        // la cantidad de hilos.
        adjust_threads(num_vehicles);


        // Primero actualizamos los semáforos.
        update_traffic_lights(
            lights,
            num_lights
        );


        // Luego movemos los carros según
        // el estado de los semáforos.
        move_vehicles(
            vehicles,
            num_vehicles,
            lights,
            num_lights
        );


        // Esperamos 1 segundo entre ciclos.
        // Esto es para la simulación normal,
        // NO para las pruebas de rendimiento.

        #ifdef _WIN32
            Sleep(1000);
        #else
            sleep(1);
        #endif
    }
}



// ==========================================
// PASO 6: AJUSTAR DINÁMICAMENTE LOS HILOS
// ==========================================

void adjust_threads(int num_vehicles) {

    // Permitimos que OpenMP pueda
    // ajustar dinámicamente el equipo.
    omp_set_dynamic(1);


    // Si hay pocos carros,
    // solicitamos pocos hilos.
    if (num_vehicles <= 20) {

        omp_set_num_threads(2);
    }


    // Carga media
    else if (num_vehicles <= 50) {

        omp_set_num_threads(4);
    }


    // Carga grande
    else {

        omp_set_num_threads(8);
    }
}



// ==========================================
// PASO 7: PRUEBAS DE RENDIMIENTO
// ==========================================

// mode:
// 0 = secuencial
// 1 = paralelo estático
// 2 = paralelo dinámico

double run_test(
    int mode,
    int num_iterations,
    Vehicle *vehicles,
    int num_vehicles,
    TrafficLight *lights,
    int num_lights
) {

    // Para comparar static vs dynamic de forma
    // controlada, pedimos 4 hilos.
    //
    // Aquí desactivamos el ajuste automático
    // de cantidad de hilos porque queremos
    // comparar el TIPO DE REPARTO.
    if (mode != 0) {

        omp_set_dynamic(0);

        omp_set_num_threads(4);
    }


    // Guardamos el tiempo inicial
    double start = omp_get_wtime();


    // Repetimos la simulación muchas veces
    // para poder medir mejor el tiempo.
    for (int iteration = 0;
         iteration < num_iterations;
         iteration++) {


        // ======================================
        // MODO 0: SECUENCIAL
        // ======================================

        if (mode == 0) {


            // ------------------------------
            // Actualizar semáforos
            // uno por uno
            // ------------------------------

            for (int i = 0; i < num_lights; i++) {

                lights[i].timer--;

                if (lights[i].timer <= 0) {

                    lights[i].state =
                        (lights[i].state + 1) % 3;

                    lights[i].timer = 5;
                }
            }


            // ------------------------------
            // Mover vehículos
            // uno por uno
            // ------------------------------

            for (int i = 0; i < num_vehicles; i++) {

                int light_index =
                    i % num_lights;


                if (lights[light_index].state == 1) {

                    vehicles[i].position++;
                }
            }
        }



        // ======================================
        // MODO 1: PARALELO ESTÁTICO
        // ======================================

        else if (mode == 1) {


            // STATIC:
            // OpenMP reparte el trabajo
            // desde el principio.
            #pragma omp parallel for schedule(static)
            for (int i = 0; i < num_lights; i++) {

                lights[i].timer--;

                if (lights[i].timer <= 0) {

                    lights[i].state =
                        (lights[i].state + 1) % 3;

                    lights[i].timer = 5;
                }
            }


            // También repartimos los carros
            // usando schedule(static).
            #pragma omp parallel for schedule(static)
            for (int i = 0; i < num_vehicles; i++) {

                int light_index =
                    i % num_lights;


                if (lights[light_index].state == 1) {

                    vehicles[i].position++;
                }
            }
        }



        // ======================================
        // MODO 2: PARALELO DINÁMICO
        // ======================================

        else if (mode == 2) {


            // DYNAMIC:
            // los hilos van tomando trabajo
            // conforme terminan sus tareas.
            #pragma omp parallel for schedule(dynamic)
            for (int i = 0; i < num_lights; i++) {

                lights[i].timer--;

                if (lights[i].timer <= 0) {

                    lights[i].state =
                        (lights[i].state + 1) % 3;

                    lights[i].timer = 5;
                }
            }


            // Los carros también se reparten
            // dinámicamente.
            #pragma omp parallel for schedule(dynamic)
            for (int i = 0; i < num_vehicles; i++) {

                int light_index =
                    i % num_lights;


                if (lights[light_index].state == 1) {

                    vehicles[i].position++;
                }
            }
        }
    }


    // Tiempo final
    double end = omp_get_wtime();


    // Devolvemos cuánto tardó
    return end - start;
}



// ==========================================
// FUNCIÓN PARA PROBAR UNA CONFIGURACIÓN
// ==========================================

void test_configuration(
    int num_vehicles,
    int num_iterations,
    unsigned int seed
) {

    Intersection test_intersection;

    test_intersection.id = 1;

    test_intersection.vehicle_count =
        num_vehicles;


    printf(
        "\n====================================\n"
    );

    printf(
        "PRUEBA CON %d VEHICULOS\n",
        num_vehicles
    );

    printf(
        "====================================\n"
    );


    // ======================================
    // PRUEBA 1: SECUENCIAL
    // ======================================

    // Ponemos la misma semilla para que
    // los semáforos comiencen igual.
    srand(seed);


    initialize_vehicles(
        test_intersection.vehicles,
        num_vehicles
    );


    initialize_traffic_lights(
        test_intersection.lights,
        NUM_LIGHTS
    );


    double sequential_time =
        run_test(
            0,
            num_iterations,
            test_intersection.vehicles,
            num_vehicles,
            test_intersection.lights,
            NUM_LIGHTS
        );


    printf(
        "Secuencial:       %.6f segundos\n",
        sequential_time
    );



    // ======================================
    // PRUEBA 2: PARALELO ESTÁTICO
    // ======================================

    // Reiniciamos exactamente los datos.
    srand(seed);


    initialize_vehicles(
        test_intersection.vehicles,
        num_vehicles
    );


    initialize_traffic_lights(
        test_intersection.lights,
        NUM_LIGHTS
    );


    double static_time =
        run_test(
            1,
            num_iterations,
            test_intersection.vehicles,
            num_vehicles,
            test_intersection.lights,
            NUM_LIGHTS
        );


    printf(
        "Paralelo static:  %.6f segundos\n",
        static_time
    );



    // ======================================
    // PRUEBA 3: PARALELO DINÁMICO
    // ======================================

    // Otra vez comenzamos con
    // exactamente los mismos datos.
    srand(seed);


    initialize_vehicles(
        test_intersection.vehicles,
        num_vehicles
    );


    initialize_traffic_lights(
        test_intersection.lights,
        NUM_LIGHTS
    );


    double dynamic_time =
        run_test(
            2,
            num_iterations,
            test_intersection.vehicles,
            num_vehicles,
            test_intersection.lights,
            NUM_LIGHTS
        );


    printf(
        "Paralelo dynamic: %.6f segundos\n",
        dynamic_time
    );
}



// ==========================================
// MAIN
// ==========================================

int main() {

    // ======================================
    // INTERSECCIÓN PRINCIPAL
    // ======================================

    Intersection intersection;


    intersection.id = 1;


    // Cantidad inicial de carros
    intersection.vehicle_count = 10;



    // ======================================
    // PASO 2: INICIALIZACIÓN
    // ======================================

    initialize_vehicles(
        intersection.vehicles,
        intersection.vehicle_count
    );


    initialize_traffic_lights(
        intersection.lights,
        NUM_LIGHTS
    );



    // ======================================
    // PASO 6:
    // AJUSTE INICIAL DE HILOS
    // ======================================

    adjust_threads(
        intersection.vehicle_count
    );



    // ======================================
    // PASO 5:
    // SIMULACIÓN NORMAL
    // ======================================

    /*
        Si queremos ver la simulación normal
        durante 20 ciclos, podemos usar:

        simulate_traffic(
            20,
            intersection.vehicles,
            intersection.vehicle_count,
            intersection.lights,
            NUM_LIGHTS
        );

        Lo dejamos comentado mientras hacemos
        benchmarks porque tiene sleep(1).
    */



    // ======================================
    // PASO 7:
    // PRUEBAS DE RENDIMIENTO
    // ======================================

    printf("\nPRUEBAS DE RENDIMIENTO\n");


    // Pocos vehículos
    test_configuration(
        10,       // vehículos
        10000,    // iteraciones
        1234      // semilla
    );


    // Carga media
    test_configuration(
        50,
        10000,
        1234
    );


    // Carga alta
    test_configuration(
        100,
        10000,
        1234
    );


    return 0;
}