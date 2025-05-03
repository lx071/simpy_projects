TOPLEVEL = tinyalu

vsrc = tinyalu.sv
csrc = sim_main.cpp

objdir = obj_dir
# cflags_extra = -fopenmp
VERILATOR_ROOT ?= $(shell verilator -getenv VERILATOR_ROOT)
INCLUDE_FLAGS = -I./${objdir} -I${VERILATOR_ROOT}/include/
LDFLAGS = ./${objdir}/V${TOPLEVEL}__ALL.a -pthread -lpthread -latomic


.PHONY: all
all: run-base

# Get Vtop__ALL.a, Vtop.h
${objdir}/V${TOPLEVEL}__ALL.a ${objdir}/V${TOPLEVEL}.h:
	verilator -cc --build hdl/${vsrc} --trace

V${TOPLEVEL}: ${objdir}/V${TOPLEVEL}__ALL.a ${objdir}/V${TOPLEVEL}.h $(VERILATOR_ROOT)/include/verilated.cpp $(VERILATOR_ROOT)/include/verilated_vcd_c.cpp $(VERILATOR_ROOT)/include/verilated_threads.cpp
	$(CXX) ${cflags_extra} ${csrc} ${INCLUDE_FLAGS} ${LDFLAGS} $^ -o V${TOPLEVEL}

.PHONY: run-base
run-base: V${TOPLEVEL}
	./V${TOPLEVEL}

run-trace: V${TOPLEVEL}
	./V${TOPLEVEL} +trace


### Python -- Cpp -- Verilog

objdir2 = verilator
LIB_NAME = wrapper
HARNESS_NAME = tinyalu-harness.cpp
CXXFLAGS = -O3 -Wall -shared -std=c++11 -fPIC -faligned-new
PYBIND_INCLUDE = $(shell python3 -m pybind11 --includes)

VERILATOR_FLAGS += -CFLAGS -fPIC
VERILATOR_FLAGS += -LDFLAGS -shared
# VERILATOR_FLAGS += -CFLAGS -I/usr/include/python3.8
VERILATOR_FLAGS += $(foreach var, $(PYBIND_INCLUDE), -CFLAGS $(var))
# VERILATOR_FLAGS += -CFLAGS -fvisibility=hidden -LDFLAGS -fvisibility=hidden -CFLAGS -DTRACE
VERILATOR_FLAGS += -CFLAGS -DTRACE

$(objdir2)/$(LIB_NAME).so:
	verilator $(VERILATOR_FLAGS) --Mdir $(objdir2) --cc hdl/$(vsrc) --build --trace --exe $(HARNESS_NAME)
	c++ $(CXXFLAGS) ./$(objdir2)/*.o -o $(objdir2)/$(LIB_NAME).so

run-python: $(objdir2)/$(LIB_NAME).so
	python $(TOPLEVEL).py

# verilator -CFLAGS -fPIC -CFLAGS -m64 -CFLAGS -shared -CFLAGS -Wno-attributes \
# 	-LDFLAGS -fPIC -LDFLAGS -m64 -LDFLAGS -shared -LDFLAGS -Wno-attributes \
# 	-CFLAGS -I/usr/include/python3.8 -CFLAGS -I/home/lx071/.local/lib/python3.8/site-packages/pybind11/include \
# 	-CFLAGS -fvisibility=hidden -LDFLAGS -fvisibility=hidden -CFLAGS -DTRACE \
# 	--Mdir verilator --cc hdl/tinyalu.sv --build --trace --exe tinyalu-harness.cpp

# c++ -O3 -Wall -shared -std=c++11 -fPIC -faligned-new ./verilator/*.o -o verilator/wrapper.so

.PHONY: clean
clean:
	-rm -rf ${objdir} V${TOPLEVEL} *.vcd logs utils/__pycache__ simulation verilator
