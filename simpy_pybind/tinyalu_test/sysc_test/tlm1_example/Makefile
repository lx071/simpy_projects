src = tlm1.cpp
INCLUDE_FLAGS = -I /usr/local/systemc-2.3.4/include
LDFLAGS = -L /usr/local/systemc-2.3.4/lib-linux64 -l systemc

.PHONY: all
all: run

main:
	g++ -o main $(src) $(INCLUDE_FLAGS) $(LDFLAGS)

run: main
	./main

clean:
	rm -rf main *.vcd
