#ifndef UTILS_H
#define UTILS_H

#include <systemc.h>
#include <tlm.h>
#include <queue>

// 前向声明
class uvm_tlm_generic_payload;
class uvm_sequence;
class uvm_sequencer;

class uvm_seq_item_if : public sc_core::sc_interface {
    uvm_sequencer& imp;
public:
    uvm_seq_item_if(uvm_sequencer& comp);
    void get_next_item(uvm_tlm_generic_payload*& trans,
                     sc_core::sc_time delay);
    void item_done(uvm_tlm_generic_payload* trans,
                 sc_core::sc_time delay);
};


class uvm_sequence_item {
public:
    uvm_sequence_item(sc_core::sc_module_name name) 
        : m_sequence_id(-1), m_use_sequence_info(0), 
          m_depth(-1), m_sequencer(nullptr), m_parent_sequence(nullptr) {}

    virtual ~uvm_sequence_item() {}

    virtual const std::string get_type_name() const {
        return "uvm_sequence_item";
    }

    void set_sequence_id(int id) { m_sequence_id = id; }
    int get_sequence_id() const { return m_sequence_id; }

    void set_item_context(uvm_sequence* parent_seq, uvm_sequencer* sequencer = nullptr) {
        set_use_sequence_info(1);
        // if (parent_seq != nullptr) {
        //     set_parent_sequence(parent_seq);
        // }
        // if (sequencer == nullptr && m_parent_sequence != nullptr) {
        //     sequencer = m_parent_sequence->get_sequencer();
        // }
        set_sequencer(sequencer);
        // if (m_parent_sequence != nullptr) {
        //     set_depth(m_parent_sequence->get_depth() + 1);
        // }
    }

    void set_use_sequence_info(int value) { m_use_sequence_info = value; }
    int get_use_sequence_info() const { return m_use_sequence_info; }

    void set_id_info(uvm_sequence_item* item) {
        if (item == nullptr) {
            SC_REPORT_FATAL("set_id_info", "called with null parameter");
        }
        set_sequence_id(item->get_sequence_id());
    }

    void set_sequencer(uvm_sequencer* sequencer) { m_sequencer = sequencer; }
    uvm_sequencer* get_sequencer() const { return m_sequencer; }

    void set_parent_sequence(uvm_sequence* parent) { m_parent_sequence = parent; }
    uvm_sequence* get_parent_sequence() const { return m_parent_sequence; }

    void set_depth(int value) { m_depth = value; }
    int get_depth() {
        if (m_depth != -1) {
            return m_depth;
        }
        // if (m_parent_sequence == nullptr) {
        //     m_depth = 1;
        // } else {
        //     m_depth = m_parent_sequence->get_depth() + 1;
        // }
        return m_depth;
    }

protected:
    std::string name;
    int m_sequence_id;
    int m_use_sequence_info;
    int m_depth;
    uvm_sequencer* m_sequencer;
    uvm_sequence* m_parent_sequence;
};

class uvm_tlm_generic_payload : public uvm_sequence_item, public tlm::tlm_generic_payload {
public:
    uvm_tlm_generic_payload(sc_core::sc_module_name name)
        : uvm_sequence_item(name), tlm::tlm_generic_payload() {}
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
    void get_next_item(uvm_tlm_generic_payload*& trans, sc_core::sc_time delay) 
    {
        // std::cout << "Getting next item at " 
        //         << sc_core::sc_time_stamp() 
        //         << std::endl;
        trans = m_req_fifo.read();
    }

    void item_done(uvm_tlm_generic_payload* trans,
                            sc_core::sc_time delay) 
    {
        // std::cout << "Item done at " 
        //         << sc_core::sc_time_stamp() 
        //         << std::endl;
        item_done_event.notify();
    }
    
    void send_request(uvm_sequence* sequence_ptr, uvm_tlm_generic_payload* t, int rerandomize = 0) {
        // t->set_sequencer(this);
        // std::cout << "uvm_sequencer::send_request" << std::endl;
        m_req_fifo.write(t);
    }
    
    void wait_for_item_done(uvm_sequence* sequence_ptr, int transaction_id) {
        wait(item_done_event);
    }

    sc_fifo<uvm_tlm_generic_payload*> m_req_fifo;
    sc_event item_done_event;
};


class uvm_sequence : public uvm_sequence_item, sc_module {
public:
    uvm_sequence(sc_core::sc_module_name name)
        : uvm_sequence_item(name) {}

    virtual void start(uvm_sequencer* sequencer, uvm_sequence* parent_sequence = nullptr) {
        SC_HAS_PROCESS(uvm_sequence);
        m_sequencer = sequencer;
        set_item_context(parent_sequence, sequencer);
        SC_THREAD(body);
        // body();
    }

    virtual void body() = 0;

    virtual uvm_tlm_generic_payload* create_item() {
        return new uvm_tlm_generic_payload("tr");
    }

    virtual void start_item(uvm_tlm_generic_payload* item, uvm_sequencer* sequencer) {
        item->set_item_context(this, sequencer);
        // pre_do(1);
    }

    virtual void finish_item(uvm_tlm_generic_payload* item) {
        uvm_sequencer* sequencer = item->get_sequencer();
        if (sequencer == nullptr) {
            SC_REPORT_FATAL("finish_item", "sequence_item has null sequencer");
        }
        
        // mid_do(item);
        sequencer->send_request(this, item);
        sequencer->wait_for_item_done(this, -1);
        // post_do(item);
    }

    virtual void send_request(uvm_tlm_generic_payload* request, int rerandomize = 0) {
        if (m_sequencer == nullptr) {
            SC_REPORT_FATAL("send_request", "Null m_sequencer reference");
        }
        m_sequencer->send_request(this, request, rerandomize);
    }

    virtual void wait_for_item_done(int transaction_id = -1) {
        if (m_sequencer == nullptr) {
            SC_REPORT_FATAL("wait_for_item_done", "Null m_sequencer reference");
        }
        m_sequencer->wait_for_item_done(this, transaction_id);
    }
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

void uvm_seq_item_if::get_next_item(uvm_tlm_generic_payload*& trans,
                                           sc_core::sc_time delay) 
{
    imp.get_next_item(trans, delay);
}

void uvm_seq_item_if::item_done(uvm_tlm_generic_payload* trans,
                                       sc_core::sc_time delay) 
{
    imp.item_done(trans, delay);
}

#endif // UTILS_H