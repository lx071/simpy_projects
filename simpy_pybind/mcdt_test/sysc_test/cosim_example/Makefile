all: compile

dsrc += $(PWD)/../../hdl/arbiter.v
dsrc += $(PWD)/../../hdl/slave_fifo.v
dsrc += $(PWD)/../../hdl/mcdt.v

compile:
	verilator --trace --timing -sc --exe --build --top-module mcdt -j $(dsrc) sc_main.cpp

run:
	./obj_dir/Vmcdt

clean:
	-rm -rf obj_dir *.log *.dmp *.vpd core dump.vcd