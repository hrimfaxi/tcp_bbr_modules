obj-m:=tcp_nanqinlang.o tcp_tsunami.o tcp_bbrplus.o
KDIR := /lib/modules/$(shell uname -r)/build

all:
	make -C $(KDIR) M=$(PWD) modules

clean:
	make -C $(KDIR) M=$(PWD) clean

dkms:
	dkms add .
	dkms install tcp_bbr_modules/1.0

dkms-remove:
	dkms remove tcp_bbr_modules/1.0 --all
