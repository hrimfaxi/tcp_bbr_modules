obj-m:=tcp_nanqinlang.o tcp_tsunami.o tcp_bbrplus.o tcp_brutal.o

ifeq ($(BUILD_BBR3),1)
	obj-m += tcp_bbr3.o
endif

ifneq ($(KERNELRELEASE),)
	KDIR ?= /lib/modules/$(KERNELRELEASE)/build
else
	KDIR ?= /lib/modules/$(shell uname -r)/build
endif

ifeq ($(LLVM),1)
	KCONF_CC ?= clang
else
	KCONF_CC ?= $(CC)
endif

all: kernel_config.h
	make -C $(KDIR) M=$(PWD) modules

clean:
	make -C $(KDIR) M=$(PWD) clean
	rm -f kernel_config.h

kernel_config.h:
	./gen_kconfig.py -j $(shell nproc) $(KC_DEBUG_FLAGS) $(KDIR) kernel_config.h $(KCONF_CC) $(ARCH_ARGS) kapi_checklist

dkms:
	dkms add .
	dkms install tcp_bbr_modules/1.0

dkms-remove:
	dkms remove tcp_bbr_modules/1.0 --all
