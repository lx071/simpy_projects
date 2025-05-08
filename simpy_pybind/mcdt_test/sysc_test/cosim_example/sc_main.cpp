// SystemC global header
#include <systemc>

// Include common routines
#include <verilated.h>

// Include model header, generated from Verilating "top.v"
#include "Vmcdt.h"

using namespace sc_core;

int sc_main(int argc, char* argv[]) {
    
    // Pass arguments so Verilated code can see them, e.g. $value$plusargs
    // This needs to be called before you create any model
    Verilated::commandArgs(argc, argv);

    // Define clocks
    sc_clock clk("clk", 10, SC_NS);  // 创建周期为 10 的时钟信号对象，名称为 "clk"

    // Define interconnect
    sc_signal<bool> rstn_i;
    sc_signal<uint32_t> ch0_data_i;
    sc_signal<bool> ch0_valid_i;
    sc_signal<bool> ch0_ready_o;
    sc_signal<uint32_t> ch0_margin_o;

    sc_signal<uint32_t> ch1_data_i;
    sc_signal<bool> ch1_valid_i;
    sc_signal<bool> ch1_ready_o;
    sc_signal<uint32_t> ch1_margin_o;

    sc_signal<uint32_t> ch2_data_i;
    sc_signal<bool> ch2_valid_i;
    sc_signal<bool> ch2_ready_o;
    sc_signal<uint32_t> ch2_margin_o;

    sc_signal<uint32_t> mcdt_data_o;
    sc_signal<bool> mcdt_val_o;
    sc_signal<uint32_t> mcdt_id_o;

    // Construct the Verilated model, from inside Vtop.h
    // Using unique_ptr is similar to "Vtop* top = new Vtop" then deleting at end
    const std::unique_ptr<Vmcdt> top{new Vmcdt{"top"}};

    // Attach Vmcdt's signals to this upper model
    top->clk_i(clk);
    top->rstn_i(rstn_i);
    
    top->ch0_data_i(ch0_data_i);
    top->ch0_valid_i(ch0_valid_i);
    top->ch0_ready_o(ch0_ready_o);
    top->ch0_margin_o(ch0_margin_o);

    top->ch1_data_i(ch1_data_i);
    top->ch1_valid_i(ch1_valid_i);
    top->ch1_ready_o(ch1_ready_o);
    top->ch1_margin_o(ch1_margin_o);
    
    top->ch2_data_i(ch2_data_i);
    top->ch2_valid_i(ch2_valid_i);
    top->ch2_ready_o(ch2_ready_o);
    top->ch2_margin_o(ch2_margin_o);

    top->mcdt_data_o(mcdt_data_o);
    top->mcdt_val_o(mcdt_val_o);
    top->mcdt_id_o(mcdt_id_o);

    // You must do one evaluation before enabling waves, in order to allow
    // SystemC to interconnect everything for testing.
    sc_start(SC_ZERO_TIME);

    int num = 0;
    int id = 0;
    // Simulate until $finish
    while (!Verilated::gotFinish()) {

        // Apply inputs
        if (sc_time_stamp() > sc_time(1, SC_NS) && sc_time_stamp() < sc_time(10, SC_NS)) {
            rstn_i = 0;  // Assert reset
        } else {
            rstn_i = 1;  // Deassert reset
        }
        
        id = num % 3;

        if(id == 0) {
            ch0_data_i.write(num % 100);
            ch0_valid_i.write(1);
        }
        else if(id == 1) {
            ch1_data_i.write(num % 100);
            ch1_valid_i.write(1);
        }
        else if(id == 2) {
            ch2_data_i.write(num % 100);
            ch2_valid_i.write(1);
        }
        // cout << "num:" << num << endl;

        // Simulate 5ns
        sc_start(10, SC_NS);

        num ++;
        if (sc_time_stamp() > sc_time(20, SC_NS)) cout << "mcdt_data_o: " << mcdt_data_o << "\tmcdt_val_o: " << mcdt_val_o << "\tmcdt_id_o: " << mcdt_id_o << endl;

        if(num > 10) 
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