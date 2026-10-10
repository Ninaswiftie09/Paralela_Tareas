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
#define NUM_ITERATIONS 20

typedef struct {
    int id;
    int position;
} Vehicle;

typedef struct {
    int state;   // 0 = rojo, 1 = verde, 2 = amarillo
    int timer;
} TrafficLight;

typedef struct {
    Vehicle vehicles[MAX_VEHICLES];
    int vehicle_count;
    TrafficLight lights[NUM_LIGHTS];
    int id;
} Intersection;

void wait_one_second(void) {
#ifdef _WIN32
    Sleep(1000);
#else
    sleep(1);
#endif
}

void initialize_vehicles(Vehicle *vehicles, int num_vehicles) {
    for (int i = 0; i < num_vehicles; i++) {
        vehicles[i].id = i;
        vehicles[i].position = 0;
    }
}

void initialize_traffic_lights(TrafficLight *lights, int num_lights) {
    for (int i = 0; i < num_lights; i++) {
        lights[i].state = 0;
        lights[i].timer = rand() % 10 + 1;
    }
}

// Ajuste dinamico de hilos segun la carga de vehiculos.
void adjust_threads(int num_vehicles) {
    omp_set_dynamic(1);

    if (num_vehicles <= 20) {
        omp_set_num_threads(2);
    } else if (num_vehicles <= 50) {
        omp_set_num_threads(4);
    } else {
        omp_set_num_threads(8);
    }
}

// Los semaforos se actualizan simultaneamente entre los hilos disponibles.
void update_traffic_lights(TrafficLight *lights, int num_lights) {
    #pragma omp parallel for schedule(dynamic)
    for (int i = 0; i < num_lights; i++) {
        lights[i].timer--;

        if (lights[i].timer <= 0) {
            lights[i].state = (lights[i].state + 1) % 3;
            lights[i].timer = 5;
        }
    }
}

// Los vehiculos se reparten dinamicamente entre los hilos.
void move_vehicles(Vehicle *vehicles, int num_vehicles,
                   TrafficLight *lights, int num_lights) {
    #pragma omp parallel for schedule(dynamic)
    for (int i = 0; i < num_vehicles; i++) {
        int light_index = i % num_lights;

        if (lights[light_index].state == 1) {
            vehicles[i].position++;
        }
    }
}

void simulate_traffic(int num_iterations,
                      Vehicle *vehicles, int num_vehicles,
                      TrafficLight *lights, int num_lights) {
    for (int i = 0; i < num_iterations; i++) {
        // En cada iteracion se revisa la carga antes de abrir regiones paralelas.
        adjust_threads(num_vehicles);

        update_traffic_lights(lights, num_lights);
        move_vehicles(vehicles, num_vehicles, lights, num_lights);
        wait_one_second();
    }
}

void print_results(const Intersection *intersection) {
    printf("\nEstado final de los semaforos:\n");
    for (int i = 0; i < NUM_LIGHTS; i++) {
        printf("Semaforo %d -> estado=%d, timer=%d\n",
               i,
               intersection->lights[i].state,
               intersection->lights[i].timer);
    }

    printf("\nPosicion final de los vehiculos:\n");
    for (int i = 0; i < intersection->vehicle_count; i++) {
        printf("Vehiculo %d -> posicion=%d\n",
               intersection->vehicles[i].id,
               intersection->vehicles[i].position);
    }
}

int main(void) {
    Intersection intersection;

    intersection.id = 1;
    intersection.vehicle_count = 10;

    srand(1234);

    initialize_vehicles(intersection.vehicles, intersection.vehicle_count);
    initialize_traffic_lights(intersection.lights, NUM_LIGHTS);

    printf("Simulacion PARALELA con %d vehiculos.\n",
           intersection.vehicle_count);

    simulate_traffic(
        NUM_ITERATIONS,
        intersection.vehicles,
        intersection.vehicle_count,
        intersection.lights,
        NUM_LIGHTS
    );

    print_results(&intersection);
    return 0;
}
