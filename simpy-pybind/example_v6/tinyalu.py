from utils.tlm_utils import *
from utils.harness_utils import sim
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


class Sequence(Sequence_Item):

    def __init__(self, env, name):
        super().__init__(name)
        self.env = env


    def start(self, sequencer, parent_sequence = None):
        self.m_sequencer = sequencer
        self.set_item_context(parent_sequence, sequencer)
        self.env.process(self.body())
        

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
        yield self.env.process(self.finish_item(item))
        yield self.env.timeout(0)


    def create_item(self):
        trans = Generic_Payload()
        payload = {
            'in1': 0,
            'in2': 0,
            'op': 0,
        }
        trans.set_data_ptr(payload)
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

        yield self.env.process(sequencer.send_request(self, item))
        yield self.env.process(sequencer.wait_for_item_done(self, -1))
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
        self.m_sequencer.wait_for_item_done(self, transaction_id)


class Sequencer(Module):
    
    m_id = 0

    def __init__(self, env, name):
        super().__init__(env, name)
        self.sequence_item_requested = 0
        self.get_next_item_called = 0

        self.socket = Socket(self)

        self.socket.register_get_next_item(self.get_next_item)
        self.socket.register_item_done(self.item_done)

        # uvm_tlm_fifo #(REQ) m_req_fifo;
        self.store = simpy.Store(env, capacity=1)

        self.reg_sequences = []

        Sequencer.m_id += 1
        self.m_sequencer_id = Sequencer.m_id

        self.m_wait_for_item_sequence_id = 0
        self.m_wait_for_item_transaction_id = 0

        self.item_done_e = self.env.event()

    def get_next_item(self, trans):
        ptr = trans.get_data_ptr()

        if self.get_next_item_called == 1:
            # uvm_report_error(get_full_name(), "Get_next_item called twice without item_done or get in between", UVM_NONE);
            print("ERROR:", "Get_next_item called twice without item_done or get in between")
        
        # if not self.sequence_item_requested:
        #     m_select_sequence()

        # Set flag indicating that the item has been requested to ensure that item_done or get
        # is called between requests
        self.sequence_item_requested = 1
        self.get_next_item_called = 1
        # self.m_req_fifo.peek(t)
        
        item = yield self.store.get()
        
        ptr[0] = item.get_data_ptr()
        trans.set_response_status(tlm_response_status.TLM_OK_RESPONSE, self.socket.other_socket)
    

    def item_done(self, item = None):
        self.sequence_item_requested = 0
        self.get_next_item_called = 0

        self.item_done_e.succeed()
        self.item_done_e = self.env.event()  
        if item != None:
            self.put_response(item)

    def send_request(self, sequence_ptr, t: Generic_Payload, rerandomize = 0):
        t.set_sequencer(self)
        # if self.m_req_fifo.try_put(t) != 1:
        yield self.store.put(t)
        #     # uvm_report_fatal(get_full_name(), "Concurrent calls to get_next_item() not supported. Consider using a semaphore to ensure that concurrent processes take turns in the driver", UVM_NONE);
        #     print("Concurrent calls to get_next_item() not supported. Consider using a semaphore to ensure that concurrent processes take turns in the driver")
        #     raise ResponseError("Concurrent calls to get_next_item() not supported. Consider using a semaphore to ensure that concurrent processes take turns in the driver")

    def put_response(self, t: Sequence_Item):
        sequence_ptr = self.reg_sequences[t.get_sequence_id()]
        sequence_ptr.put_response(t)

    def wait_for_item_done(self, sequence_ptr, transaction_id):
        # sequence_id = sequence_ptr.m_get_sqr_sequence_id(self.m_sequencer_id, 1)
        # self.m_wait_for_item_sequence_id = -1
        # self.m_wait_for_item_transaction_id = -1
        yield self.item_done_e
        pass


class Driver(Module):

    def __init__(self, env, name):
        super().__init__(env, name)

        self.simContext = config_db['simContext']

        # 创建 socket，与 sequencer 进行连接
        self.socket = Socket(self)
        
        self.run_thread = self.env.process(self.run())
        self.bfm_thread = self.env.process(self.bfm())

        self.get_item = self.env.event()
        self.item_done = self.env.event()
        self.exit = self.env.event()

        self.input1 = None
        self.input2 = None
        self.op = None
        self.output = None
        self.res = [0] * 20
        self.data = [None]


    def run(self):
        trans = Generic_Payload()
        trans.set_data_ptr( self.data )
        trans.set_response_status( tlm_response_status.TLM_INCOMPLETE_RESPONSE, self.socket )
        yield self.env.process(self.socket.get_next_item(trans))

        payload = trans.get_data_ptr()[0]
        print("payload:", payload)

        self.input1 = payload['in1']
        self.input2 = payload['in2']
        self.op = payload['op']

        self.get_item.succeed()
        self.get_item = self.env.event()
        yield self.item_done
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

        self.driver.socket.bind(self.sequencer.socket)


def test_tinyalu():
    # 创建一个 env 实例
    env = simpy.Environment()

    # 创建顶层模块 top，传入 env
    top = Top(env, 'top')

    sequence = Sequence(env, 'seq')
    sequence.start(top.sequencer)

    # 运行仿真
    env.run()


def basic_test():

    test_tinyalu()
    pass


if __name__ == '__main__':
    basic_test()
