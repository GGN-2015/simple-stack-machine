# simple-stack-machine
A simple stack-style machine language interpreter.

## Install

```bash
pip install simple-stack-machine
```

## Usage

```bash
python3 -m simple_stack_machine <filepath.asm>
python3 -m simple_stack_machine --debug <filepath.asm>
```

## 示例程序

> 见 [https://github.com/GGN-2015/simple-stack-machine/tree/main/sample_asm](https://github.com/GGN-2015/simple-stack-machine/tree/main/sample_asm)

## 指令和数据

你将有一个长度为 64 位的地址空间，每个位置存放一个字节，空间中需要存放全部的程序和数据。

所有的指令（除了 `PUSHIMM` 外）长度均为一个字节，当前程序正在执行的指令地址的位置被存储在一个长度为 64 位的程序计数器  (PC) 中。

## 寄存器组

1. 程序计数器：PC (64 位)
2. 栈顶寄存器：SP (64 位)
3. 访存寄存器：AP (64 位)

SP 指向的位置，是栈顶元素所在位置 + 8，机器字长为 64 位。

在程序启动时：
- 初始 PC 存储在：`mem[8] ... mem[15]`
- 初始 SP 存储在：`mem[16] ... mem[23]`
- AP 初始值为 0

## 调用约定

当调用函数前，由调用者负责创建参数列表：

```
stack: [..., arg_1, arg_2, ..., arg_n]
```

然后，由调用者创建返回值存储位置：

```
stack: [..., arg_1, arg_2, ..., arg_n, 0]
```

再然后，返回地址 (ret_addr) 压栈，无条件跳转到目标函数入口，当程序来到目标函数入口时，栈空间中一定为：

```
stack: [..., arg_1, arg_2, ..., arg_n, 0, ret_addr]
```

在目标函数中，可以自行拷贝使用 `arg_1, ..., arg_n`，最终需要将 `0` 所在位置，赋值为函数返回值。我们约定函数返回值一定都是整数。

目标函数在执行过程中，最好不要修改 `ret_val` 以及它之前的除了返回值存储位置外的任何位置。

目标函数返回后，栈中状态为：

```
stack: [..., arg_1, arg_2, ..., arg_n, ret_ans]
```

其中 `ret_ans` 是函数的计算结果。

## 指令集

### 0. 什么都不做：NOP

```cpp
PC += 1;
```

### 1. 停机指令：HALT

```cpp
SP -= 8;
exit(make_interger(mem, SP, SP + 8));
```

### 2. 舍弃一个栈顶元素：POP

```cpp
SP -= 8;
PC += 1;
```

### 3. 给访存寄存器赋值：POPAP

```cpp
{
    SP -= 8;
    AP = make_interger(mem, SP, SP + 8);
}
PC += 1;
```

### 4. 向栈顶加入一个立即数：PUSHIMM

```cpp
for(int i = 0; i < 8; i += 1) {
    mem[SP + i] = mem[PC + 1 + i];
}
SP += 8;
PC += 9; // 在程序中占据 9 个字节
```

### 5. 为栈顶寄存器赋值：POPSP

```cpp
{
    SP -= 8;
    SP = make_interger(mem, SP, SP + 8);
}
PC += 1;
```

### 6. 栈顶寄存器的值入栈：PUSHSP

```cpp
save_interger(SP, mem, SP, SP + 8);
SP += 8;
PC += 1;
```

### 7. 程序计数器的值入栈：PUSHPC

```cpp
save_interger(PC, mem, SP, SP + 8);
SP += 8;
PC += 1;
```

### 8. 函数调用：CALL

```cpp
{
    long long old_pc = PC;
    SP -= 8;
    PC = make_interger(mem, SP, SP + 8);
    save_interger(old_pc + 1, mem, SP, SP + 8)
    SP += 8;
}
```

### 9. 读取内存到栈顶：LOAD

```cpp
for(int i = 0; i < 8; i += 1) {
    mem[SP + i] = mem[AP + i];
}
SP += 8;
PC += 1;
```

### 10. 将栈顶信息写内存：SAVE

```cpp
SP -= 8;
for(int i = 0; i < 8; i += 1) {
    mem[AP + i] = mem[SP + i];
}
PC += 1;
```

### 11. 系统调用：SYSCAL

```cpp
mem[0] = 1; // 触发系统调用
            // 系统调用的参数储存在 mem[8] ~ mem[63]
            // 系统调用完成后，会把 mem[0] 的值清零
            // mem[8] ~ mem[63] 的值中可能存储一些计算返回结果
PC += 1;
```

### 12. 有符号加法: ADD

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] 构成一个 64 bit 整数
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = val_1 + val_2;
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 13. 有符号减法: SUB

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] 构成一个 64 bit 整数
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = val_1 - val_2;
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 14. 有符号乘法: MUL

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] 构成一个 64 bit 整数
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = val_1 * val_2;
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 15. 有符号除法: DIV

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] 构成一个 64 bit 整数
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = val_1 / val_2;
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 16. 有符号模运算: MOD

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] 构成一个 64 bit 整数
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = val_1 % val_2;
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 17. 取相反数：NEG

