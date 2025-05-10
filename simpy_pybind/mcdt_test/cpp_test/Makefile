TOPLEVEL = mcdt

dsrc += $(PWD)/../hdl/arbiter.v
dsrc += $(PWD)/../hdl/slave_fifo.v
dsrc += $(PWD)/../hdl/mcdt.v

csrc = sim_main.cpp

objdir = obj_dir
# cflags_extra = -fopenmp
CXXFLAGS = -O3 -Wall -std=c++17 -no-pie
VERILATOR_ROOT ?= $(shell verilator -getenv VERILATOR_ROOT)
INCLUDE_FLAGS = -I./${objdir} -I${VERILATOR_ROOT}/include/
LDFLAGS = -pthread -lpthread -latomic


.PHONY: all
all: V${TOPLEVEL}

# Get Vmcdt__ALL.cpp, Vmcdt.h, *.cpp, *.h
${objdir}/V${TOPLEVEL}__ALL.cpp:
	verilator -cc --build ${dsrc} --top ${TOPLEVEL}

V${TOPLEVEL}: ${objdir}/V${TOPLEVEL}__ALL.cpp $(VERILATOR_ROOT)/include/verilated.cpp $(VERILATOR_ROOT)/include/verilated_vcd_c.cpp $(VERILATOR_ROOT)/include/verilated_threads.cpp
	$(CXX) ${cflags_extra} ${csrc} ${INCLUDE_FLAGS} ${LDFLAGS} $^ -o V${TOPLEVEL}

.PHONY: run
run:
	./V${TOPLEVEL}

.PHONY: clean
clean:
	-rm -rf ${objdir} V${TOPLEVEL}
