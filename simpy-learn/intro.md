SimPy is a process-based discrete-event simulation framework based on standard Python.  
SimPy 是一个基于标准 Python 以进程为基础的离散事件仿真框架  
SimPy：用 Python 模拟真实世界的进程  

SimPy 中的进程（Processes）是由 Python 生成器函数构成，可以用来建模具有主动性的物件，比如客户、汽车、或者中介等等。  
SimPy也提供多种类的共享资源（shared resource）来描述拥挤点（比如服务器、收银台和隧道）。  

SimPy 是一个离散事件仿真库。  
活动组件（如车辆、客户或消息）的行为是通过进程（processes）进行建模的。  
所有进程都存在于一个环境（environment）中。  
它们通过事件（events）与环境和彼此进行交互。  

进程（Processes）由简单的 Python 生成器描述。您可以根据它是普通函数还是类的方法，将其称为进程函数（process function）或进程方法（process method）。在它们的生命周期中，它们创建事件并将其产出（yield），以等待事件发生。  

当一个进程产出（yields）一个事件时，该进程被暂停。当事件发生时（我们称之为事件被处理），SimPy 会恢复该进程。多个进程可以等待同一个事件。SimPy 会按照它们产出（yielded）事件的顺序来恢复这些进程。  

一个重要的事件类型是延时（Timeout）。这种类型的事件在经过一定的（模拟的）时间后发生（被处理）。它们允许进程在给定的时间内休眠（或保持状态）。Timeout 事件和其他所有事件都可以通过调用进程所在的环境（Environment）的相应方法来创建（例如，Environment.timeout()）。  


如果将 SimPy 分解开来，它只是一个异步事件调度器。  
您可以生成事件并在给定的仿真时间安排它们。事件按优先级、仿真时间和递增的事件 ID 进行排序。  
事件还具有回调函数列表，当事件被触发并由事件循环处理时，这些回调函数将被执行。事件也可以有返回值。  
涉及的组件包括环境、事件和您编写的进程函数。  


00_clock.py -- A short example simulating two clocks ticking in different time intervals  
01_car.py -- a car process. The car will alternately drive and park for a while  
02_car.py -- Process Interaction -- Waiting for a Process  
03_car.py -- Process Interaction -- Interrupting Another Process  
04_car.py -- Shared Resources -- Basic Resource Usage  
05_example.py -- an example  
06_event.py -- Events  