```cpp
{
    SP -= 8;
    long long val = make_interger(mem, SP, SP + 8);
    
    long long ans = -val;
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 18. 逻辑取反：NOT

```cpp
{
    SP -= 8;
    long long val = make_interger(mem, SP, SP + 8);
    
    long long ans = (!val);
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 19. 按位与: AND

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] 构成一个 64 bit 整数
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 & val_2);
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 20. 按位或: OR

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] 构成一个 64 bit 整数
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 | val_2);
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 21. 按位异或: XOR

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] 构成一个 64 bit 整数
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 ^ val_2);
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 22. 逻辑右移: RSH

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] 构成一个 64 bit 整数
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 >> val_2);
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 23. 逻辑左移: LSH

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] 构成一个 64 bit 整数
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 << val_2);
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 24. 无条件跳转：JMP

```cpp
SP -= 8;
PC = make_interger(mem, SP, SP + 8);
```

### 25. 有条件跳转：BR

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] 构成一个 64 bit 整数
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    if(val_1 != 0) {
        PC = val_2 - 1;
    }
}
PC += 1;
```

### 26. 判断小于等于：LEQ

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] 构成一个 64 bit 整数
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 <= val_2);
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 27. 判断小于：LT

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] 构成一个 64 bit 整数
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 < val_2);
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 28. 判断等于：EQU

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] 构成一个 64 bit 整数
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 == val_2);
    save_interger(ans, mem, SP, SP + 8); // 把计算结果存回栈顶
    SP += 8;
}
PC += 1;
```

### 29. 拷贝栈中元素: DUP

```cpp
{
    SP -= 8;
    long long offset = make_interger(mem, SP, SP + 8);

    for(int i = 0; i < 8; i += 1) {
        mem[SP + i] = mem[SP - 8 * offset - 8 + i];
    }
    SP += 8;
}
PC += 1;
```

### 30. 设置栈中元素: POPS

```cpp
{
    SP -= 8;
    long long offset = make_interger(mem, SP, SP + 8);

    SP -= 8;
    val_pos = SP;

    for(int i = 0; i < 8; i += 1) {
        mem[SP - 8 * offset - 8 + i] = mem[val_pos + i];
    }
}
PC += 1;
```

### 31. 交换两个栈顶元素: EXCH

```cpp
{
    for(int i = 0; i < 8; i += 1) {
        unsigned char t = mem[SP - 16 + i];
        mem[SP - 16 + i] = mem[SP - 8 + i];
        mem[SP - 8 + i] = t;
    }
}
PC += 1;
```

## 系统调用

目前仅支持三个系统调用：

1. 从标准输入读入一个字符。
2. 输出一个字符串到标准输出（字符串以 `\0` 为结尾）。
3. 开启或者关闭调试模式。

### 从标准输入读入一个字符

```asm
PUSHIMM 8 // 地址位置 8 用于存储系统调用类型
POPAP
PUSHIMM 1 // 1 号系统调用表示从标准输入读入一个字符
SAVE
SYSCAL

// 系统调用执行结束后，字符的 ASCII 编码会被存放到地址 8 处的 64 位变量
PUSHIMM 8
POPAP
LOAD // 将这个值放入栈中
```

### 输出一个字符串

```asm
PUSHIMM 16 // 地址 16 处存放系统调用的参数
POPAP      
PUSHIMM str_ptr // 我们需要把字符串的首地址存到这个位置
SAVE

PUSHIMM 8 // 地址位置 8 用于存储系统调用类型
POPAP
PUSHIMM 2 // 2 号系统调用表示输出一个字符串
SAVE
SYSCAL

// 系统调用执行结束后，成功输出的字符个数会被存放到地址 8 处的 64 位变量
PUSHIMM 8
POPAP
LOAD // 将这个值放入栈中
```

### 开启 / 关闭调试模式

```asm
PUSHIMM 16 // 地址 16 处存放系统调用的参数
POPAP      
PUSHIMM 1 // 填入非零数表示开始调试模式，填入 0 表示关闭调试模式 
SAVE

PUSHIMM 8 // 地址位置 8 用于存储系统调用类型
POPAP
PUSHIMM 3 // 3 号系统调用表示输出一个字符串
SAVE
SYSCAL
```
