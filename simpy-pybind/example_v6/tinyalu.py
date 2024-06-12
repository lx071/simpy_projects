from utils.tlm_utils import *
from utils.harness_utils import sim
import simpy
import random
import queue

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


class Sequence(Sequence_Item):

    def __init__(self, env, name):
        super().__init__(env, name)
        
        # 创建 socket
        self.socket = Socket(self)

        self.m_sequencer = None

        # 创建事件 event
        self.init_event = self.env.event()
        self.item_done = self.env.event()

        # 创建进程，用于向 driver 传输数据
        # process 函数：传入 ProcessGenerator，返回 Process(self, generator)
        self.trans2drv_thread = self.env.process(self.transport2drv())

        self.in1 = []
        self.in2 = []
        self.op = []
        self.res = []


    def start(self, sequencer, parent_sequence = None):
        self.m_sequencer = sequencer
        self.set_item_context(parent_sequence, sequencer);
        

    def body(self):
        # in1 = [random.randrange(0, 20) for i in range(20)]
        # in2 = [random.randrange(0, 20) for i in range(20)]
        item = self.create_item()
        self.start_item(item, self.m_sequencer)

        payload = {
            'in1': 2,
            'in2': 3,
            'op': 1,
        }
        item.set_data_ptr(payload)
        
        self.finish_item(item)

    def create_item(self):
        trans = Generic_Payload()
        payload = {
            'in1': 0,
            'in2': 0,
            'op': 0,
        }
        trans.set_data_ptr( payload )
        trans.set_response_status( tlm_response_status.TLM_INCOMPLETE_RESPONSE, self.socket ); # Mandatory initial value
        return trans
    

    def start_item(self, item, sequencer):
        item.set_item_context(self, sequencer)
        # self.m_sequencer.wait_for_grant(this, set_priority)
        '''a user-definable callback task that is called ~on the parent sequence~ after the sequencer has selected this sequence, and before the item is randomized.''' 
        # pre_do(1) 
        pass


    def finish_item(self, item):

        sequencer = item.get_sequencer()
        if sequencer == None:
            # uvm_report_fatal("STRITM", "sequence_item has null sequencer", UVM_NONE);
            print("FATAL:", "sequence_item has null sequencer")
            raise ResponseError("sequence_item has null sequencer")
        
        '''a user-definable callback function that is called after the sequence item has been randomized, and just before the item is sent to the driver.'''        
        # mid_do(item); 
        sequencer.send_request(self, item)
        sequencer.wait_for_item_done(self, -1)
        '''a user-definable callback function that is called after the driver has indicated that it has completed the item, using either this item_done or put methods.'''
        # post_do(item);


    def send_request(self, request, rerandomize = 0):
        if self.m_sequencer == None:
            # uvm_report_fatal("SSENDREQ", "Null m_sequencer reference", UVM_NONE);
            print("FATAL:", "Null m_sequencer reference")
            raise ResponseError("Null m_sequencer reference")
        self.m_sequencer.send_request(self, request, rerandomize)


    def wait_for_item_done(self, transaction_id = -1):
        if self.m_sequencer == None:
            # uvm_report_fatal("WAITITEMDONE", "Null m_sequencer reference", UVM_NONE);
            print("FATAL:", "Null m_sequencer reference")
            raise ResponseError("Null m_sequencer reference")
        self.m_sequencer.wait_for_item_done(self, transaction_id);


    # 数据初始化；触发 init_event 事件
    def src_in(self, in1, in2, op_, res_):
        self.in1 = in1
        self.in2 = in2
        self.op = op_
        self.res = res_
        self.init_event.succeed()

    
    # 向 driver 传送数据，in1、in2、op
    def transport2drv(self):

        # 等待 数据初始化
        yield self.init_event
        
        trans = Generic_Payload()
        delay = 1
        
        for i in range(len(self.op)):
            
            payload = {
                'in1': self.in1[i],
                'in2': self.in2[i],
                'op': self.op[i],
            }

            trans.set_data_ptr( payload )
            trans.set_response_status( tlm_response_status.TLM_INCOMPLETE_RESPONSE, self.socket ); # Mandatory initial value

            # 取出一组数据，发送给 alu
            yield self.env.process(self.socket.b_transport(trans, delay))

            # Realize the delay annotated onto the transport call
            yield self.env.timeout(0)

        payload = {
            'exit': True
        }
        trans.set_data_ptr( payload )
        trans.set_response_status( tlm_response_status.TLM_INCOMPLETE_RESPONSE, self.socket ); # Mandatory initial value
        yield self.env.process(self.socket.b_transport(trans, delay))
        
        # Realize the delay annotated onto the transport call
        yield self.env.timeout(0)


