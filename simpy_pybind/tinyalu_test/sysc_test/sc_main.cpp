// -*- SystemC -*-
// DESCRIPTION: Verilator Example: Top level main for invoking SystemC model
//
// This file ONLY is placed under the Creative Commons Public Domain, for
// any use, without warranty, 2017 by Wilson Snyder.
// SPDX-License-Identifier: CC0-1.0
//======================================================================

// SystemC global header
#include <systemc.h>

// Include common routines
#include <verilated.h>

// Include model header, generated from Verilating "top.v"
#include "Vtinyalu.h"

#include <tlm.h>

#if VM_TRACE
#include <verilated_vcd_sc.h>
#endif

#include <iostream>
#include <queue>

std::mutex mtx;        // 全局互斥锁
std::condition_variable cr;   // 全局条件变量

struct Item {
    int in1;
    int in2;
    int op;
};

sc_event item_done_e; // declare an event

class Interface : public sc_core::sc_interface{
public:
    virtual void get_next_item(tlm::tlm_generic_payload* trans);
    virtual void item_done(tlm::tlm_generic_payload* trans);
    virtual ~Interface() {}
};

SC_MODULE(Sequencer) {
public:

    class seq_item_imp : public Interface {
    public:
        seq_item_imp(Sequencer* parent) : parent(parent) {}

        void get_next_item(tlm::tlm_generic_payload* trans) override {
            parent->get_next_item(trans);
        }

        void item_done(tlm::tlm_generic_payload* item = nullptr) override {
            parent->item_done(item);
        }

    private:
        uvm_sequencer* parent;
    };

    sc_export<Interface> seq_item_export;
    SC_CTOR(Sequencer) {
        // socket.register_b_transport(this, &Sequencer::get_next_item);   //register methods with each socket
    }

    std::queue<Item> req_mb;


    void get_next_item(tlm::tlm_generic_payload& trans, sc_time& delay) {    
		
        Item req = req_mb.front();
        req_mb.pop();
        cout << "in1:" << req.in1 << "\nin2:" << req.in2 << "\nop:" << req.op << endl;

        trans.set_data_ptr( reinterpret_cast<unsigned char*>(&req) );
        wait(SC_ZERO_TIME);
        trans.set_response_status(tlm::TLM_OK_RESPONSE);
    }

    void send_request(Item item) {
        req_mb.push(item);
    }

    void wait_for_item_done() {
        // wait(item_done_e);
    }
};

    // class Interface_imp : public Interface {
    //     Sequencer& parent;
    // public 
    // };
    

SC_MODULE(Driver) {
public:
    sc_port<Interface> seq_item_port;

    SC_CTOR(Driver) {
        SC_THREAD(run);
    }

private:

    void run() {
        tlm::tlm_generic_payload trans;
        sc_time delay = sc_time(10, SC_NS);

        seq_item_port.get_next_item(trans, delay);
        
        Item item = *reinterpret_cast<Item*>(trans.get_data_ptr());
        
        cout << "in1:" << item.in1 << "\nin2:" << item.in2 << "\nop:" << item.op << endl;
    }
};

SC_MODULE(Sequence) {
public:

    SC_CTOR(Sequence) {
        m_sequencer = nullptr;
    }

    Sequencer *m_sequencer;

    void set_item_context() {


    }

    void start(Sequencer *sequencer) {        
        m_sequencer = sequencer;
        body();
    }

    void body() {
        cout << "body" << endl;
        Item item;
        item.in1 = 2;
        item.in2 = 3;
        item.op = 4;
        m_sequencer->send_request(item);
        // m_sequencer->wait_for_item_done();
    }

    // def start(self, sequencer, parent_sequence = None):
    //     self.m_sequencer = sequencer
    //     self.set_item_context(parent_sequence, sequencer)
    //     self.env.process(self.body())
        
};

SC_MODULE(Test) {
public:
    
    Sequencer *sequencer;
    Driver *driver;
    Sequence *sequence;
    
    SC_CTOR(Test) {
        sequencer = new Sequencer("sequencer");
        driver = new Driver("driver");
        sequence = new Sequence("sequence");
        driver->seq_item_port.bind(sequencer->seq_item_export);

        sequence->start(sequencer);
    }
};

int sc_main(int argc, char* argv[]) {
    Test test("test");
    cout << "xxx" << endl;
    sc_start();
    return 0;
}
