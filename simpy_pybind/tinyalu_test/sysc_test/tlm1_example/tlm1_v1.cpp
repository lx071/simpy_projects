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
        A.write(0);
        B.write(0);
        op.write(0);
        start.write(0);
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
    : uvm_sequence(name) { }

    void body() override {

        uvm_tlm_generic_payload *item;
        
        int num = 10;
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
        sc_stop();
    }
};

class driver: public uvm_driver {
public:
    uvm_tlm_generic_payload *trans;
    DUT *dut;
    Vtinyalu *top;
    driver(sc_core::sc_module_name name, DUT *dut) 
    : uvm_driver(name), dut(dut) {
        trans = new uvm_tlm_generic_payload("trans");
        top = dut->top;
    }

    void drive_transfer(int a, int b, int op) {
        // Apply inputs
        if (sc_time_stamp() > sc_time(1, SC_NS) && sc_time_stamp() < sc_time(10, SC_NS)) {
            dut->reset_n.write(0);  // Assert reset
        } else {
            dut->reset_n.write(1);  // Deassert reset
        }
        
        dut->A.write(a);
        dut->B.write(b);
        dut->op.write(op);
        dut->start.write(1);

        // Simulate 20ns
        wait(20, SC_NS);

        std::cout << dut->A.read() << " + " << dut->B.read() << " = " << dut->result.read() << std::endl;
    }

    void run_phase() override { 

        sc_core::sc_time delay(10, SC_NS);
        
        // 测试场景
        while(true) {
            // 获取下一个事务
            seq_item_port->get_next_item(trans, delay);

            unsigned char* data = trans->get_data_ptr();
            unsigned int len = trans->get_data_length();
            // std::cout << "len:" << len << std::endl;
            for(int i = 0; i < len / 3; i ++) {
                drive_transfer(int(data[i * 3]), int(data[i * 3 + 1]), int(data[i * 3 + 2]));
            }
            seq_item_port->item_done(trans, delay);
        }
    }
};


int sc_main(int argc, char* argv[]) {
    // Pass arguments so Verilated code can see them, e.g. $value$plusargs
    // This needs to be called before you create any model
    Verilated::commandArgs(argc, argv);

    // 创建模块实例
    DUT dut("dut");
    uvm_sequencer sqr("Sequencer");
    driver drv("Driver", &dut);
    sequence seq("Sequence");

    // 连接端口
    drv.seq_item_port(sqr.seq_item_export);
    seq.start(&sqr);

    // 启动仿真
    sc_core::sc_start();
    
    return 0;
}