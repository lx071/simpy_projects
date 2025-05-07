#include <systemc.h>
#include <tlm.h>

#include "utils_v1.h"

// Include common routines
#include <verilated.h>

// Include model header, generated from Verilating "top.v"
#include "Vtinyalu.h"

using namespace sc_core;

class DUT: public sc_module {
public:

    // Define clocks
    sc_clock clk;  // 创建周期为 10 的时钟信号对象，名称为 "clk"

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
    Vtinyalu* top;

    DUT(sc_core::sc_module_name name)
        : sc_module(name), clk("clk", 10, SC_NS) {

        top = new Vtinyalu("tinyalu");
        
        // Attach Vtinyalu's signals to this upper model
        top->clk(clk);
        top->reset_n(reset_n);
        top->A(A);
        top->B(B);
        top->op(op);
        top->start(start);
        top->done(done);
        top->result(result);

        init_value();

        // You must do one evaluation before enabling waves, in order to allow
        // SystemC to interconnect everything for testing.
        // sc_start(SC_ZERO_TIME);
    }

    void init_value() {
        A.write(1);
        B.write(1);
        op.write(1);
    }

    ~DUT() {
        // Final model cleanup
        top->final();
        delete top;	
	}
};

class sequence: public uvm_sequence {
public:
    sequence(sc_core::sc_module_name name)
    : uvm_sequence(name) {
        std::cout << "sequence::new()" << std::endl;
    }

    void body() override {
        std::cout << "sequence::body()" << std::endl;
        uvm_tlm_generic_payload *item = create_item();
        
        int num = 3;
        int item_num = 5;
        for(int i = 0; i < num; i ++) {
            item = create_item();
            start_item(item, m_sequencer);
            
            unsigned char arr[item_num*3];

            for (int i = 0; i < item_num; i = i + 1) {
                arr[i*3] = i%100;
                arr[i*3+1] = i%100;
                arr[i*3+2] = 1;
            }
            // unsigned char arr[] = {0x1, 0x2, 0x3, 0x4, 0x5};
            unsigned char *payload_data = arr;

            // set data
            item->set_command(tlm::TLM_WRITE_COMMAND);
            item->set_address(0x0);
            item->set_data_ptr(reinterpret_cast<unsigned char*>(payload_data));
            item->set_data_length(item_num * 3);

            finish_item(item);
        }
    }
};

class driver: public uvm_driver {
public:
    uvm_tlm_generic_payload *trans;
    DUT *top;

    driver(sc_core::sc_module_name name, DUT *top) 
    : uvm_driver(name), top(top) {
        trans = new uvm_tlm_generic_payload("trans");
    }

    void run_phase() override {
        // 创建测试事务
        
        sc_core::sc_time delay(10, SC_NS);
        
        // 测试场景
        for (int i = 0; i < 3; ++i) {
            // 获取下一个事务
            seq_item_port->get_next_item(trans, delay);

            unsigned char* data = trans->get_data_ptr();
            unsigned int len = trans->get_data_length();
            std::cout << "len:" << len << std::endl;
            for(int i = 0; i < len / 3; i ++) {
                std::cout << int(data[i * 3]) << " " << int(data[i * 3 + 1]) << " " << int(data[i * 3 + 2]) << std::endl;
            }
            // 模拟处理延迟
            wait(25, SC_NS);
            top->A.write(1);
            top->B.write(1);
            top->op.write(1);
            
            // Simulate 5ns
            wait(10, SC_NS);

            if (sc_time_stamp() > sc_time(10, SC_NS)) std::cout << top->A << " + " << top->B << " = " << top->result << std::endl;
            
            // 标记事务完成
            seq_item_port->item_done(trans, delay);
            
            // 间隔
            wait(50, SC_NS);
        }
    }
};



int sc_main(int argc, char* argv[]) {
    // Pass arguments so Verilated code can see them, e.g. $value$plusargs
    // This needs to be called before you create any model
    Verilated::commandArgs(argc, argv);

    // 创建模块实例
    DUT dut("top");
    uvm_sequencer sqr("Sequencer");
    driver drv("Driver", &dut);
    sequence seq("Sequence");

    // 连接端口
    drv.seq_item_port(sqr.seq_item_export);
    seq.start(&sqr);

    // int num = 0;

    // Simulate until $finish
    // while (!Verilated::gotFinish()) {

    //     // Apply inputs
    //     if (sc_time_stamp() > sc_time(1, SC_NS) && sc_time_stamp() < sc_time(10, SC_NS)) {
    //         reset_n = 0;  // Assert reset
    //     } else {
    //         reset_n = 1;  // Deassert reset
    //     }
        
    //     num ++;
    //     A = num % 100;
    //     B = num % 100;
    //     op = 1;

    //     // Simulate 5ns
    //     sc_start(10, SC_NS);

    //     if (sc_time_stamp() > sc_time(10, SC_NS)) cout << A << " + " << B << " = " << result << endl;

    //     if(num > 100) 
    //     {
    //         num = 0;
    //         break;
    //     }
    // }

    // 启动仿真
    sc_core::sc_start(200, SC_NS);
    
    return 0;
}