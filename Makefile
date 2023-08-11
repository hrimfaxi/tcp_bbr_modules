obj-m:=tcp_nanqinlang.o tcp_tsunami.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

dkms:
	dkms add .
	dkms install tcp_nanqinlang_tsunami/1.0

dkms-remove:
	dkms remove tcp_nanqinlang_tsunami/1.0 --all
