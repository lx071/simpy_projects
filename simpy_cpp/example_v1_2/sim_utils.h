#include <stdint.h>

extern "C" double sc_time_stamp();

extern "C" void getHandle(const char * name);

extern "C" void setValue(int id, uint64_t newValue);

extern "C" uint64_t getValue(int id);

extern "C" void dump();

extern "C" bool eval();

extern "C" void sleep_cycles(uint64_t cycles);
extern "C" void deleteHandle();

// 启动产生波形
extern "C" void enableWave();

// 关闭产生波形
extern "C" void disableWave();