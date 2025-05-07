// SystemC global header
#include <systemc>

// Include common routines
#include <verilated.h>

// Include model header, generated from Verilating "top.v"
#include "Vtinyalu.h"

using namespace sc_core;

int sc_main(int argc, char* argv[]) {
    
    // Pass arguments so Verilated code can see them, e.g. $value$plusargs
    // This needs to be called before you create any model
    Verilated::commandArgs(argc, argv);

    // Define clocks
    sc_clock clk("clk", 10, SC_NS);  // 创建周期为 10 的时钟信号对象，名称为 "clk"

    // Define interconnect
    sc_signal<bool> reset_n;
    sc_signal<uint32_t> A;
    sc_signal<uint32_t> B;
    sc_signal<uint32_t> op;
    sc_signal<bool> start;
    sc_signal<bool> done;
    sc_signal<uint32_t> result;

    // Construct the Verilated model, from inside Vtop.h
    // Using unique_ptr is similar to "Vtop* top = new Vtop" then deleting at end
    const std::unique_ptr<Vtinyalu> top{new Vtinyalu{"top"}};

    // Attach Vtop's signals to this upper model
    top->clk(clk);
    top->reset_n(reset_n);
    top->A(A);
    top->B(B);
    top->op(op);
    top->start(start);
    top->done(done);
    top->result(result);

    // You must do one evaluation before enabling waves, in order to allow
    // SystemC to interconnect everything for testing.
    sc_start(SC_ZERO_TIME);

    int num = 0;

    // Simulate until $finish
    while (!Verilated::gotFinish()) {

        // Apply inputs
        if (sc_time_stamp() > sc_time(1, SC_NS) && sc_time_stamp() < sc_time(10, SC_NS)) {
            reset_n = 0;  // Assert reset
        } else {
            reset_n = 1;  // Deassert reset
        }
        
        num ++;
        A = num % 100;
        B = num % 100;
        op = 1;

        // Simulate 5ns
        sc_start(10, SC_NS);

        if (sc_time_stamp() > sc_time(10, SC_NS)) cout << A << " + " << B << " = " << result << endl;

        if(num > 100) 
        {
            num = 0;
            break;
        }
    }

    // Final model cleanup
    top->final();

    // Return good completion status
    return 0;
}