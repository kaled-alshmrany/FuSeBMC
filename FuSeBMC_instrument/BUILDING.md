# Introduction

__FuSeBMC_instrument__ is a part of __FuSeBMC__ project; for more details, please refere the [FuSeBMC on Github](https://github.com/kaled-alshmrany/FuSeBMC).
This guide assumes that you have cloned the source code of  __FuSeBMC__ project to directory like:

```
<path_to_your_project>/FuSeBMC
```
# Installing Dependencies

The dependencies are listed in the following installation command:

```
sudo apt-get update && sudo apt-get install build-essential cmake gcc-multilib linux-libc-dev wget
```

## Preparing Clang 11

__FuSeBMC_instrument__ uses [__clang__](https://clang.llvm.org/). It currently supports version 11.0.0.

First, we need to download the package. It can be performed using the following __wget__ command:

```
wget https://github.com/llvm/llvm-project/releases/download/llvmorg-11.0.0/clang+llvm-11.0.0-x86_64-linux-gnu-ubuntu-20.04.tar.xz
```

Then, we need to extract the package. You can use the following __tar__ command in your directory <path_to_your_project>/FuSeBMC/:

```
tar xJf clang+llvm-11.0.0-x86_64-linux-gnu-ubuntu-20.04.tar.xz && mv clang+llvm-11.0.0-x86_64-linux-gnu-ubuntu-20.04 clang11

```


Before proceeding to the next section, make sure you have clang, LLVM ready in your workspace:

```
clang and LLVM:
<path_to_your_project>/FuSeBMC/clang11

FuSeBMC_instrument:
<path_to_your_project>/FuSeBMC/FuSeBMC_instrument

```

## Building FuSeBMC_instrument


First, we need to setup __cmake__, by using the following command in <path_to_your_project>/FuSeBMC/ directory:

```
cd FuSeBMC_instrument && mkdir build && cd build && cmake .. -DClang_DIR=$PWD/../../clang11 -DLLVM_DIR=$PWD/../../clang11 -DCMAKE_INSTALL_PREFIX:PATH=$PWD/../release

```

Finally, we can trigger the build process, by using the following command:

```
cmake --build . && make install
```

Once it is finished, __FuSeBMC_instrument__ should be available in the _release_ and <path_to_your_project>/FuSeBMC/FuSeBMC_instrument folders.