class Sequencer(Module):
    def __init__(self, env, name):
        super().__init__(env, name)

        self.socket = Socket(self)
        self.socket.register_b_transport(self.get_next_item)
        self.m_req_fifo = Queue()

    def get_next_item():
        pass

    def item_done():
        pass

    def send_request(self, sequence_ptr, t: Sequence_Item, rerandomize = 0):
        t.set_sequencer(self)
        m_req_fifo
        pass

class Driver(Module):

    def __init__(self, env, name):
        super().__init__(env, name)

        self.simContext = config_db['simContext']

        # 创建 socket，与 sequencer 进行连接
        self.socket = Socket(self)
        
        # 函数注册，用于从 sequencer 接收数据
        self.socket.register_b_transport(self.recv_from_seqr)
        
        self.bfm_thread = self.env.process(self.bfm())

        self.get_item = self.env.event()
        self.item_done = self.env.event()
        self.exit = self.env.event()

        self.input1 = None
        self.input2 = None
        self.op = None
        self.output = None
        self.res = [0] * 20


    # 从 sequencer 接收数据，由 sequencer.socket.b_transport(trans, delay) 调用
    def recv_from_seqr(self, trans, delay):
        payload = trans.get_data_ptr()
        if 'exit' in payload.keys():
            self.exit.succeed()
            trans.set_response_status(tlm_response_status.TLM_OK_RESPONSE, self.socket.other_socket)
            return
        self.input1 = payload['in1']
        self.input2 = payload['in2']
        self.op = payload['op']
        # print(self.input1, self.input2, self.op)

        # 数据接收完毕
        self.get_item.succeed()
        self.get_item = self.env.event()
        yield self.item_done 
        trans.set_response_status(tlm_response_status.TLM_OK_RESPONSE, self.socket.other_socket)
        yield self.env.timeout(0)


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
                        self.item_done.succeed()
                        self.item_done = self.env.event()  
                    elif start_value == 0 and done_value == 0:
                        yield self.get_item | self.exit
                        if self.exit.triggered:
                            break
                        top.setValue("start", 1)
                        top.setValue("op", self.op)
                        top.setValue("A", self.input1)
                        top.setValue("B", self.input2)
                        num = num + 1

            top.eval()
            
            A_value = top.getValue("A")
            B_value = top.getValue("B")
            op_value = top.getValue("op")
            result_value = top.getValue("result")
            start_value = top.getValue("start")
            done_value = top.getValue("done")
            time = top.sc_time_stamp()
            print("time: %0d, clk: %0d, reset_n: %0d, A: %0d, B: %0d, op: %0d, result: %0d, start: %0d, done: %0d" 
                    %(time, clk_value, reset_value, A_value, B_value, op_value, result_value, start_value, done_value))

            top.sleep_cycles(1)

        top.deleteHandle()


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

        self.sequencer = Sequencer(self.env, 'sqr')
        self.driver = Driver(self.env, 'drv')

        self.sequencer.socket.bind(self.driver.socket)


def test_tinyalu():
    # 创建一个 env 实例
    env = simpy.Environment()

    # 创建顶层模块 top，传入 env
    top = Top(env, 'top')

    sequence = Sequence(env, 'seq')
    sequence.start(top.sequencer)

    # 运行仿真
    # env.run()


def basic_test():

    test_tinyalu()
    pass


if __name__ == '__main__':
    basic_test()
