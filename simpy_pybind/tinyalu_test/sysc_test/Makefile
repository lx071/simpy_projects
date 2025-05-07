all: compile

compile:
	verilator --trace --timing -sc --exe --build --top-module tinyalu -j ../hdl/tinyalu.sv sc_main.cpp

run:
	./obj_dir/Vtinyalu

clean:
	-rm -rf obj_dir *.log *.dmp *.vpd core dump.vcd

# all: compile

# compile:
# 	verilator -CFLAGS -fPIC -CFLAGS -m64 -CFLAGS -shared -CFLAGS -Wno-attributes \
# 		-LDFLAGS -fPIC -LDFLAGS -m64 -LDFLAGS -shared -LDFLAGS -Wno-attributes \
# 		-CFLAGS -fvisibility=hidden -LDFLAGS -fvisibility=hidden -CFLAGS -DTRACE \
# 		-CFLAGS 
# 		--Mdir verilator --timing --sc hdl/wrapper.v hdl/bfm.v hdl/Add.v --build --trace --exe sc_main.cpp
# 	c++ -O3 -Wall -shared -std=c++11 -fPIC -faligned-new ./verilator/*.o -o verilator/wrapper

# run:
# 	./obj_dir/Vwrapper

# clean:
# 	-rm -rf obj_dir *.log *.dmp *.vpd core dump.vcd verilator

# src = sc_main.cpp
# INCLUDE_FLAGS = -I /usr/local/systemc-2.3.4/include
# LDFLAGS = -L /usr/local/systemc-2.3.4/lib-linux64 -l systemc

# .PHONY: all
# all: run

# main:
# 	g++ -o main $(src) $(INCLUDE_FLAGS) $(LDFLAGS)

# run: main
# 	./main

# clean:
# 	rm -rf main *.vcd
