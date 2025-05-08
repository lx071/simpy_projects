#include <systemc.h>
#include <tlm.h>

#include "utils.h"

// Include common routines
#include <verilated.h>

// Include model header, generated from Verilating "top.v"
#include "Vmcdt.h"

#include <chrono>

using namespace sc_core;

// module mcdt (
// input                 clk_i,
// input                 rstn_i,

// input   [31:0]        ch0_data_i,
// input                 ch0_valid_i,
// output                ch0_ready_o,
// output  [5:0]         ch0_margin_o,

// input   [31:0]        ch1_data_i,
// input                 ch1_valid_i,
// output                ch1_ready_o,
// output  [5:0]         ch1_margin_o,

// input   [31:0]        ch2_data_i,
// input                 ch2_valid_i,
// output                ch2_ready_o,
// output  [5:0]         ch2_margin_o,

// output  [31:0]        mcdt_data_o,
// output                mcdt_val_o,
// output  [1:0]         mcdt_id_o);

class DUT: public sc_module {
public:

    // Define clocks
    sc_clock clk;  // 创建周期为 10 的时钟信号对象，名称为 "clk"

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
    Vmcdt* top;

    DUT(sc_core::sc_module_name name)
        : sc_module(name), clk("clk", 10, SC_NS) {

        top = new Vmcdt("mcdt");
        
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

        init_value();

        // You must do one evaluation before enabling waves, in order to allow
        // SystemC to interconnect everything for testing.
        // sc_start(SC_ZERO_TIME);
    }

    void init_value() {
        ch0_data_i.write(0);
        ch0_valid_i.write(0);
        ch1_data_i.write(0);
        ch1_valid_i.write(0);
        ch2_data_i.write(0);
        ch2_valid_i.write(0);
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
        
        int num = 100;
        int item_num = 1;
        for(int i = 0; i < num; i ++) {
            item = create_item();
            start_item(item, m_sequencer);
            
            unsigned char arr[item_num*2];

            for (int j = 0; j < item_num; j = j + 1) {
                arr[j * 2] = i % 3;
                arr[j * 2 + 1] = i % 100;
            }
            // unsigned char arr[] = {0x1, 0x2, 0x3, 0x4, 0x5};
            unsigned char *payload_data = arr;

            // set data
            item->set_command(tlm::TLM_WRITE_COMMAND);
            item->set_address(0x0);
            item->set_data_ptr(reinterpret_cast<unsigned char*>(payload_data));
            item->set_data_length(item_num * 2);

            finish_item(item);
        }
        sc_stop();
    }
};

class driver: public uvm_driver {
public:
    uvm_tlm_generic_payload *trans;
    DUT *dut;
    Vmcdt *top;
    driver(sc_core::sc_module_name name, DUT *dut) 
    : uvm_driver(name), dut(dut) {
        trans = new uvm_tlm_generic_payload("trans");
        top = dut->top;
    }

    void drive_transfer(int id, int data) {
        // Apply inputs
        if (sc_time_stamp() > sc_time(1, SC_NS) && sc_time_stamp() < sc_time(10, SC_NS)) {
            dut->rstn_i.write(0);  // Assert reset
        } else {
            dut->rstn_i.write(1);  // Deassert reset
        }
        if(id == 0) {
            dut->ch0_data_i.write(data);
            dut->ch0_valid_i.write(1);
        }
        else if(id == 1) {
            dut->ch1_data_i.write(data);
            dut->ch1_valid_i.write(1);    
        }
        else if(id == 2) {
            dut->ch2_data_i.write(data);
            dut->ch2_valid_i.write(1);    
        }

        // Simulate 20ns
        wait(20, SC_NS);

        // std::cout << dut->mcdt_data_o.read() << " + " << dut->mcdt_val_o.read() << " = " << dut->mcdt_id_o.read() << std::endl;
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
            for(int i = 0; i < len / 2; i ++) {
                drive_transfer(int(data[i * 2]), int(data[i * 2 + 1]));
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

    auto start = std::chrono::high_resolution_clock::now();

    // 启动仿真
    sc_core::sc_start();

    auto end = std::chrono::high_resolution_clock::now();
    
    // 计算持续时间（秒，带小数）
    std::chrono::duration<double> duration = end - start;
    
    std::cout << "实际执行时间: " << duration.count() << " 秒" << std::endl;
    
    return 0;
}