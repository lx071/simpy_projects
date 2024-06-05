import utils
import simpy

class alu(object):

    def __init__(self, env):
        self.env = env

    def calc(self, op, a, b):
        if(op == "+"):
            self.env.process(self.add(a, b))
        else:
            print("can't handle the operation")

    def add(self, a, b):
        res = utils.add(a, b)
        print("res:", res)
        yield self.env.timeout(1)


env = simpy.Environment()
inst = alu(env)
inst.calc("+", 3, 4)
env.run()
