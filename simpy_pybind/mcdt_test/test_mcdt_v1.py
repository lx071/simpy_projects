import sys
sys.path.append("../")

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
        # in1 = [random.randrange(0, 20) for i in range(20)]
        # in2 = [random.randrange(0, 20) for i in range(20)]
        for i in range(20):
            item = self.create_item()
            self.start_item(item, self.m_sequencer)
            trans = chnl_trans(i % 3, 0)
            payload = {
                'data': trans
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

        self.ch_id = 0
        self.data = [None]
        self.pkt_data = 0


    def run(self):
        trans = uvm_tlm_generic_payload()
        trans.set_data_ptr( self.data )

        while True:
            trans.set_response_status( tlm_response_status.TLM_INCOMPLETE_RESPONSE, self.socket )
            yield self.env.process(self.socket.get_next_item(trans))

            payload = trans.get_data_ptr()[0]

            if 'exit' in payload.keys():
                self.exit_e.succeed()
                trans.set_response_status(tlm_response_status.TLM_OK_RESPONSE, self.socket.other_socket)
                return

            self.ch_id = payload['data'].ch_id
            self.pkt_data = payload['data'].data
            
            self.get_item_e.succeed()
            self.get_item_e = self.env.event()
            yield self.item_done_e
            self.socket.item_done()


    def posedge_clk(self):
        top = self.simContext
        top.eval()
        # read outputs
        data = top.getValue("mcdt_data_o")
        val = top.getValue("mcdt_val_o")
        id = top.getValue("mcdt_id_o")
        if val == 1:
            print("data: %8x, val: %0d, id: %0d" %(data, val, id))

        top.sleep_cycles(5)
        top.setValue("clk_i", 0)
        top.eval()
        top.sleep_cycles(5)
        top.setValue("clk_i", 1)


    def chnl_write(self, id, data):
        top = self.simContext
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


    def bfm(self):
        top = self.simContext

        num = 0
        clk_value = 0
        reset_value = 0
        time = 0

        top.setValue("clk_i", 0)
        top.setValue("rstn_i", 0)
        top.setValue("ch0_data_i", 0)
        top.setValue("ch0_valid_i", 0)
        top.setValue("ch1_data_i", 0)
        top.setValue("ch1_valid_i", 0)
        top.setValue("ch2_data_i", 0)
        top.setValue("ch2_valid_i", 0)

        top.eval()
        
        while True:
            top.sleep_cycles(5)
            time = time + 5

            top.setValue("clk_i", not clk_value)
            clk_value = not clk_value
            if clk_value == 0:
                if time < 30:
                    reset_value = 0
                else:
                    reset_value = 1
                top.setValue("rstn_i", reset_value)
                  
            if clk_value == 1:
                if reset_value == 0:
                    top.setValue("ch0_data_i", 0)
                    top.setValue("ch0_valid_i", 0)
                    top.setValue("ch1_data_i", 0)
                    top.setValue("ch1_valid_i", 0)
                    top.setValue("ch2_data_i", 0)
                    top.setValue("ch2_valid_i", 0)
                else:
                    yield self.get_item_e | self.exit_e
                    if self.exit_e.triggered:
                        print("exit break")
                        break
                    num = len(self.pkt_data)
                    for i in range(num):
                        self.chnl_write(self.ch_id, self.pkt_data[i])
                    self.item_done_e.succeed()
                    self.item_done_e = self.env.event() 
        top.deleteHandle()

        # config_db["cycle_event"].set()
        # yield self.env.timeout(0)
        # config_db["cycle_event"].clear()
        # yield self.env.timeout(0)

        # top.sleep_cycles(1)


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
        top_module_file_name = "mcdt.v"
        sim_folder = "simulation"
        self.simContext = self.dut.getSimContext(dut_path, top_module_file_name, sim_folder)

        config_db["simContext"] = self.simContext
        config_db["cycle_event"] = Event(self.env)

        self.monitor = Monitor(self.env, 'mon')
        self.sequencer = Sequencer(self.env, 'sqr')
        self.driver = Driver(self.env, 'drv')

        self.driver.socket.bind(self.sequencer.socket)


def test_mcdt():
    # 创建一个 env 实例
    env = simpy.Environment()

    # 创建顶层模块 top，传入 env
    top = Top(env, 'top')

    seq = Sequence(env, 'seq')
    seq.start(top.sequencer)

    # 运行仿真
    env.run()


def basic_test():

    test_mcdt()
    pass


if __name__ == '__main__':
    basic_test()
