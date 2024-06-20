# 汽车（car）进程, 汽车将交替驾驶和停车一段时间
# 需要一个对 Environment（env）的引用，以便创建新的事件
def car(env):
    while True:
        print('Start parking at %d' % env.now)
        parking_duration = 5
        yield env.timeout(parking_duration)

        print('Start driving at %d' % env.now)
        trip_duration = 2
        yield env.timeout(trip_duration)

import simpy

# 实例化环境
env = simpy.Environment()
# 添加进程
env.process(car(env))
# 设定仿真结束条件, 这里是 15s 后停止
env.run(until=15)

"""
Start parking at 0
Start driving at 5
Start parking at 7
Start driving at 12
Start parking at 14
"""
