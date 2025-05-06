#include <systemc.h>
#include <tlm.h>

#include "utils.h"

class driver: public uvm_driver {
public:
    driver(sc_core::sc_module_name name) 
    : uvm_driver(name) 
    {
    }
    void run_phase() override {
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
};

int sc_main(int argc, char* argv[]) {
    // 创建模块实例
    uvm_sequencer sequencer("Sequencer");
    driver driver("Driver");
    
    // 连接端口
    driver.seq_item_port(sequencer.seq_item_export);
    
    // 启动仿真
    sc_core::sc_start(200, SC_NS);
    
    return 0;
}