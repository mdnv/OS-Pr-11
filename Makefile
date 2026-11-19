# Ubuntu 22.04/24.04: make test | make graph | make c
PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
CC := gcc
CFLAGS := -std=c11 -Wall -Wextra -O2
.PHONY: all test graph c clean
all: test

test:
	$(PYTHON) -m unittest discover -s tests -v

graph:
	$(PYTHON) experiments.py

c:
	$(CC) $(CFLAGS) -o faults level_c/faults.c
	./faults

clean:
	rm -f faults
