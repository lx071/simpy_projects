import sys
sys.path.append("../../")

import simpy
from utils import *
import random

"""
    input [7:0] A,
    input [7:0] B,
    input [2:0] op,
    input clk,
    input reset_n,
    input start,
    output done,
    output [15:0] result
"""

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


class Sequence(uvm_sequence):

    def __init__(self, env, name):
        super().__init__(env, name)


    def body(self):
        # in1 = [random.randrange(0, 20) for i in range(20)]
        # in2 = [random.randrange(0, 20) for i in range(20)]
        for i in range(10000):
            item = self.create_item()
            self.start_item(item, self.m_sequencer)
            payload = {
                'in1': i,
                'in2': i,
                'op': 1,
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

    def init_value(self):
        top = self.simContext
        top.setValue("start", 0)
        top.setValue("A", 0)
        top.setValue("B", 0)
        top.setValue("op", 0)

    def read_output(self):
        top = self.simContext
        clk_value = top.getValue("clk")
        reset_value = top.getValue("reset_n")
        A_value = top.getValue("A")
        B_value = top.getValue("B")
        op_value = top.getValue("op")
        result_value = top.getValue("result")
        start_value = top.getValue("start")
        done_value = top.getValue("done")
        time = top.sc_time_stamp()
        print("time: %0d, clk: %0d, reset_n: %0d, A: %0d, B: %0d, op: %0d, result: %0d, start: %0d, done: %0d" 
                %(time, clk_value, reset_value, A_value, B_value, op_value, result_value, start_value, done_value))

    def posedge_clk(self):
        top = self.simContext
        top.eval()
        # self.read_output()
        top.sleep_cycles(5)
        top.setValue("clk", 0)
        top.eval()
        top.sleep_cycles(5)
        top.setValue("clk", 1)

    def run(self):
        trans = uvm_tlm_generic_payload()
        trans.set_data_ptr( self.data )

        while True:
            trans.set_response_status( tlm_response_status.TLM_INCOMPLETE_RESPONSE, self.socket )
            yield self.env.process(self.socket.get_next_item(trans))

            payload = trans.get_data_ptr()[0]

            input1 = payload['in1']
            input2 = payload['in2']
            op = payload['op']
            self.drive_transfer(op, input1, input2)

            self.socket.item_done()

    def drive_transfer(self, op, input1, input2):
        top = self.simContext
        self.time = self.time + 5
        if self.time < 10:
            reset_value = 0
        else:
            reset_value = 1
        top.setValue("reset_n", reset_value)
        
        self.posedge_clk()
        top.setValue("start", 1)
        top.setValue("op", op)
        top.setValue("A", input1)
        top.setValue("B", input2)


class Monitor(uvm_monitor):
    
    def __init__(self, env, name):
        super().__init__(env, name)

        self.simContext = config_db['simContext']
        self.run_thread = self.env.process(self.run())

    def read_output(self):
        top = self.simContext
        # read outputs
        clk_value = top.getValue("clk")
        reset_value = top.getValue("reset_n")
        A_value = top.getValue("A")
        B_value = top.getValue("B")
        op_value = top.getValue("op")
        result_value = top.getValue("result")
        start_value = top.getValue("start")
        done_value = top.getValue("done")
        time = top.sc_time_stamp()
        print("time: %0d, clk: %0d, reset_n: %0d, A: %0d, B: %0d, op: %0d, result: %0d, start: %0d, done: %0d" 
                %(time, clk_value, reset_value, A_value, B_value, op_value, result_value, start_value, done_value))


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
        top_module_file_name = "tinyalu.sv"
        sim_folder = "simulation"
        self.simContext = self.dut.getSimContext(dut_path, top_module_file_name, sim_folder)

        config_db["simContext"] = self.simContext
        config_db["cycle_event"] = Event(self.env)

        self.monitor = Monitor(self.env, 'mon')
        self.sequencer = Sequencer(self.env, 'sqr')
        self.driver = Driver(self.env, 'drv')

        self.driver.socket.bind(self.sequencer.socket)


import time

def test_tinyalu():
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

if __name__ == '__main__':
    test_tinyalu()
