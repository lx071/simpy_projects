// For std::unique_ptr
#include <memory>

// Include common routines
#include <verilated.h>

// Include model header, generated from Verilating "tinyalu.v"
#include "Vtinyalu.h"


int main(int argc, char **argv)
{
    // Create logs/ directory in case we have traces to put under it
    Verilated::mkdir("logs");

    // Construct a VerilatedContext to hold simulation time, etc.
    // Multiple modules (made later below with Vtop) may share the same
    // context to share time, or modules may have different contexts if
    // they should be independent from each other.

    // Using unique_ptr is similar to
    // "VerilatedContext* contextp = new VerilatedContext" then deleting at end.
    const std::unique_ptr<VerilatedContext> contextp{new VerilatedContext};

    // Set debug level, 0 is off, 9 is highest presently used
    // May be overridden by commandArgs argument parsing
    contextp->debug(0);

    // Randomization reset policy
    // May be overridden by commandArgs argument parsing
    contextp->randReset(2);

    // Verilator must compute traced signals
    contextp->traceEverOn(true);

    // Pass arguments so Verilated code can see them, e.g. $value$plusargs
    // This needs to be called before you create any model
    contextp->commandArgs(argc, argv);

    // Construct the Verilated model, from Vtop.h generated from Verilating "top.v".
    // Using unique_ptr is similar to "Vtop* top = new Vtop" then deleting at end.
    // "TOP" will be the hierarchical name of the module.
    const std::unique_ptr<Vtinyalu> top{new Vtinyalu{contextp.get(), "TOP"}};

    // Set Vtinyalu's input signals
    top->clk = 0;
    top->reset_n = 0;
    top->start = 0;
    top->A = 0;
    top->B = 0;
    top->op = 0;
    
    int num = 0;

    // Simulate until $finish
    while (!contextp->gotFinish()) // old version: !Verilated::gotFinish()
    {
        // Most of the contextp-> calls can use Verilated:: calls instead;
        // the Verilated:: versions just assume there's a single context
        // being used (per thread).  It's faster and clearer to use the
        // newer contextp-> versions.

        contextp->timeInc(1);  // 1 timeprecision period passes... old version: sc_time_stamp()

        // Toggle a fast (time/2 period) clock
        top->clk = !top->clk;
        
        if(!top->clk) 
        {
            if (contextp->time() > 1 && contextp->time() < 10) top->reset_n = 0;  // Assert reset
            else top->reset_n = 1;  // Deassert reset
            // Assign some other inputs
        }

        if(top->clk) 
        {
            if(top->reset_n == 0)
            {
                top->start = 0;
                top->A = 0;
                top->B = 0;
                top->op = 0;
            }
            else
            {
                if(num >= 20) break;
                if(top->start && top->done)
                {
                    top->start = 0;
                }
                else if(!top->start && !top->done)
                {
                    top->start = 1;
                    top->op = 1;
                    top->A = num % 200;
                    top->B = num % 200;  
                    num ++;
                }
            }
        }
        // printf("time: %0ld, clk: %0d, reset_n: %0d, A: %0d, B: %0d, op: %0d, result: %0d\n", contextp->time(), top->clk, top->reset_n, top->A, top->B, top->op, top->result);
        
        // Evaluate model
        // (If you have multiple models being simulated in the same
        // timestep then instead of eval(), call eval_step() on each, then
        // eval_end_step() on each. See the manual.)
        top->eval();
        // eval_end_step() Evaluate at end of a timestep for tracing.

        // printf("time: %0ld, clk: %0d, reset_n: %0d, A: %0d, B: %0d, op: %0d, result: %0d\n", contextp->time(), top->clk, top->reset_n, top->A, top->B, top->op, top->result);    

        // Read outputs
        VL_PRINTF("[%" PRId64 "] clk = %0d, rstn = %0d, A = %0d, B = %0d, op = %0d, result = %0d, start = %0d, done = %0d\n",
                    contextp->time(), top->clk, top->reset_n, top->A, top->B,
                    top->op, top->result, top->start, top->done);
    }

    // Final model cleanup
    top->final();

    // Final simulation summary
    // contextp->statsPrintSummary();

    // Return good completion status
    // Don't use exit() or destructor won't get called
    return 0;
}