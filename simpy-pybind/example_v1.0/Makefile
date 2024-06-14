CPP = utils
MODULE = main

CXX_FLAGS = -O3 -Wall -shared -std=c++11 -fPIC $(shell python3 -m pybind11 --includes)

all: run

$(CPP).so: 
	c++ $(CXX_FLAGS) $(CPP).cpp -o $@


.PHONY: run
run: $(CPP).so
	python $(MODULE).py


.PHONY: clean
clean:
	rm -rf *.so
