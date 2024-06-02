# Shared Resources -- Basic Resource Usage

def car(env, name, bcs, driving_time, charge_duration):
    # Simulate driving to the BCS (battery charging station)
    yield env.timeout(driving_time)

    # Request one of its charging spots
    print('%s arriving at %d' % (name, env.now))
    
    # resource’s request() 生成一个事件, 使用 with 语句来使用资源, 资源会自动释放
    with bcs.request() as req:
        yield req

        # Charge the battery
        print('%s starting to charge at %s' % (name, env.now))
        yield env.timeout(charge_duration)
        print('%s leaving the bcs at %s' % (name, env.now))


import simpy
env = simpy.Environment()
bcs = simpy.Resource(env, capacity=2)

# 创建 car 进程, 并将资源的引用以及一些额外的参数传递给它们
for i in range(4):
    env.process(car(env, 'Car %d' % i, bcs, i*2, 5))

# 开始仿真, 当没有更多的事件时, 仿真会自动停止
env.run()

"""
Car 0 arriving at 0
Car 0 starting to charge at 0
Car 1 arriving at 2
Car 1 starting to charge at 2
Car 2 arriving at 4
Car 0 leaving the bcs at 5
Car 2 starting to charge at 5
Car 3 arriving at 6
Car 1 leaving the bcs at 7
Car 3 starting to charge at 7
Car 2 leaving the bcs at 10
Car 3 leaving the bcs at 12
"""
