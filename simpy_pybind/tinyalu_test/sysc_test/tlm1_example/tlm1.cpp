#include <systemc.h>
#include <tlm.h>

#include "utils_v1.h"

class sequence: public uvm_sequence {
public:
    sequence(sc_core::sc_module_name name)
    : uvm_sequence(name) {
        std::cout << "sequence::new()" << std::endl;
    }

    void body() override {
        std::cout << "sequence::body()" << std::endl;
        uvm_tlm_generic_payload *item = create_item();
        start_item(item, m_sequencer);
        finish_item(item);
    }
};

class driver: public uvm_driver {
public:
    uvm_tlm_generic_payload *trans;

    driver(sc_core::sc_module_name name) 
    : uvm_driver(name) {
        trans = new uvm_tlm_generic_payload("trans");
    }

    void run_phase() override {
        // 创建测试事务
        
        sc_core::sc_time delay(10, SC_NS);
        
        // 测试场景
        for (int i = 0; i < 3; ++i) {
            // 获取下一个事务
            seq_item_port->get_next_item(*trans, delay);
            
            // 模拟处理延迟
            wait(25, SC_NS);
            
            // 标记事务完成
            seq_item_port->item_done(*trans, delay);
            
            // 间隔
            wait(50, SC_NS);
        }
    }
};

int sc_main(int argc, char* argv[]) {
    // 创建模块实例
    uvm_sequencer sqr("Sequencer");
    driver drv("Driver");
    sequence seq("Sequence");

    // 连接端口
    drv.seq_item_port(sqr.seq_item_export);
    seq.start(&sqr);

    // 启动仿真
    sc_core::sc_start(200, SC_NS);
    
    return 0;
}