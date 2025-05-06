#ifndef SEQUENCER_H
#define SEQUENCER_H

#include <systemc.h>
#include <tlm.h>

// 接口定义
// class Interface : public sc_core::sc_interface {
// public:
//     virtual void get_next_item(tlm::tlm_generic_payload& trans, 
//                              sc_core::sc_time& delay) = 0;
//     virtual void item_done(tlm::tlm_generic_payload& trans,
//                          sc_core::sc_time& delay) = 0;
//     virtual ~Interface() {}
// };

// 前向声明
class Sequencer;

// 适配器类声明
// class uvm_seq_item_if : public sc_core::sc_interface {
//     Sequencer& imp;
// public:
//     uvm_seq_item_if(Sequencer& seq);
//     void get_next_item(tlm::tlm_generic_payload& trans,
//                      sc_core::sc_time& delay) override;
//     void item_done(tlm::tlm_generic_payload& trans,
//                  sc_core::sc_time& delay) override;
// };

class uvm_seq_item_if : public sc_core::sc_interface {
    Sequencer& imp;
public:
    uvm_seq_item_if(Sequencer& comp);
    void get_next_item(tlm::tlm_generic_payload& trans,
                     sc_core::sc_time& delay);
    void item_done(tlm::tlm_generic_payload& trans,
                 sc_core::sc_time& delay);
};

// Sequencer类声明
SC_MODULE(Sequencer) {
public:
    sc_core::sc_export<uvm_seq_item_if> seq_item_export;
    uvm_seq_item_if intf;

    SC_CTOR(Sequencer);
    
    void get_next_item(tlm::tlm_generic_payload& trans,
                     sc_core::sc_time& delay);
    void item_done(tlm::tlm_generic_payload& trans,
                 sc_core::sc_time& delay);
};

SC_MODULE(Driver) {
public:
    // 端口声明
    sc_core::sc_port<uvm_seq_item_if> seq_item_port;
    
    // 构造函数
    SC_CTOR(Driver);
    
private:
    // 测试线程
    void run_test();
};

#endif // SEQUENCER_H