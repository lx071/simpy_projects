#ifndef SEQUENCER_H
#define SEQUENCER_H

#include <systemc.h>
#include <tlm.h>


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

    SC_CTOR(uvm_sequencer);
    // uvm_driver(sc_module_name name) : sc_module(name) {
    //     SC_THREAD(run_phase);
    // }
     
    void get_next_item(tlm::tlm_generic_payload& trans,
                     sc_core::sc_time& delay);
    void item_done(tlm::tlm_generic_payload& trans,
                 sc_core::sc_time& delay);
};

class uvm_driver : public sc_module {
public:
    // 端口声明
    sc_core::sc_port<uvm_seq_item_if> seq_item_port;
    
    // 构造函数
    SC_CTOR(uvm_driver);
    // uvm_driver(sc_module_name name) : sc_module(name) {
    //     SC_THREAD(run_phase);
    // }
    
private:
    // 测试线程
    void run_test();
};

#endif // SEQUENCER_H