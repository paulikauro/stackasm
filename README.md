# stackasm
A simple stack language interpreter to be used as a macro assembler mainly for Minecraft CPUs.

The language itself is (mostly) independent of the specifics of each CPU. An instruction set for a specific CPU is easy to encode as functions that write the binary instruction into a global buffer (a concept in the stack language). Similarly, functions for writing NBT data (a binary format, somewhat like JSON, that Minecraft uses) are written as a [library](https://github.com/paulikauro/stackasm/blob/master/nbt).
