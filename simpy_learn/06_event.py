# Event basics -- Adding callbacks to an event
"""
import simpy

def my_callback(event):
    print('Called back from', event)

env = simpy.Environment()
event = env.event()
event.callbacks.append(my_callback)
# >>> event.callbacks
# [<function my_callback at 0x...>]
"""

# Example usages for Event
"""
class School:
    def __init__(self, env):
        self.env = env
        self.class_ends = env.event()
        self.pupil_procs = [env.process(self.pupil()) for i in range(3)]
        self.bell_proc = env.process(self.bell())

    def bell(self):
        for i in range(2):
            yield self.env.timeout(45)
            self.class_ends.succeed()
            self.class_ends = self.env.event()
            print()

    def pupil(self):
        for i in range(2):
            print(r' \o/', end='')
            yield self.class_ends

import simpy
env = simpy.Environment()
school = School(env)
env.run()
#  \o/ \o/ \o/ 
#  \o/ \o/ \o/
"""


# Processes are events, too
"""
def sub(env):
    yield env.timeout(1)
    return 23

def parent(env):
    ret = yield env.process(sub(env))
    return ret

import simpy
env = simpy.Environment()
print(env.now, env.run(env.process(parent(env))), env.now)
# 0 23 1
"""


"""
from simpy.util import start_delayed

def sub(env):
    yield env.timeout(1)
    return 23

def parent(env):
    # 在一定延迟后启动
    sub_proc = yield start_delayed(env, sub(env), delay=3)
    ret = yield sub_proc
    return ret

import simpy
env = simpy.Environment()
print(env.now, env.run(env.process(parent(env))), env.now)
# 0 23 4
"""


# Waiting for multiple events at once
"""
# AnyOf 和 AllOf 事件, 都是 Condition 事件
from simpy.events import AnyOf, AllOf, Event
events = [Event(env) for i in range(3)]
a = AnyOf(env, events)  # Triggers if at least one of "events" is triggered.
b = AllOf(env, events)  # Triggers if all each of "events" is triggered.
"""
"""
# 条件事件的值是一个有序字典, 其中每个触发的事件都有一个条目
# 事件实例被用作键, 事件值将是值
def test_condition(env):
    t1, t2 = env.timeout(1, value='spam'), env.timeout(2, value='eggs')
    ret = yield t1 | t2
    print("ret:", ret)
    print("ret[t1]:", ret[t1])
    assert ret == {t1: 'spam'}

    t1, t2 = env.timeout(1, value='spam'), env.timeout(2, value='eggs')
    ret = yield t1 & t2
    print("ret:", ret)
    print("ret[t1]:", ret[t1])
    print("ret[t2]:", ret[t2])
    assert ret == {t1: 'spam', t2: 'eggs'}

    # You can also concatenate & and |
    e1, e2, e3 = [env.timeout(i) for i in range(3)]
    yield (e1 | e2) & e3
    assert all(e.processed for e in [e1, e2, e3])


import simpy
env = simpy.Environment()
proc = env.process(test_condition(env))
env.run()
"""

"""
ret: <ConditionValue {<Timeout(1, value=spam) object at 0x7f5860f10940>: 'spam'}>
ret[t1]: spam
ret: <ConditionValue {<Timeout(1, value=spam) object at 0x7f5860f10760>: 'spam', <Timeout(2, value=eggs) object at 0x7f5860f106a0>: 'eggs'}>
ret[t1]: spam
ret[t2]: eggs
"""



def fetch_values_of_multiple_events(env):
    t1, t2 = env.timeout(1, value='spam'), env.timeout(2, value='eggs')
    r1, r2 = (yield t1 & t2).values()
    print("r1:", r1)
    print("r2:", r2)
    assert r1 == 'spam' and r2 == 'eggs'

import simpy
env = simpy.Environment()
proc = env.process(fetch_values_of_multiple_events(env))
env.run()


"""
r1: spam
r2: eggs
"""
