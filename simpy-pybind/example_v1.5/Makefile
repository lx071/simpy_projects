TOPLEVEL = tinyalu


.PHONY: all
all: run-python


### Python -- Cpp -- Verilog


run-python:
	python $(TOPLEVEL).py


.PHONY: clean
clean:
	-rm -rf ${objdir} V${TOPLEVEL} *.vcd logs utils/__pycache__ simulation verilator
