# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# test_my_design.py (extended)

import cocotb
from cocotb.triggers import Timer
from cocotb.triggers import FallingEdge, RisingEdge
from cocotb.triggers import Event
from cocotb.queue import Queue
from cocotb.simulator import *


class intf:
    def __init__(self, dut):
        self.clk = dut.clk
        self.rstn = dut.reset_n
        self.A = dut.A
        self.B = dut.B
        self.op = dut.op
        self.start = dut.start
        self.done = dut.done
        self.result = dut.result


class trans:
    def __init__(self, num = 0):
        self.in1 = num % 200
        self.in2 = num % 200
        self.op = 1
        

class generator:
    def __init__(self):
        self.req_mb = Queue(1)
      
    async def send_trans(self, num):
        t = trans(num)
        await self.req_mb.put(t)


class driver:
    def __init__(self, name):
        self.name = name
        self.req_mb = Queue(1)
    
    async def run(self):
        intf = self.intf
        await RisingEdge(intf.rstn)        
        while True:
            await RisingEdge(intf.clk)
            if self.req_mb.empty() is False:
                t = self.req_mb.get_nowait()
                await self.assign(t)        

    async def assign(self, t):
        intf = self.intf
        await RisingEdge(intf.clk)
        time_ns = get_sim_time()
        intf.start.value = 1
        intf.op.value = t.op
        intf.A.value = t.in1
        intf.B.value = t.in2
        # cocotb.log.info("%s %s drivered data %0d, %0d", time_ns, self.name, t.in1, t.in2)

    def set_interface(self, intf):
        self.intf = intf
  

class agent:
    def __init__(self, driver_name="driver", monitor_name = "monitor", name="agent"):
        self.name = name
        self.driver = driver(driver_name)

    async def run(self):
        await cocotb.start(self.driver.run())
        
    def set_interface(self, vif):
        self.vif = vif
        self.driver.set_interface(vif)

     
async def generate_clock(dut):
    """Generate clock pulses."""
    dut.clk.value = 0
    # for cycle in range(100):
    while True:
        dut.clk.value = 0
        await Timer(5, units="ns")
        dut.clk.value = 1
        await Timer(5, units="ns")


async def generate_rst(dut):
    await Timer(10, units="ns")
    dut.reset_n.value = 0
    for cycle in range(10):
        await RisingEdge(dut.clk)
    dut.reset_n.value = 1


class root_test:
    def __init__(self, name = "root_test"):
        self.name = name
        self.agt = agent("driver", "monitor", "agent")
        self.gen = generator()
        self.agt.driver.req_mb = self.gen.req_mb   
        self.finish_e = Event()

    async def run(self, dut): 
        await cocotb.start(self.agt.run())
        for i in range(20):
            await self.gen.send_trans(i % 200)
            
        cocotb.log.info("%s finished", self.name)
        self.finish_e.set()
        self.finish_e.clear()
        
    def set_interface(self, vif):
        self.agt.set_interface(vif)


@cocotb.test()
async def tb(dut):
    """Try accessing the design."""
    vif = intf(dut)
    
    await cocotb.start(generate_clock(dut))  # run the clock "in the background"
    await cocotb.start(generate_rst(dut))  # run the clock "in the background"

    test = root_test()
    test.set_interface(vif)
    await cocotb.start(test.run(dut))

    cocotb.log.info("***************** finished********************")
    
    time_ns = get_sim_time()
    cocotb.log.info("%s", time_ns)
    await RisingEdge(dut.reset_n)

    await test.finish_e.wait()
    for cycle in range(5):
        await RisingEdge(dut.clk)