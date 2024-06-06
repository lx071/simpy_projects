
#include <pybind11/pybind11.h>
#include <pybind11/embed.h> // everything needed for embedding
namespace py = pybind11;

#include <stdint.h>
#include <iostream>
#include <string>

#include "Vtinyalu.h"
#ifdef TRACE
#include "verilated_vcd_c.h"
#endif
#include "Vtinyalu__Syms.h"


//usr/local/share/verilator/include/verilated.h
//typedef vluint8_t    CData;     ///< Verilated pack data, 1-8 bits
//typedef vluint16_t   SData;     ///< Verilated pack data, 9-16 bits
//typedef vluint32_t   IData;     ///< Verilated pack data, 17-32 bits
//typedef vluint64_t   QData;     ///< Verilated pack data, 33-64 bits
//typedef vluint32_t   EData;     ///< Verilated pack element of WData array
//typedef EData        WData;     ///< Verilated pack data, >64 bits, as an array

/* version 5.010
using CData = uint8_t;    ///< Data representing 'bit' of 1-8 packed bits
using SData = uint16_t;   ///< Data representing 'bit' of 9-16 packed bits
using IData = uint32_t;   ///< Data representing 'bit' of 17-32 packed bits
using QData = uint64_t;   ///< Data representing 'bit' of 33-64 packed bits
using EData = uint32_t;   ///< Data representing one element of WData array
using WData = EData;        ///< Data representing >64 packed bits (used as pointer)
*/


class ISignalAccess{
    public:
        virtual ~ISignalAccess() {}
        
        virtual uint64_t getValue() = 0;
        virtual void setValue(uint64_t value) = 0;
};

class  CDataSignalAccess : public ISignalAccess
{
    public:
        //指针指向信号值
        CData* raw;
        //构造函数      单冒号(:)的作用是表示后面是初始化列表,对类成员进行初始化
        CDataSignalAccess(CData *raw) : raw(raw){}
        CDataSignalAccess(CData &raw) : raw(std::addressof(raw)){}
        uint64_t getValue() {return *raw;}
        void setValue(uint64_t value)  {*raw = value; }
};

class  SDataSignalAccess : public ISignalAccess
{
    public:
        //指针指向信号值
        SData* raw;
        //构造函数      单冒号(:)的作用是表示后面是初始化列表,对类成员进行初始化
        SDataSignalAccess(SData *raw) : raw(raw){}
        SDataSignalAccess(SData &raw) : raw(std::addressof(raw)){}
        uint64_t getValue() {return *raw;}
        void setValue(uint64_t value)  {*raw = value; }
};

class  IDataSignalAccess : public ISignalAccess
{
    public:
        //指针指向信号值
        IData* raw;
        //构造函数      单冒号(:)的作用是表示后面是初始化列表,对类成员进行初始化
        IDataSignalAccess(IData *raw) : raw(raw){}
        IDataSignalAccess(IData &raw) : raw(std::addressof(raw)){}
        uint64_t getValue() {return *raw;}
        void setValue(uint64_t value)  {*raw = value; }
};

class  QDataSignalAccess : public ISignalAccess
{
    public:
        //指针指向信号值
        QData* raw;
        //构造函数      单冒号(:)的作用是表示后面是初始化列表,对类成员进行初始化
        QDataSignalAccess(QData *raw) : raw(raw){}
        QDataSignalAccess(QData &raw) : raw(std::addressof(raw)){}
        uint64_t getValue() {return *raw;}
        void setValue(uint64_t value)  {*raw = value; }
};

class Wrapper;
thread_local Wrapper *simHandle1;

class Wrapper
{
    public:
        uint64_t time;
        std::string name;

        // 指针数组, 指向各个Signal
        ISignalAccess *signal[8];
        // 是否产生波形
        bool waveEnabled;
        //dut
        Vtinyalu top;
        #ifdef TRACE
        VerilatedVcdC tfp;
	    #endif

        Wrapper(const char * name)
        {
            simHandle1 = this;
            
            signal[0] = new CDataSignalAccess(top.A);
            signal[1] = new CDataSignalAccess(top.B);
            signal[2] = new CDataSignalAccess(top.op);
            signal[3] = new CDataSignalAccess(top.clk);
            signal[4] = new CDataSignalAccess(top.reset_n);
            signal[5] = new CDataSignalAccess(top.start);
            signal[6] = new CDataSignalAccess(top.done);
            signal[7] = new SDataSignalAccess(top.result);
            
            time = 0;
            waveEnabled = true;
            #ifdef TRACE
            Verilated::traceEverOn(true);
            top.trace(&tfp, 99);
            tfp.open("dump.vcd");
            #endif
            this->name = name;
        }

        // 析构函数在对象消亡时即自动被调用
        virtual ~Wrapper()
        {
            for(int idx = 0;idx < 8;idx++)
            {
                delete signal[idx];
            }
            #ifdef TRACE
            if(waveEnabled) tfp.dump((uint64_t)time);
            tfp.close();
            #endif
            std::cout<<"closeAll()"<<std::endl;
        }
};

double sc_time_stamp() 
{
    return simHandle1->time;
}

void getHandle(const char * name)
{
    Wrapper* handle = new Wrapper(name);
}

void setValue(int id, uint64_t newValue)
{
    simHandle1->signal[id]->setValue(newValue);
}

uint64_t getValue(int id)
{
    return simHandle1->signal[id]->getValue();
}

void dump()
{
    #ifdef TRACE
    if(simHandle1->waveEnabled) simHandle1->tfp.dump((uint64_t)simHandle1->time);
    #endif
}

bool eval()
{
    simHandle1->top.eval();
//    std::cout<<"time:"<<simHandle1->time<<std::endl;
    return Verilated::gotFinish();
}

void sleep_cycles(uint64_t cycles)
{
    dump();
    simHandle1->time += cycles;
}

void deleteHandle()
{
    delete simHandle1;
}

// 启动产生波形
void enableWave()
{
    simHandle1->waveEnabled = true;
}

// 关闭产生波形
void disableWave()
{
    simHandle1->waveEnabled = false;
}

void doPythonApi()
{
    py::print("Hello, World!"); // use the Python API
    py::module_ calc = py::module_::import("calc");
    
    for(int i=0;i<1000000;i++)
        calc.attr("add")(i%100, i%100);
    py::object result = calc.attr("add")(1, 2);
    int n = result.cast<int>();
    assert(n == 3);
    std::cout << n << std::endl;
    
    py::module_ utils = py::module_::import("harness_utils");
    utils.attr("do_python_api")();
}

// creating Python bindings
// 定义Python与C++之间交互的func与class
PYBIND11_MODULE(wrapper, m)
{
    py::class_<Wrapper>(m, "Wrapper")
        .def(py::init<const char *>());

    m.def("getHandle", &getHandle);
    m.def("setValue", &setValue);
    m.def("getValue", &getValue);
    m.def("dump", &dump);
    m.def("eval", &eval);
    m.def("sleep_cycles", &sleep_cycles);
    m.def("deleteHandle", &deleteHandle);
    m.def("enableWave", &enableWave);
    m.def("disableWave", &disableWave);
    m.def("doPythonApi", &doPythonApi);
}

