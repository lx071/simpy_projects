all: compile

compile:
	verilator --trace --timing -sc --exe --build --top-module tinyalu -j ../../hdl/tinyalu.sv sc_main.cpp

run:
	./obj_dir/Vtinyalu

clean:
	-rm -rf obj_dir *.log *.dmp *.vpd core dump.vcd