#ifndef UTILS_H
#define UTILS_H

#include <systemc.h>
#include <tlm.h>
#include <queue>

// 前向声明
class uvm_sequencer;

class uvm_seq_item_if : public sc_core::sc_interface {
    uvm_sequencer& imp;
public:
    uvm_seq_item_if(uvm_sequencer& comp);
    void get_next_item(tlm::tlm_generic_payload& trans,
                     sc_core::sc_time& delay);
    void item_done(tlm::tlm_generic_payload& trans,
                 sc_core::sc_time& delay);
};

// Sequencer类声明
class uvm_sequencer : public sc_module {
public:
    sc_core::sc_export<uvm_seq_item_if> seq_item_export;
    uvm_seq_item_if intf;

    // Sequencer构造函数实现
    uvm_sequencer(sc_core::sc_module_name name) 
        : sc_module(name), intf(*this) 
    {
        seq_item_export.bind(intf);
    }

    // Sequencer方法实现
    void get_next_item(tlm::tlm_generic_payload& trans, 
                                sc_core::sc_time& delay) 
    {
        std::cout << "Getting next item at " 
                << sc_core::sc_time_stamp() 
                << std::endl;
    }

    void item_done(tlm::tlm_generic_payload& trans,
                            sc_core::sc_time& delay) 
    {
        std::cout << "Item done at " 
                << sc_core::sc_time_stamp() 
                << std::endl;
    }

    std::queue<tlm::tlm_generic_payload*> m_req_fifo;
};



class uvm_driver : public sc_module {
public:
    // 端口声明
    sc_core::sc_port<uvm_seq_item_if> seq_item_port;
    
    // 构造函数
    uvm_driver(sc_core::sc_module_name name) 
    : sc_module(name) 
    {
        SC_HAS_PROCESS(uvm_driver);
        // 注册测试线程
        SC_THREAD(run_phase);
    }

    // 测试线程
    virtual void run_phase() 
    {
        std::cout << "uvm_driver::run_phase" << std::endl;
    };
};


// interface 方法实现
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

#endif // UTILS_H