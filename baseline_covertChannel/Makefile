CC=nvcc
HOSTCC=g++-10

all: receiver sender

receiver:
	$(CC) -ccbin $(HOSTCC) src/receiver.cu -o receiver.out

sender:
	$(CC) -ccbin $(HOSTCC) src/sender.cu -o sender.out

test:
	./receiver.out
	./receiver.out 1
	./sender.out
	./sender.out 1

clean:
	rm -rf *.out
