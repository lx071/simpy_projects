# 模拟两个时钟以不同的时间间隔进行滴答
import simpy
 
def clock(env, name, tick):
    while True:
        print(name, env.now)
        yield env.timeout(tick)
 
# 实例化环境
env = simpy.Environment()
# 添加进程
env.process(clock(env, 'fast', 0.5))
env.process(clock(env, 'slow', 1))
# 设定仿真结束条件, 这里是 2s 后停止
env.run(until=2)

"""
fast 0
slow 0
fast 0.5
slow 1
fast 1.0
fast 1.5
"""
