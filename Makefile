obj-m:=tcp_nanqinlang.o tcp_tsunami.o tcp_bbrplus.o tcp_brutal.o

ifeq ($(BUILD_BBR3),1)
obj-m += tcp_bbr3.o
endif

ifneq ($(KERNELRELEASE),)
	KDIR ?= /lib/modules/$(KERNELRELEASE)/build
else
	KDIR ?= /lib/modules/$(shell uname -r)/build
endif

all:
	make -C $(KDIR) M=$(PWD) modules

clean:
	make -C $(KDIR) M=$(PWD) clean

dkms:
	dkms add .
	dkms install tcp_bbr_modules/1.0

dkms-remove:
	dkms remove tcp_bbr_modules/1.0 --all
