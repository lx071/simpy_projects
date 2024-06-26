from utils import *
import simpy
import random
from simpy.events import AnyOf, AllOf, Event

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


def RisingEdge(env, io_ports, pin, cycle_event):
    value = io_ports[pin].getValue()
    while True:
        yield env.process(io_ports["clk"].event.wait())
        newValue = io_ports[pin].getValue()
        if (value == 0 and newValue != value):
            break
        value = newValue
        cycle_event.set()
        cycle_event.clear()


def FallingEdge(env, io_ports, pin, cycle_event):
    value = io_ports[pin].getValue()
    while True:
        yield env.process(io_ports["clk"].event.wait())
        newValue = io_ports[pin].getValue()
        if (newValue == 0 and newValue != value):
            break
        value = newValue
        cycle_event.set()
        cycle_event.clear()
       

class Port:
    def __init__(self, env, name, simContext, io_port = 0):
        self.env = env
        self.name = name
        self.mIOType = io_port
        self.simContext = simContext
        self.pos_event = self.env.event()
        self.neg_event = self.env.event()
        self.event = Event(env)
        self.value = self.simContext.getValue(self.name)


    def setValue(self, value):
        if self.mIOType == 1:
            raise Exception("output type is not allowed to setValue")
        if value != self.value:
            self.simContext.setValue(self.name, value)
            self.value = value
        self.event.set()
        self.event.clear()

    
    def getValue(self):
        if self.mIOType == 1:   # output
            self.value = self.simContext.getValue(self.name)
        return self.value


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

        self.bfm_thread = self.env.process(self.bfm_process())
        self.reset_thread = self.env.process(self.reset_process())
        self.clk_thread = self.env.process(self.clk_process())
        self.run_thread = self.env.process(self.run())
        
        self.item_done_e = self.env.event()

        self.reset_e = Event(env)
        self.bfm_e = Event(env)

        # self.cycle_event = AllOf(self.env, [self.reset_e.event, self.bfm_e.event])

        self.data = [None]
        self.exit_e = self.env.event()

        self.store = simpy.Store(env, capacity=1)


    def print_attr(self, top, io_ports):
        clk_value = io_ports["clk"].getValue()
        reset_value = io_ports["reset_n"].getValue()
        A_value = io_ports["A"].getValue()
        B_value = io_ports["B"].getValue()
        op_value = io_ports["op"].getValue()
        result_value = io_ports["result"].getValue()
        start_value = io_ports["start"].getValue()
        done_value = io_ports["done"].getValue()
        time = top.sc_time_stamp()
        print("time: %0d, clk: %0d, reset_n: %0d, A: %0d, B: %0d, op: %0d, result: %0d, start: %0d, done: %0d" 
                %(time, clk_value, reset_value, A_value, B_value, op_value, result_value, start_value, done_value))


    # run_phase: get_next_item + item_done
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
                break

            yield self.store.put(payload)
            yield self.item_done_e
            self.socket.item_done()


    def clk_process(self):
        top = self.dut.simContext
        io_ports = self.dut.io_ports
        
        clk_value = 0
        io_ports["clk"].setValue(0)
        
        cycle = 0
        while True:
            yield self.env.timeout(0)
            io_ports["clk"].setValue(not clk_value)
            clk_value = not clk_value

            yield (self.reset_e.event & self.bfm_e.event) | self.exit_e
            if self.exit_e.triggered:
                break
            # yield self.cycle_event
            # self.cycle_event = AllOf(self.env, [self.reset_e.event, self.bfm_e.event])

            top.eval()
            top.sleep_cycles(1)

            self.print_attr(top, io_ports)
            cycle += 1
            
        top.deleteHandle()
    

    def reset_process(self):
        io_ports = self.dut.io_ports
        
        io_ports["reset_n"].setValue(0)
        yield self.env.process(FallingEdge(self.env, self.dut.io_ports, "clk", self.reset_e))
        self.reset_e.set()
        io_ports["reset_n"].setValue(1)


    def bfm_process(self):
        io_ports = self.dut.io_ports

        while True:
            yield self.env.process(RisingEdge(self.env, io_ports, "clk", self.bfm_e))

            reset_value = io_ports["reset_n"].getValue()
            if reset_value == 0:
                io_ports["start"].setValue(0)
                io_ports["A"].setValue(0)
                io_ports["B"].setValue(0)
                io_ports["op"].setValue(0)
            else:
                start_value = io_ports["start"].getValue()
                done_value = io_ports["done"].getValue()
                if start_value == 1 and done_value == 1:
                    io_ports["start"].setValue(0)
                    self.item_done_e.succeed()
                    self.item_done_e = self.env.event()  
                elif start_value == 0 and done_value == 0:
                    payload = yield self.store.get()
                    io_ports["start"].setValue(1)
                    io_ports["A"].setValue(payload['in1'])
                    io_ports["B"].setValue(payload['in2'])
                    io_ports["op"].setValue(payload['op'])

            self.bfm_e.set()
            self.bfm_e.clear()


class DUT(Module):

    def __init__(self, env, name):
        super().__init__(env, name)
        self.io_ports = {}
        # self.signal_id = None
        self.simContext = None
        

    def set_attr(self, dut_path, top_module_file_name, sim_folder):

        self.simContext = sim(dut_path, top_module_file_name, sim_folder)
        self.simContext.getHandle('sim_wrapper')
        # self.signal_id = self.simContext.signal_id
        input_ports_name = self.simContext.input_ports_name
        output_ports_name = self.simContext.output_ports_name

        for in_port_name in input_ports_name:
            self.io_ports[in_port_name] = Port(self.env, in_port_name, self.simContext, 0)
        for out_port_name in output_ports_name:
            self.io_ports[out_port_name] = Port(self.env, out_port_name, self.simContext, 1)
        
        print("input_ports_name:", input_ports_name)
        print("output_ports_name:", output_ports_name)
        
        
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
