#include <systemc.h>
#include <tlm.h>

#include "utils.h"

// Sequencer构造函数实现
uvm_sequencer::uvm_sequencer(sc_core::sc_module_name name) 
    : sc_module(name), intf(*this) 
{
    seq_item_export.bind(intf);
}

// Sequencer方法实现
void uvm_sequencer::get_next_item(tlm::tlm_generic_payload& trans, 
                            sc_core::sc_time& delay) 
{
    std::cout << "Getting next item at " 
              << sc_core::sc_time_stamp() 
              << std::endl;
}

void uvm_sequencer::item_done(tlm::tlm_generic_payload& trans,
                        sc_core::sc_time& delay) 
{
    std::cout << "Item done at " 
              << sc_core::sc_time_stamp() 
              << std::endl;
}


// 适配器方法实现
uvm_seq_item_if::uvm_seq_item_if(uvm_sequencer& comp) 
    : imp(comp) {}

void uvm_seq_item_if::get_next_item(tlm::tlm_generic_payload& trans,
                                           sc_core::sc_time& delay) 
{
    imp.get_next_item(trans, delay);
}

void uvm_seq_item_if::item_done(tlm::tlm_generic_payload& trans,
                                       sc_core::sc_time& delay) 
{
    imp.item_done(trans, delay);
}


uvm_driver::uvm_driver(sc_core::sc_module_name name) 
    : sc_module(name) 
{
    // 注册测试线程
    SC_THREAD(run_test);
}

void uvm_driver::run_test() {
    // 创建测试事务
    tlm::tlm_generic_payload trans;
    sc_core::sc_time delay(10, SC_NS);
    
    // 测试场景
    for (int i = 0; i < 3; ++i) {
        // 获取下一个事务
        seq_item_port->get_next_item(trans, delay);
        
        // 模拟处理延迟
        wait(25, SC_NS);
        
        // 标记事务完成
        seq_item_port->item_done(trans, delay);
        
        // 间隔
        wait(50, SC_NS);
    }
}

int sc_main(int argc, char* argv[]) {
    // 创建模块实例
    uvm_sequencer sequencer("Sequencer");
    uvm_driver driver("Driver");
    
    // 连接端口
    driver.seq_item_port(sequencer.seq_item_export);
    
    // 启动仿真
    sc_core::sc_start(200, SC_NS);
    
    return 0;
}