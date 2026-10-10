#pragma once
#include <omp.h>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

struct Body { double x, y, vx, vy, mass; };
struct Force { double x = 0, y = 0; };
struct Config { int n = 5000, steps = 10, threads = 8, chunk = 0; std::string schedule = "static"; };

inline Config parse(int argc, char** argv) {
    Config c;
    for (int k = 1; k < argc; k += 2) {
        if (k + 1 == argc) throw std::runtime_error("Missing option value");
        std::string key = argv[k], value = argv[k + 1];
        if (key == "--schedule") c.schedule = value;
        else {
            std::size_t end;
            int v = std::stoi(value, &end);
            if (end != value.size()) throw std::runtime_error("Invalid integer");
            if (key == "--n") c.n = v;
            else if (key == "--steps") c.steps = v;
            else if (key == "--threads") c.threads = v;
            else if (key == "--chunk") c.chunk = v;
            else throw std::runtime_error("Unknown option");
        }
    }
    if (c.n < 1 || c.steps < 1 || c.threads < 1 || c.chunk < 0) throw std::runtime_error("Invalid range");
    if (c.schedule != "static" && c.schedule != "dynamic" && c.schedule != "guided") throw std::runtime_error("Invalid schedule");
    return c;
}

inline std::vector<Body> initial(int n) {
    std::mt19937 rng(42);
    auto unit = [&]() { return static_cast<double>(rng()) / 4294967295.0; };
    std::vector<Body> b(n);
    for (auto& v : b) v = {2 * unit() - 1, 2 * unit() - 1, 0, 0, 1 + unit()};
    return b;
}

inline Force pair_force(const Body& a, const Body& b) {
    double dx = b.x - a.x, dy = b.y - a.y;
    double r2 = dx * dx + dy * dy + 1e-4;
    double scale = 1e-3 * a.mass * b.mass / (r2 * std::sqrt(r2));
    return {scale * dx, scale * dy};
}

inline void advance(Body& b, Force f) {
    b.vx += 1e-3 * f.x / b.mass;
    b.vy += 1e-3 * f.y / b.mass;
    b.x += 1e-3 * b.vx;
    b.y += 1e-3 * b.vy;
}

inline void sequential(std::vector<Body>& b, int steps) {
    std::vector<Force> f(b.size());
    for (int step = 0; step < steps; ++step) {
        for (std::size_t i = 0; i < b.size(); ++i) {
            f[i] = {};
            for (std::size_t j = 0; j < b.size(); ++j) if (i != j) {
                Force p = pair_force(b[i], b[j]);
                f[i].x += p.x;
                f[i].y += p.y;
            }
        }
        for (std::size_t i = 0; i < b.size(); ++i) advance(b[i], f[i]);
    }
}

inline int parallel(std::vector<Body>& b, const Config& c, bool optimized) {
    omp_set_dynamic(0);
    omp_sched_t policy = c.schedule == "static" ? omp_sched_static : c.schedule == "dynamic" ? omp_sched_dynamic : omp_sched_guided;
    omp_set_schedule(policy, c.chunk);
    std::vector<Force> f(c.n);
    std::vector<std::vector<Force>> local;
    if (optimized) local.assign(c.threads, std::vector<Force>(c.n));
    int used = 0;
    #pragma omp parallel num_threads(c.threads) shared(used, b, f, local)
    {
        int tid = omp_get_thread_num();
        if (tid == 0) used = omp_get_num_threads();
        #pragma omp barrier
        for (int step = 0; step < c.steps; ++step) {
            if (optimized) {
                std::fill(local[tid].begin(), local[tid].end(), Force{});
                #pragma omp barrier
                #pragma omp for schedule(runtime) nowait
                for (int i = 0; i < c.n; ++i) {
                    for (int j = i + 1; j < c.n; ++j) {
                        Force p = pair_force(b[i], b[j]);
                        local[tid][i].x += p.x;
                        local[tid][i].y += p.y;
                        local[tid][j].x -= p.x;
                        local[tid][j].y -= p.y;
                    }
                }
                #pragma omp barrier
                #pragma omp for schedule(static) nowait
                for (int i = 0; i < c.n; ++i) {
                    f[i] = {};
                    for (int t = 0; t < used; ++t) {
                        f[i].x += local[t][i].x;
                        f[i].y += local[t][i].y;
                    }
                }
            } else {
                #pragma omp for schedule(runtime) nowait
                for (int i = 0; i < c.n; ++i) {
                    f[i] = {};
                    for (int j = 0; j < c.n; ++j) if (i != j) {
                        Force p = pair_force(b[i], b[j]);
                        f[i].x += p.x;
                        f[i].y += p.y;
                    }
                }
            }
            #pragma omp barrier
            #pragma omp for schedule(static) nowait
            for (int i = 0; i < c.n; ++i) advance(b[i], f[i]);
            #pragma omp barrier
        }
    }
    return used;
}

inline int run(int argc, char** argv, const std::string& mode) {
    try {
        Config c = parse(argc, argv);
        auto b = initial(c.n);
        int max_threads = omp_get_max_threads();
        double start = omp_get_wtime();
        int used = 1;
        if (mode == "sequential") sequential(b, c.steps);
        else used = parallel(b, c, mode == "parallel-optimized");
        double elapsed = omp_get_wtime() - start;
        auto reference = initial(c.n);
        sequential(reference, c.steps);
        double checksum = 0, error = 0;
        for (int i = 0; i < c.n; ++i) {
            checksum += (i + 1) * (b[i].x + 3 * b[i].y + 5 * b[i].vx + 7 * b[i].vy);
            error = std::max({error, std::abs(b[i].x - reference[i].x), std::abs(b[i].y - reference[i].y), std::abs(b[i].vx - reference[i].vx), std::abs(b[i].vy - reference[i].vy)});
        }
        std::cout << std::setprecision(12) << "Student: Nina Najera Marakovits\nExecutable: " << argv[0]
                  << "\nMode: " << mode << "\nN: " << c.n << " | Steps: " << c.steps << " | Seed: 42\nThreads requested: "
                  << (mode == "sequential" ? 1 : c.threads) << " | Threads used: " << used
                  << "\nSchedule: " << (mode == "sequential" ? "sequential" : c.schedule) << " | Chunk: " << c.chunk
                  << "\nElapsed: " << elapsed << " s\nChecksum: " << checksum << "\nMax difference: " << error
                  << "\nProcessors reported by OpenMP: " << omp_get_num_procs() << "\nMax threads reported by OpenMP: " << max_threads << '\n';
        return error <= 1e-9 ? 0 : 2;
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
