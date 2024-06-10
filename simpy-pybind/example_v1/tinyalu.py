import re
import os
from verilator import wrapper
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

# 解析verilog代码, 返回输入端口名列表 和 输出端口名列表, 各端口位宽
def verilog_parse(dut_path, top_module_file_name):
    dut_name = top_module_file_name.split('.')[0]  # 模块名
    top_module_path = os.path.join(dut_path, top_module_file_name)
    # print(top_module_path)
    module_begin_match = r"module\s+([a-zA-Z0-9_]+)"
    # 匹配输入端口        input clock, input [31:0] io_a
    input_port_match = r"input\s+(reg|wire)*\s*(\[-?[0-9]+\:-?[0-9]+\]*)*\s*([a-zA-Z0-9_]+)"
    # 匹配输出端口        output [31:0] io_c
    output_port_match = r"output\s+(reg|wire)*\s*(\[-?[0-9]+\:-?[0-9]+\]*)*\s*([a-zA-Z0-9_]+)"
    current_module_name = ''
    input_ports_name = []
    output_ports_name = []
    ports_width = dict()
    with open(top_module_path, "r") as verilog_file:
        while verilog_file:
            verilog_line = verilog_file.readline().strip(' ')  # 读取一行
            # print(verilog_line)
            if verilog_line == "":  # 注：如果是空行，为'\n'
                break
            if "DPI-C" in verilog_line or "function " in verilog_line or "task " in verilog_line:
                continue
            module_begin = re.search(module_begin_match, verilog_line)

            if module_begin:
                current_module_name = module_begin.group(1)
                # print(current_module_name)

            if current_module_name == dut_name:
                input_port = re.search(input_port_match, verilog_line)
                output_port = re.search(output_port_match, verilog_line)
                if input_port:
                    # 输入端口名列表
                    input_ports_name.append(input_port.group(3))
                    range = input_port.group(2)
                    if range is None:
                        ports_width[input_port.group(3)] = 1
                    else:
                        left, right = range[1:-1].split(':')
                        ports_width[input_port.group(3)] = abs(int(left)-int(right))+1
                if output_port:
                    # 输出端口名列表
                    output_ports_name.append(output_port.group(3))
                    range = output_port.group(2)
                    if range is None:
                        ports_width[output_port.group(3)] = 1
                    else:
                        left, right = range[1:-1].split(':')
                        ports_width[output_port.group(3)] = abs(int(left) - int(right)) + 1
    # print(dut_name)
    # print(input_ports_name)
    # print(output_ports_name)
    # for x, y in ports_width.items():
    #     print(x, y)
    return input_ports_name, output_ports_name, ports_width


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

    def dut(self):
        dut_path = "./hdl/"
        top_module_file_name = "tinyalu.sv"
        input_ports_name, output_ports_name, ports_width = verilog_parse(dut_path, top_module_file_name)
        # print('in:', input_ports_name)
        # print('out:', output_ports_name)
        ports_name = input_ports_name + output_ports_name
        list_n = [i for i in range(len(ports_name))]
        signal_id = dict(zip(ports_name, list_n))

        yield self.start

        wrapper.getHandle('sim_wrapper')

        wrapper.setValue(signal_id["clk"], 0)
        wrapper.setValue(signal_id["reset_n"], 1)

        wrapper.setValue(signal_id["A"], 2)
        wrapper.setValue(signal_id["B"], 3)
        wrapper.setValue(signal_id["op"], 1)
        wrapper.setValue(signal_id["start"], 1)

        wrapper.eval()
        wrapper.sleep_cycles(5)

        A = wrapper.getValue(signal_id["A"])
        B = wrapper.getValue(signal_id["B"])
        result = wrapper.getValue(signal_id["result"])

        
        print("A: %0d, B: %0d, result: %0d" %(A, B, result))

        wrapper.setValue(signal_id["clk"], 1)
        wrapper.eval()
        wrapper.sleep_cycles(5)

        A = wrapper.getValue(signal_id["A"])
        B = wrapper.getValue(signal_id["B"])
        result = wrapper.getValue(signal_id["result"])

        
        print("A: %0d, B: %0d, result: %0d" %(A, B, result))

        wrapper.deleteHandle()

        self.finish.succeed()


    def dut2(self):
        dut_path = "./hdl/"
        top_module_file_name = "tinyalu.sv"
        input_ports_name, output_ports_name, ports_width = verilog_parse(dut_path, top_module_file_name)
        # print('in:', input_ports_name)
        # print('out:', output_ports_name)
        ports_name = input_ports_name + output_ports_name
        list_n = [i for i in range(len(ports_name))]
        signal_id = dict(zip(ports_name, list_n))

        yield self.start

        num = 0
        clk_value = 0
        reset_value = 0

        A = [i for i in range(20)]
        B = [i for i in range(20)]
        op = [1 for i in range(20)]

        wrapper.getHandle('sim_wrapper')
        wrapper.setValue(signal_id["clk"], 0)
        wrapper.setValue(signal_id["reset_n"], 0)

        while True:

            wrapper.setValue(signal_id["clk"], not clk_value)
            clk_value = not clk_value

            if clk_value == 0:
                wrapper.setValue(signal_id["reset_n"], 1)
                reset_value = 1
            
            if clk_value == 1:
                if reset_value == 0:
                    wrapper.setValue(signal_id["start"], 0)
                    wrapper.setValue(signal_id["A"], 0)
                    wrapper.setValue(signal_id["B"], 0)
                    wrapper.setValue(signal_id["op"], 0)
                else:
                    if num >= 20:
                        break
                    start_value = wrapper.getValue(signal_id["start"])
                    done_value = wrapper.getValue(signal_id["done"])
                    if start_value == 1 and done_value == 1:
                        wrapper.setValue(signal_id["start"], 0)
                    elif start_value == 0 and done_value == 0:
                        wrapper.setValue(signal_id["start"], 1)
                        wrapper.setValue(signal_id["op"], op[num])
                        wrapper.setValue(signal_id["A"], A[num])
                        wrapper.setValue(signal_id["B"], B[num])
                        num = num + 1

            wrapper.eval()
            wrapper.sleep_cycles(1)

            A_value = wrapper.getValue(signal_id["A"])
            B_value = wrapper.getValue(signal_id["B"])
            op_value = wrapper.getValue(signal_id["op"])
            result_value = wrapper.getValue(signal_id["result"])
            start_value = wrapper.getValue(signal_id["start"])
            done_value = wrapper.getValue(signal_id["done"])
            print("clk: %0d, reset_n: %0d, A: %0d, B: %0d, op: %0d, result: %0d, start: %0d, done: %0d" %(clk_value, reset_value, A_value, B_value, op_value, result_value, start_value, done_value))

        wrapper.deleteHandle()

        self.finish.succeed()
        pass


def test_tinyalu():
    # 创建一个 env 实例
    env = simpy.Environment()

    # 创建顶层模块 top，传入 env
    top = Top(env, 'top')

    # 运行仿真
    env.run()


if __name__ == '__main__':
    test_tinyalu()
