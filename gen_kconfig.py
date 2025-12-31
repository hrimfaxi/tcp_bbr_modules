#!/usr/bin/env python3

import os, subprocess, tempfile, argparse, concurrent.futures

# 格式: #include <头文件> KERNEL_CONFIG_EOL void test() { 测试语句; } // HAVE_XXXX
# 如果oneline成功编译，将会定义HAVE_XXXX为1
# KERNEL_CONFIG_EOL将在编译时替换为换行符
def parse_oneline(oneline):
    s, macro_name = oneline.split('//')
    return s.replace('KERNEL_CONFIG_EOL', '\n'), macro_name.strip()

Debug = False

# 获取编译器前缀: arm-linux-gnueabihf-gcc => arm-linux-gnueabihf-
def compilerPrefix(cc):
    # clang 使用 --target，不需要前缀
    if cc == "clang":
        return ""
    gcc = cc.rfind("gcc")
    if gcc < 0:
        raise RuntimeError(f"invalid compiler: {cc}")
    return cc[:gcc]

def cmd2Str(list):
    try:
        import shlex
        return shlex.join(list)
    except:
        return " ".join(list)

class KernelApiChecker:
    def __init__(self, mp, arch, kernel_source_path, output_config_file, compiler, api_list_file):
        self.mp = mp
        self.arch = arch
        self.kernel_source_path = kernel_source_path
        self.output_config_file = output_config_file
        self.compiler = compiler
        self.api_list_file = api_list_file

    def create_test(self, snippet):
        test_code = f"""
#include <linux/kernel.h>
#include <linux/module.h>

{snippet}

static int __init test_init_module(void) {{
    return 0;
}}
module_init(test_init_module);

static void __exit test_cleanup_module(void) {{
}}
module_exit(test_cleanup_module);

MODULE_LICENSE("GPL");
"""
        if Debug:
            print (test_code)
        return test_code

    def compile_test_code(self, test_code):
        with tempfile.TemporaryDirectory() as test_dir:
            # print(test_dir)
            with open(os.path.join(test_dir, "Makefile"), "w") as f:
                f.write("""pwd=$(shell pwd)

obj-m := main.o
EXTRA_CFLAGS := -g -DDEBUG=1 -Wall -Wno-missing-declarations -Wno-missing-prototypes

ifndef ($(KDIR))
KDIR=/lib/modules/$(shell uname -r)/build
endif

all:
	make -C $(KDIR) M=$(pwd) modules

install modules_install:
	make -C $(KDIR) M=$(pwd) modules_install

clean:
	make -C $(KDIR) M=$(pwd) clean
""")
            with open(os.path.join(test_dir, "main.c"), "w") as f:
                f.write(test_code)

            try:
                makecall = [ "make", "-C", test_dir, ]

                if self.arch:
                    makecall.append(f"ARCH={self.arch}")
                if self.compiler != "gcc" and self.compiler != "cc" and self.compiler != "clang":
                    makecall.append(f"CROSS_COMPILE={compilerPrefix(self.compiler)}")
                if self.compiler == "clang":
                    makecall.append(f"LLVM=1")
                if Debug:
                    print (cmd2Str(makecall))
                    subprocess.check_output(
                            makecall
                    )
                else:
                    subprocess.check_output(
                            makecall,
                            stderr = subprocess.DEVNULL,
                    )
                return True
            except subprocess.CalledProcessError as e:
                return False

    def process_api(self, api):
        sources, api_name = parse_oneline(api)
        test_code = self.create_test(sources)
        if self.compile_test_code(test_code):
            s = f"#define {api_name} 1"
        else:
            s = f"// {api_name} not available"
        print(s)
        return s

    def generate_config_header(self):
        apis = self.read_api_list()
        config_lines = []

        if self.mp:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.mp) as executor:
                futures = {executor.submit(self.process_api, api): api for api in apis}
                for future in concurrent.futures.as_completed(futures):
                    api = futures[future]
                    try:
                        result = future.result()
                        config_lines.append(result)
                    except Exception as exc:
                        print(f'{api} generated an exception: {exc}')
        else:
            for api in apis:
                config_lines.append(self.process_api(api))
        return config_lines

    def write_config_file(self, args, config_lines):
        with open(self.output_config_file, "w") as f:
            f.write("#pragma once\n\n")
            f.write(f"// kernel source path: {args.kernel_source_path}\n")
            f.write(f"// compiler: {args.compiler}\n")
            f.write("\n")
            f.write("\n".join(config_lines))
            f.write("\n")

    def read_api_list(self):
        with open(self.api_list_file, "r") as f:
            return [line.strip() for line in f]

    def run(self, args):
        config_lines = self.generate_config_header()
        self.write_config_file(args, config_lines)

def main():
    parser = argparse.ArgumentParser(description = 'Generate kernel compatible config header')
    parser.add_argument('kernel_source_path', help='Path to kernel source.')
    parser.add_argument('output_config_file', help='Output configuration header file')
    parser.add_argument('compiler', help='Compiler to use')
    parser.add_argument('api_list_file', help='File containing list of APIs to check')
    parser.add_argument('-d', '--debug', action='store_true', help='debug mode')
    parser.add_argument('-j', '--multiprocessing', help='multi processing mode', type=int)
    parser.add_argument('-a', '--arch', help='Kernel build arch', default='')

    args = parser.parse_args()

    global Debug
    Debug = args.debug

    checker = KernelApiChecker(args.multiprocessing, args.arch, args.kernel_source_path, args.output_config_file, args.compiler, args.api_list_file)
    checker.run(args)
    print (f"{args.output_config_file} created.")

if __name__ == "__main__":
    main()
