from utils.harness_utils import sim
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
        self.dut_thread = self.env.process(self.dut2())
        self.report_thread = self.env.process(self.report())
        
    def report(self):
        print("start")
        self.start.succeed()
        yield self.finish
        print("finish")

    # def dut(self):
    #     dut_path = "./hdl/"
    #     top_module_file_name = "tinyalu.sv"
    #     sim_folder = "simulation"
    #     s = sim(dut_path, top_module_file_name, sim_folder)

    #     yield self.start

    #     s.getHandle('sim_wrapper')

    #     s.setValue("clk", 0)
    #     s.setValue("reset_n", 1)

    #     s.setValue("A", 2)
    #     s.setValue("B", 3)
    #     s.setValue("op", 1)
    #     s.setValue("start", 1)

    #     s.eval()
    #     s.sleep_cycles(5)

    #     A = s.getValue("A")
    #     B = s.getValue("B")
    #     result = s.getValue("result")

        
    #     print("A: %0d, B: %0d, result: %0d" %(A, B, result))

    #     s.setValue("clk", 1)
    #     s.eval()
    #     s.sleep_cycles(5)

    #     A = s.getValue("A")
    #     B = s.getValue("B")
    #     result = s.getValue("result")

        
    #     print("A: %0d, B: %0d, result: %0d" %(A, B, result))

    #     s.deleteHandle()

    #     self.finish.succeed()


    def dut2(self):
        dut_path = "./hdl/"
        top_module_file_name = "tinyalu.sv"
        sim_folder = "simulation"
        s = sim(dut_path, top_module_file_name, sim_folder)

        yield self.start

        # num = 0
        # clk_value = 0
        # reset_value = 0

        # A = [i for i in range(20)]
        # B = [i for i in range(20)]
        # op = [1 for i in range(20)]

        # s.getHandle('sim_wrapper')
        # s.setValue("clk", 0)
        # s.setValue("reset_n", 0)

        # while True:

        #     s.setValue("clk", not clk_value)
        #     clk_value = not clk_value

        #     if clk_value == 0:
        #         s.setValue("reset_n", 1)
        #         reset_value = 1
            
        #     if clk_value == 1:
        #         if reset_value == 0:
        #             s.setValue("start", 0)
        #             s.setValue("A", 0)
        #             s.setValue("B", 0)
        #             s.setValue("op", 0)
        #         else:
        #             if num >= 20:
        #                 break
        #             start_value = s.getValue("start")
        #             done_value = s.getValue("done")
        #             if start_value == 1 and done_value == 1:
        #                 s.setValue("start", 0)
        #             elif start_value == 0 and done_value == 0:
        #                 s.setValue("start", 1)
        #                 s.setValue("op", op[num])
        #                 s.setValue("A", A[num])
        #                 s.setValue("B", B[num])
        #                 num = num + 1

        #     s.eval()
        #     s.sleep_cycles(1)

        #     A_value = s.getValue("A")
        #     B_value = s.getValue("B")
        #     op_value = s.getValue("op")
        #     result_value = s.getValue("result")
        #     start_value = s.getValue("start")
        #     done_value = s.getValue("done")
        #     print("clk: %0d, reset_n: %0d, A: %0d, B: %0d, op: %0d, result: %0d, start: %0d, done: %0d" %(clk_value, reset_value, A_value, B_value, op_value, result_value, start_value, done_value))

        # s.deleteHandle()

        # self.finish.succeed()
        # pass


 
def test_tinyalu():
    # 创建一个 env 实例
    env = simpy.Environment()

    # 创建顶层模块 top，传入 env
    top = Top(env, 'top')

    # 运行仿真
    env.run()


if __name__ == '__main__':
    test_tinyalu()
