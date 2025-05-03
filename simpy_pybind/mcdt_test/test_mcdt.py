import sys
sys.path.append("../")

from utils import *
import simpy

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

class Module:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        pass
    def __register(self, func):
        pass


class Top(Module):

    def __init__(self, env, name):
        super().__init__(env, name)
        self.start = self.env.event()
        self.finish = self.env.event()
        self.dut_thread = self.env.process(self.dut())
        self.report_thread = self.env.process(self.report())
        
    def report(self):
        print("start")
        self.start.succeed()
        yield self.finish
        print("finish")

    def posedge_clk(self):
        top = self.top
        top.eval()
        # read outputs
        data = top.getValue("mcdt_data_o")
        val = top.getValue("mcdt_val_o")
        id = top.getValue("mcdt_id_o")
        print("data: %0d, val: %0d, id: %0d" %(data, val, id))

        top.sleep_cycles(5)
        top.setValue("clk_i", 0)
        top.eval()
        top.sleep_cycles(5)
        top.setValue("clk_i", 1)
        pass

    def chnl_write(self, id, data):
        top = self.top
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

    def dut(self):
        dut_path = "./hdl/"
        top_module_file_name = "mcdt.v"
        sim_folder = "simulation"
        top = sim(dut_path, top_module_file_name, sim_folder)
        self.top = top
        
        yield self.start
        num = 0
        clk_value = 0
        reset_value = 0
        time = 0

        A = [i for i in range(20)]
        B = [i for i in range(20)]
        op = [1 for i in range(20)]

        top.getHandle('sim_wrapper')
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
                    if num >= 20:
                        break
                    self.chnl_write(0, num + 10000);
                    self.chnl_write(1, num + 20000);
                    self.chnl_write(2, num + 30000);
                    num = num + 1

        # data = top.getValue("mcdt_data_o")
        # val = top.getValue("mcdt_val_o")
        # id = top.getValue("mcdt_id_o")

        # print("data: %0d, val: %0d, id: %0d" %(data, val, id))

        top.deleteHandle()

        self.finish.succeed()

 
def test_mcdt():
    # 创建一个 env 实例
    env = simpy.Environment()

    # 创建顶层模块 top，传入 env
    top = Top(env, 'top')

    # 运行仿真
    env.run()


if __name__ == '__main__':
    test_mcdt()
