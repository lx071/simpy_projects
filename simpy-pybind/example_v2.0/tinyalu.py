from utils import *
import simpy
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


class Sequence(uvm_sequence):

    def __init__(self, env, name):
        super().__init__(env, name)


    def body(self):
        # in1 = [random.randrange(0, 20) for i in range(20)]
        # in2 = [random.randrange(0, 20) for i in range(20)]
        for i in range(20):
            item = self.create_item()
            self.start_item(item, self.m_sequencer)
            payload = {
                'in1': i,
                'in2': i,
                'op': 1,
            }
            item.set_data_ptr(payload)
            yield self.env.process(self.finish_item(item))
        
        item = self.create_item()
        self.start_item(item, self.m_sequencer)
        payload = {
            'exit': True
        }
        item.set_data_ptr(payload)
        yield self.env.process(self.finish_item(item))


class Sequencer(uvm_sequencer):
    
    def __init__(self, env, name):
        super().__init__(env, name)


class Driver(uvm_driver):

    def __init__(self, env, name):
        super().__init__(env, name)

        self.dut = config_db['dut']

        # self.run_thread = self.env.process(self.run())
        
        self.reset_thread = self.env.process(self.reset())
        self.clk_thread = self.env.process(self.clk())
        
        # self.bfm_thread = self.env.process(self.bfm())

        self.get_item_e = self.env.event()
        self.item_done_e = self.env.event()
        self.exit_e = self.env.event()

        self.eval_e = self.env.event()

        self.input1 = None
        self.input2 = None
        self.op = None
        self.output = None
        self.res = [0] * 20
        self.data = [None]
        self.exit = 0


    def print_attr(self, s):
        clk_value = s.getValue("clk")
        reset_value = s.getValue("reset_n")
        A_value = s.getValue("A")
        B_value = s.getValue("B")
        op_value = s.getValue("op")
        result_value = s.getValue("result")
        start_value = s.getValue("start")
        done_value = s.getValue("done")
        time = s.sc_time_stamp()
        print("time: %0d, clk: %0d, reset_n: %0d, A: %0d, B: %0d, op: %0d, result: %0d, start: %0d, done: %0d" 
                %(time, clk_value, reset_value, A_value, B_value, op_value, result_value, start_value, done_value))


    def run(self):
        trans = uvm_tlm_generic_payload()
        trans.set_data_ptr( self.data )

        while True:
            trans.set_response_status( tlm_response_status.TLM_INCOMPLETE_RESPONSE, self.socket )
            yield self.env.process(self.socket.get_next_item(trans))

            payload = trans.get_data_ptr()[0]
            print("payload:", payload)

            if 'exit' in payload.keys():
                self.exit_e.succeed()
                trans.set_response_status(tlm_response_status.TLM_OK_RESPONSE, self.socket.other_socket)
                return

            self.input1 = payload['in1']
            self.input2 = payload['in2']
            self.op = payload['op']

            self.get_item_e.succeed()
            self.get_item_e = self.env.event()
            yield self.item_done_e
            self.socket.item_done()


    def clk(self):
        top = self.dut.simContext
        io_ports = self.dut.io_ports
        
        clk_value = 0
        top.setValue("clk", 0)
        
        while True:
            if self.exit == 1:
                break

            # if num >= 20:
            #     break
            
            top.setValue("clk", not clk_value)
            clk_value = not clk_value

            # if clk_value:
            #     io_ports["clk"].pos_event.succeed()
            #     io_ports["clk"].pos_event = self.env.event()
            # else:
            #     io_ports["clk"].neg_event.succeed()
            #     io_ports["clk"].neg_event = self.env.event()
            
            io_ports["clk"].edge_event.succeed()
            io_ports["clk"].edge_event = self.env.event()
            yield self.eval_e
    

    def reset(self):
        print("reset")
        top = self.dut.simContext
        io_ports = self.dut.io_ports

        reset_value = 0
        num = 0

        while True:
            if num >= 10:
                break

            yield io_ports["clk"].edge_event
            
            clk_value = top.getValue("clk")
            if clk_value == 0 and reset_value == 0:
                top.setValue("reset_n", 1)
                reset_value = 1
            elif clk_value == 1:
                top.setValue("A", num)
                top.setValue("B", num)
                top.setValue("op", 1)
                num = num + 1
            
            top.eval()
            # top.sleep_cycles(1)
            self.print_attr(top)
            
            self.eval_e.succeed()
            self.eval_e = self.env.event()
            
            pass
        self.exit = 1
        top.deleteHandle()


    # def bfm(self):
    #     top = self.dut.simContext

    #     top.deleteHandle()


class Port:
    def __init__(self, env, name):
        self.xdata, self.value, self.mIOType = None, None, 0
        self.env = env
        self.name = name
        self.pos_event = self.env.event()
        self.neg_event = self.env.event()
        self.edge_event = self.env.event()
        

class DUT(Module):

    def __init__(self, env, name):
        super().__init__(env, name)
        self.io_ports = {}
        self.signal_id = None
        self.simContext = None
        

    def set_attr(self, dut_path, top_module_file_name, sim_folder):

        self.simContext = sim(dut_path, top_module_file_name, sim_folder)
        self.simContext.getHandle('sim_wrapper')
        self.signal_id = self.simContext.signal_id

        for port_name in self.signal_id.keys():
            self.io_ports[port_name] = Port(self.env, port_name)
        
        print("signal_id:", self.signal_id)

        
class Top(Module):
    def __init__(self, env, name):
        super().__init__(env, name)

        self.dut = DUT(self.env, 'dut')

        dut_path = "./hdl/"
        top_module_file_name = "tinyalu.sv"
        sim_folder = "simulation"
        self.dut.set_attr(dut_path, top_module_file_name, sim_folder)

        config_db["dut"] = self.dut

        self.sequencer = Sequencer(self.env, 'sqr')
        self.driver = Driver(self.env, 'drv')

        self.driver.socket.bind(self.sequencer.socket)


def test_tinyalu():
    # 创建一个 env 实例
    env = simpy.Environment()

    # 创建顶层模块 top，传入 env
    top = Top(env, 'top')

    seq = Sequence(env, 'seq')
    seq.start(top.sequencer)

    # 运行仿真
    env.run()


def basic_test():

    test_tinyalu()
    pass


if __name__ == '__main__':
    basic_test()
