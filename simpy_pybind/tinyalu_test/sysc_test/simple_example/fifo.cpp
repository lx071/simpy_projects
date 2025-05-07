#include <systemc.h>

SC_MODULE(Producer) {
    sc_fifo_out<int> out;
    SC_CTOR(Producer) {
        SC_THREAD(produce);
    }
    void produce() {
        for (int i = 0; i < 10; ++i) {
            out.write(i);
            wait(1, SC_NS);
        }
    }
};

SC_MODULE(Consumer) {
    sc_fifo_in<int> in;
    SC_CTOR(Consumer) {
        SC_THREAD(consume);
    }
    void consume() {
        int data;
        while (true) {
            in.read(data);
            cout << "Received: " << data << endl;
        }
    }
};

int sc_main(int argc, char* argv[]) {
    sc_fifo<int> fifo(10);
    Producer producer("Producer");
    Consumer consumer("Consumer");
    producer.out(fifo);
    consumer.in(fifo);
    sc_start();
    return 0;
}