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


class Initiator(Module):

    def __init__(self, env, name):
        super().__init__(env, name)
        
        # 创建 socket
        self.socket = Socket()

        # 函数注册，用于从 alu 接收数据
        self.socket.register_transport(self.recv_from_alu)

        # 创建事件 event
        self.init_event = self.env.event()
        self.item_done = self.env.event()

        # 创建进程，用于向 alu 传输数据
        # process 函数：传入 ProcessGenerator，返回 Process(self, generator)
        self.trans2alu_thread = self.env.process(self.transport2alu())

        self.in1 = []
        self.in2 = []
        self.op = []
        self.res = []

    # 数据初始化；触发 init_event 事件
    def src_in(self, in1, in2, op_, res_):
        self.in1 = in1
        self.in2 = in2
        self.op = op_
        self.res = res_
        self.init_event.succeed()

    
    # 向 alu 传送数据，in1、in2、op
    def transport2alu(self):

        # 等待 数据初始化
        yield self.init_event

        for i in range(len(self.op)):
            payload = {
                'in1': self.in1[i],
                'in2': self.in2[i],
                'op': self.op[i],
            }
            # 取出一组数据，发送给 alu
            self.socket.transport(payload, 1)

            # 等待 alu 处理完 item
            yield self.item_done

        payload = {
            'exit': True
        }
        self.socket.transport(payload, 1)


    # 从 alu 接收到信息，触发 item_done 事件
    def recv_from_alu(self, payload, delay):
        if payload['item_done']:
            self.item_done.succeed()
            self.item_done = self.env.event()


class ALU(Module):

    def __init__(self, env, name):
        super().__init__(env, name)

        # 创建 socket，与 init 进行连接
        self.socket = Socket()
        
        # 函数注册，用于从 init 接收数据
        self.socket.register_transport(self.recv_from_init)

        self.get_item = self.env.event()
        self.item_done = self.env.event()
        self.exit = self.env.event()

        self.dut_thread = self.env.process(self.dut())
        self.trans2init_thread = self.env.process(self.transport2init())        

        self.input1 = None
        self.input2 = None
        self.op = None
        self.output = None
        self.res = [0] * 20

    # 向 init 发送 item_done 信息
    def transport2init(self):
        while True:
            yield self.item_done
            payload = {
                'item_done': True
            }
            self.socket.transport(payload, 1)

    # 从 init 接收数据，由 init.socket.transport(payload, 1) 调用
    def recv_from_init(self, payload, delay):
        if 'exit' in payload.keys():
            self.exit.succeed()
            return
        self.input1 = payload['in1']
        self.input2 = payload['in2']
        self.op = payload['op']
        # print(self.input1, self.input2, self.op)

        # 数据接收完毕
        self.get_item.succeed()
        # yield self.env.timeout(1)
        self.get_item = self.env.event()


    def dut(self):
        dut_path = "./hdl/"
        top_module_file_name = "tinyalu.sv"
        sim_folder = "simulation"
        s = sim(dut_path, top_module_file_name, sim_folder)

        num = 0
        clk_value = 0
        reset_value = 0

        s.getHandle('sim_wrapper')
        s.setValue("clk", 0)
        s.setValue("reset_n", 0)

        while True:
            # if num >= 20:
            #     break
            
            s.setValue("clk", not clk_value)
            clk_value = not clk_value

            if clk_value == 0:
                s.setValue("reset_n", 1)
                reset_value = 1
            
            if clk_value == 1:
                if reset_value == 0:
                    s.setValue("start", 0)
                    s.setValue("A", 0)
                    s.setValue("B", 0)
                    s.setValue("op", 0)
                else:
                    start_value = s.getValue("start")
                    done_value = s.getValue("done")
                    if start_value == 1 and done_value == 1:
                        s.setValue("start", 0)
                        self.item_done.succeed()
                        self.item_done = self.env.event()  
                    elif start_value == 0 and done_value == 0:
                        yield self.get_item | self.exit
                        if self.exit.triggered:
                            break
                        s.setValue("start", 1)
                        s.setValue("op", self.op)
                        s.setValue("A", self.input1)
                        s.setValue("B", self.input2)
                        num = num + 1

            s.eval()
            s.sleep_cycles(1)

            A_value = s.getValue("A")
            B_value = s.getValue("B")
            op_value = s.getValue("op")
            result_value = s.getValue("result")
            start_value = s.getValue("start")
            done_value = s.getValue("done")
            print("clk: %0d, reset_n: %0d, A: %0d, B: %0d, op: %0d, result: %0d, start: %0d, done: %0d" %(clk_value, reset_value, A_value, B_value, op_value, result_value, start_value, done_value))

        s.deleteHandle()

        
class Top(Module):
    def __init__(self, env, name):
        super().__init__(env, name)
        # 创建实例 init、alu，传入 env，将各自的 socket 进行连接
        self.init = Initiator(self.env, 'init')
        self.alu = ALU(self.env, 'alu')

        self.init.socket.bind(self.alu.socket)


def test_tinyalu(in1, in2, op, res):
    # 创建一个 env 实例
    env = simpy.Environment()

    # 创建顶层模块 top，传入 env
    top = Top(env, 'top')

    # 启动初始化
    top.init.src_in(in1, in2, op, res)

    # 运行仿真
    env.run()


def basic_test():
    # in1 = [random.randrange(0, 20) for i in range(20)]
    # in2 = [random.randrange(0, 20) for i in range(20)]
    in1 = [i for i in range(20)]
    in2 = [i for i in range(20)]
    op = [1 for i in range(20)]
    res = [0 for i in range(20)]
    test_tinyalu(in1, in2, op, res)
    pass


if __name__ == '__main__':
    basic_test()
