TOPLEVEL = tinyalu


.PHONY: all
all: run-base


### Python -- Cpp -- Verilog


run-python:
	python $(TOPLEVEL).py

VERILATOR_ROOT ?= $(shell verilator -getenv VERILATOR_ROOT)
objdir = ./simulation/verilator
INCLUDE_FLAGS = -I. -I${objdir} -I${VERILATOR_ROOT}/include/
LDFLAGS = -L${objdir}/wrapper.so

run-base:
	g++ $(INCLUDE_FLAGS) $(LDFLAGS) sim_main.cpp -o main
	./main


.PHONY: clean
clean:
	-rm -rf main simulation utils/__pycache__
