import sys
sys.path.append("../../")

from utils import *
import simpy

config_db = {}


class Event:
    def __init__(self, env):
        self.env = env
        self.event = self.env.event()

    def wait(self):
        yield self.event

    def set(self):
        self.event.succeed()

    def clear(self):
        self.event = self.env.event()


class chnl_trans:
    def __init__(self, ch_id, pkt_id):
        self.ch_id = ch_id
        self.pkt_id = pkt_id
        self.data_nidles = 0
        self.pkt_nidles = 1
        self.data_size = 10
        
        data = [1] * self.data_size
        for i in range(len(data)):
            data[i] = 0xC000_0000 + (self.ch_id<<24) + (self.pkt_id<<8) + i;
        self.data = data
        

class Sequence(uvm_sequence):

    def __init__(self, env, name):
        super().__init__(env, name)


    def body(self):

        for i in range(50000):
            item = self.create_item()
            self.start_item(item, self.m_sequencer)
            trans = chnl_trans(i % 3, 0)
            payload = {
                'data': trans
            }
            item.set_data_ptr(payload)
            yield self.env.process(self.finish_item(item))


class Sequencer(uvm_sequencer):
    
    def __init__(self, env, name):
        super().__init__(env, name)


class Driver(uvm_driver):

    def __init__(self, env, name):
        super().__init__(env, name)

        self.simContext = config_db['simContext']
        self.run_thread = self.env.process(self.run())
        self.time = 0
        self.data = [None]
        self.init_value()
    
    def init_value(self):
        top = self.simContext
        top.setValue("clk_i", 0)
        top.setValue("rstn_i", 0)
        top.setValue("ch0_data_i", 0)
        top.setValue("ch0_valid_i", 0)
        top.setValue("ch1_data_i", 0)
        top.setValue("ch1_valid_i", 0)
        top.setValue("ch2_data_i", 0)
        top.setValue("ch2_valid_i", 0)

    def run(self):
        trans = uvm_tlm_generic_payload()
        trans.set_data_ptr( self.data )

        while True:
            trans.set_response_status( tlm_response_status.TLM_INCOMPLETE_RESPONSE, self.socket )
            yield self.env.process(self.socket.get_next_item(trans))

            payload = trans.get_data_ptr()[0]

            ch_id = payload['data'].ch_id
            pkt_data = payload['data'].data
            num = len(pkt_data)
            for i in range(num):
                self.chnl_write(ch_id, pkt_data[i])

            self.socket.item_done()

    def read_output(self):
        top = self.simContext
        top.eval()
        # read outputs
        data = top.getValue("mcdt_data_o")
        val = top.getValue("mcdt_val_o")
        id = top.getValue("mcdt_id_o")
        if val == 1:
            print("data: %8x, val: %0d, id: %0d" %(data, val, id))


    def posedge_clk(self):
        top = self.simContext
        top.eval()
        # self.read_output()
        top.sleep_cycles(5)
        top.setValue("clk_i", 0)
        top.eval()
        top.sleep_cycles(5)
        top.setValue("clk_i", 1)


    def chnl_write(self, id, data):
        top = self.simContext
        self.time = self.time + 5
        if self.time < 10:
            reset_value = 0
        else:
            reset_value = 1
        top.setValue("rstn_i", reset_value)

        if id == 0:
            self.posedge_clk()
            top.setValue("ch0_data_i", data)
            top.setValue("ch0_valid_i", 1)
            self.posedge_clk()
            top.setValue("ch0_data_i", 0)
            top.setValue("ch0_valid_i", 0)
        elif id == 1:
            self.posedge_clk()
            top.setValue("ch1_data_i", data)
            top.setValue("ch1_valid_i", 1)
            self.posedge_clk()
            top.setValue("ch1_data_i", 0)
            top.setValue("ch1_valid_i", 0)
        elif id == 2:
            self.posedge_clk()
            top.setValue("ch2_data_i", data)
            top.setValue("ch2_valid_i", 1)
            self.posedge_clk()
            top.setValue("ch2_data_i", 0)
            top.setValue("ch2_valid_i", 0)


class Monitor(uvm_monitor):
    
    def __init__(self, env, name):
        super().__init__(env, name)

        self.simContext = config_db['simContext']
        self.run_thread = self.env.process(self.run())


    def read_output(self):
        top = self.simContext
        top.eval()
        # read outputs
        data = top.getValue("mcdt_data_o")
        val = top.getValue("mcdt_val_o")
        id = top.getValue("mcdt_id_o")
        if val == 1:
            print("data: %8x, val: %0d, id: %0d" %(data, val, id))


    def run(self):
        cycle_event = config_db["cycle_event"]
        while True:
            yield self.env.process(cycle_event.wait())
            self.read_output()


class DUT(Module):

    def __init__(self, env, name):
        super().__init__(env, name)


    def getSimContext(self, dut_path, top_module_file_name, sim_folder):
        s = sim(dut_path, top_module_file_name, sim_folder)
        s.getHandle('sim_wrapper')
        return s

        
class Top(Module):
    def __init__(self, env, name):
        super().__init__(env, name)

        self.dut = DUT(self.env, 'dut')

        dut_path = "./../hdl/"
        top_module_file_name = "mcdt.v"
        sim_folder = "simulation"
        self.simContext = self.dut.getSimContext(dut_path, top_module_file_name, sim_folder)

        config_db["simContext"] = self.simContext
        config_db["cycle_event"] = Event(self.env)

        self.monitor = Monitor(self.env, 'mon')
        self.sequencer = Sequencer(self.env, 'sqr')
        self.driver = Driver(self.env, 'drv')

        self.driver.socket.bind(self.sequencer.socket)


import time

def test_mcdt():
    # 创建一个 env 实例
    env = simpy.Environment()

    # 创建顶层模块 top，传入 env
    top = Top(env, 'top')

    seq = Sequence(env, 'seq')
    
    seq.start(top.sequencer)
    t1 = time.time()

    # 运行仿真
    env.run()

    t2 = time.time()
    print("t2-t1", t2-t1)


def basic_test():

    test_mcdt()
    pass


if __name__ == '__main__':
    basic_test()
