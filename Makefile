ifeq ($(OS),Windows_NT)
  UNAME := Windows
  EXE := .exe
  PYTHON ?= python
else
  UNAME := $(shell uname)
  EXE :=
  PYTHON ?= python3
endif

ifeq ($(origin CC),default)
  CC = gcc
endif
CFLAGS = -O2 -std=c11 -Wall -Wextra -fopenmp

ifeq ($(UNAME),Darwin)
  ifneq (,$(findstring clang,$(CC)))
    LIBOMP := $(shell brew --prefix libomp 2>/dev/null)
    CFLAGS = -O2 -std=c11 -Wall -Wextra -Xpreprocessor -fopenmp -I$(LIBOMP)/include
    LDFLAGS = -L$(LIBOMP)/lib -lomp
  endif
endif

all: lab12$(EXE)

lab12$(EXE): lab12_speedup.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS) -lm

run-mine:
	$(PYTHON) scripts/run_my_experiments.py

clean:
	$(PYTHON) -c "from pathlib import Path; [p.unlink() for p in [Path('lab12'), Path('lab12.exe')] if p.is_file()]"

.PHONY: all clean run-mine
