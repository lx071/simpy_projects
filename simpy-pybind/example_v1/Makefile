TOPLEVEL = tinyalu

vsrc = tinyalu.sv
csrc = sim_main.cpp

objdir = obj_dir
# cflags_extra = -fopenmp
CXXFLAGS = -O3 -Wall -std=c++17 -no-pie
VERILATOR_ROOT ?= $(shell verilator -getenv VERILATOR_ROOT)
INCLUDE_FLAGS = -I./${objdir} -I${VERILATOR_ROOT}/include/
LDFLAGS = ./${objdir}/V${TOPLEVEL}__ALL.a -pthread -lpthread -latomic


.PHONY: all
all: V${TOPLEVEL}

# Get Vtop__ALL.a, Vtop.h
${objdir}/V${TOPLEVEL}__ALL.a ${objdir}/V${TOPLEVEL}.h:
	verilator -cc --build hdl/${vsrc} --trace

V${TOPLEVEL}: ${objdir}/V${TOPLEVEL}__ALL.a ${objdir}/V${TOPLEVEL}.h $(VERILATOR_ROOT)/include/verilated.cpp $(VERILATOR_ROOT)/include/verilated_vcd_c.cpp $(VERILATOR_ROOT)/include/verilated_threads.cpp
	$(CXX) ${cflags_extra} ${csrc} ${INCLUDE_FLAGS} ${LDFLAGS} $^ -o V${TOPLEVEL}

.PHONY: run
run:
	./V${TOPLEVEL}

.PHONY: clean
clean:
	-rm -rf ${objdir} V${TOPLEVEL} *.vcd
