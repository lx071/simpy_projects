// For std::unique_ptr
#include <memory>

// Include common routines
#include <verilated.h>

// Include model header, generated from Verilating "tinyalu.v"
#include "Vmcdt.h"

void posedge_clk(VerilatedContext* contextp, Vmcdt *top)
{
    top->eval();
    // Read outputs
    VL_PRINTF("[%" PRId64 "] clk = %0d, rstn = %0d, data = %0d, val = %0d, id = %0d\n",
                contextp->time(), top->clk_i, top->rstn_i, top->mcdt_data_o, top->mcdt_val_o,
                top->mcdt_id_o);

    contextp->timeInc(1);
    top->clk_i = 0;
    top->eval();
    contextp->timeInc(1);
    top->clk_i = 1;
    // top->eval();    
}

void chnl_write(VerilatedContext* contextp, Vmcdt *top, int id, int data)
{
    if(id == 0)
    {
        posedge_clk(contextp, top);
        top->ch0_data_i = data;
        top->ch0_valid_i = 1;
        posedge_clk(contextp, top);
        top->ch0_data_i = 0;
        top->ch0_valid_i = 0;
        // top->eval();
    }
    else if(id == 1)
    {
        posedge_clk(contextp, top);
        top->ch1_data_i = data;
        top->ch1_valid_i = 1;
        posedge_clk(contextp, top);
        top->ch1_data_i = 0;
        top->ch1_valid_i = 0;
        // top->eval();
    }
    else if(id == 2)
    {
        posedge_clk(contextp, top);
        top->ch2_data_i = data;
        top->ch2_valid_i = 1;
        posedge_clk(contextp, top);
        top->ch2_data_i = 0;
        top->ch2_valid_i = 0;
        // top->eval();
    }
}
void chnl_idle(Vmcdt *top, int id, int data)
{
    if(id == 0)
    {
        top->ch0_data_i = 0;
        top->ch0_valid_i = 0;
    }
    else if(id == 1)
    {
        top->ch1_data_i = 0;
        top->ch1_valid_i = 0;
    }
    else if(id == 2)
    {
        top->ch2_data_i = 0;
        top->ch2_valid_i = 0;
    }
}

int main(int argc, char **argv)
{
    // Construct a VerilatedContext to hold simulation time, etc.
    VerilatedContext* contextp = new VerilatedContext;

    // Pass arguments so Verilated code can see them, e.g. $value$plusargs
    // This needs to be called before you create any model
    contextp->commandArgs(argc, argv);

    // Construct the Verilated model, from Vtop.h generated from Verilating "top.v"
    Vmcdt* top = new Vmcdt{contextp};

    // Set Vmcdt's input signals
    top->clk_i = 0;
    top->rstn_i = 0;
    top->ch0_data_i = 0;
    top->ch0_valid_i = 0;
    top->ch1_data_i = 0;
    top->ch1_valid_i = 0;
    top->ch2_data_i = 0;
    top->ch2_valid_i = 0;
    
    int num = 0;

    // Simulate until $finish
    while (!contextp->gotFinish())
    {
        contextp->timeInc(1);  // 1 timeprecision period passes... old version: sc_time_stamp()

        // Toggle a fast (time/2 period) clock
        top->clk_i = !top->clk_i;
        
        if(!top->clk_i) 
        {
            if (contextp->time() >= 1 && contextp->time() <= 10) top->rstn_i = 0;  // Assert reset
            else top->rstn_i = 1;  // Deassert reset
            // Assign some other inputs
        }

        if(top->clk_i) 
        {
            if(top->rstn_i == 0)
            {
                top->ch0_data_i = 0;
                top->ch0_valid_i = 0;
                top->ch1_data_i = 0;
                top->ch1_valid_i = 0;
                top->ch2_data_i = 0;
                top->ch2_valid_i = 0;
            }
            else
            {
                if(num >= 100) break;
                chnl_write(contextp, top, 0, num + 10000);
                chnl_write(contextp, top, 1, num + 20000);
                chnl_write(contextp, top, 2, num + 30000);
                num ++;
            }
        }
        // printf("time: %0ld, clk: %0d, reset_n: %0d, A: %0d, B: %0d, op: %0d, result: %0d\n", contextp->time(), top->clk, top->reset_n, top->A, top->B, top->op, top->result);
        
        // Evaluate model
        top->eval();

        // printf("time: %0ld, clk: %0d, reset_n: %0d, A: %0d, B: %0d, op: %0d, result: %0d\n", contextp->time(), top->clk, top->reset_n, top->A, top->B, top->op, top->result);    
    }

    // Final model cleanup
    top->final();

    // Destroy model
    delete top;
    
    return 0;
}