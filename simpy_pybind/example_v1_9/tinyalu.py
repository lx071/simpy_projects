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
        self.in1 = []
        self.in2 = []
        self.op = []
        self.res = []

    
    def src_in(self, in1, in2, op_, res_):
        self.in1 = in1
        self.in2 = in2
        self.op = op_
        self.res = res_


    def body(self):
        # in1 = [random.randrange(0, 20) for i in range(20)]
        # in2 = [random.randrange(0, 20) for i in range(20)]
        for i in range(20):
            item = self.create_item()
            self.start_item(item, self.m_sequencer)
            payload = {
                'in1': self.in1[i],
                'in2': self.in2[i],
                'op': self.op[i]
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

        self.simContext = config_db['simContext']

        self.run_thread = self.env.process(self.run())
        self.bfm_thread = self.env.process(self.bfm())

        self.get_item_e = self.env.event()
        self.item_done_e = self.env.event()
        self.exit_e = self.env.event()

        self.input1 = None
        self.input2 = None
        self.op = None
        self.output = None
        self.res = [0] * 20
        self.data = [None]


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


    def bfm(self):
        top = self.simContext

        num = 0
        clk_value = 0
        reset_value = 0

        top.setValue("clk", 0)
        top.setValue("reset_n", 0)

        while True:
            # if num >= 20:
            #     break
            
            top.setValue("clk", not clk_value)
            clk_value = not clk_value

            if clk_value == 0:
                top.setValue("reset_n", 1)
                reset_value = 1
            
            if clk_value == 1:
                if reset_value == 0:
                    top.setValue("start", 0)
                    top.setValue("A", 0)
                    top.setValue("B", 0)
                    top.setValue("op", 0)
                else:
                    start_value = top.getValue("start")
                    done_value = top.getValue("done")
                    if start_value == 1 and done_value == 1:
                        top.setValue("start", 0)
                        self.item_done_e.succeed()
                        self.item_done_e = self.env.event()  
                    elif start_value == 0 and done_value == 0:
                        yield self.get_item_e | self.exit_e
                        if self.exit_e.triggered:
                            break
                        top.setValue("start", 1)
                        top.setValue("op", self.op)
                        top.setValue("A", self.input1)
                        top.setValue("B", self.input2)
                        num = num + 1

            top.eval()
            
            config_db["cycle_event"].set()
            yield self.env.timeout(0)
            config_db["cycle_event"].clear()
            yield self.env.timeout(0)

            top.sleep_cycles(1)

        top.deleteHandle()


class Monitor(uvm_monitor):
    
    def __init__(self, env, name):
        super().__init__(env, name)

        self.simContext = config_db['simContext']
        self.bfm_thread = self.env.process(self.bfm())


    def bfm(self):
        top = self.simContext

        cycle_event = config_db["cycle_event"]

        while True:
            yield self.env.process(cycle_event.wait())
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

        dut_path = "./hdl/"
        top_module_file_name = "tinyalu.sv"
        sim_folder = "simulation"
        self.simContext = self.dut.getSimContext(dut_path, top_module_file_name, sim_folder)

        config_db["simContext"] = self.simContext
        config_db["cycle_event"] = Event(self.env)

        self.monitor = Monitor(self.env, 'mon')
        self.sequencer = Sequencer(self.env, 'sqr')
        self.driver = Driver(self.env, 'drv')

        self.driver.socket.bind(self.sequencer.socket)


def test_tinyalu(in1, in2, op, res):
    # 创建一个 env 实例
    env = simpy.Environment()

    # 创建顶层模块 top，传入 env
    top = Top(env, 'top')

    seq = Sequence(env, 'seq')
    seq.src_in(in1, in2, op, res)

    seq.start(top.sequencer)

    # 运行仿真
    env.run()


def basic_test():
    in1 = [i for i in range(20)]
    in2 = [i for i in range(20)]
    op = [1 for i in range(20)]
    res = [0 for i in range(20)]
    test_tinyalu(in1, in2, op, res)


# in1 = [0, 1, 2, ..., 99]
# in2 = [0, 1, 2, ..., 99]
# op = [1, 1, 1, ..., 1]
def multi_test():

    import time
    start = time.time()

    in1 = []
    in2 = []
    op = []
    res = []

    for i in range(100):
        in1.append(i)
        in2.append(i)
        op.append(1)
        res.append(i + i)
    
    batch = 4

    step = len(res) // batch
    l = len(res)

    # 激励数据分为 4组，多进程处理
    input1 = [in1[i:i+step] for i in range(0, l, step)] # [0, 25], [25, 50], [50, 75], [75, 100]
    input2 = [in2[i:i+step] for i in range(0, l, step)]
    op_ = [op[i:i+step] for i in range(0, l, step)]
    res_ = [res[i:i+step] for i in range(0, l, step)]

    multi = 1
    for i in range(len(op_)):
        input1[i] = input1[i] * multi
        input2[i] = input2[i] * multi
        op_[i] = op_[i] * multi
        res_[i] = res_[i] * multi

    from multiprocessing import Process

    start = time.time()

    lst = []
    interp = [None] * batch
    for x in range(batch):
        i = x % batch
        # test_alu(input1[i], input2[i], op_[i], res_[i])
        p = Process(target = test_tinyalu, args = (input1[i], input2[i], op_[i], res_[i]))
        lst.append(p)
        p.start()
    for p in lst:
        p.join()

    end = time.time()

    print("processing: {}".format(end - start))


if __name__ == '__main__':
    basic_test()
