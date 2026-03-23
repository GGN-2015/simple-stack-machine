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

## Example Programs

> See [https://github.com/GGN-2015/simple-stack-machine/tree/main/sample_asm](https://github.com/GGN-2015/simple-stack-machine/tree/main/sample_asm)

## Instructions and Data

You have a 64-bit address space where each position stores one byte. This space holds all program code and data.

All instructions (except `PUSHIMM`) are 1 byte long. The address of the currently executing instruction is stored in a 64-bit **Program Counter (PC)**.

## Register Set

1. Program Counter: PC (64-bit)
2. Stack Pointer: SP (64-bit)
3. Address Pointer: AP (64-bit)

The position pointed to by SP is **the address of the top stack element + 8** (the machine word size is 64 bits).

At program startup:
- Initial PC is stored at: `mem[8] ... mem[15]`
- Initial SP is stored at: `mem[16] ... mem[23]`
- AP is initialized to 0

## Calling Convention

Before calling a function, the caller is responsible for creating the parameter list:

```
stack: [..., arg_1, arg_2, ..., arg_n]
```

Then, the caller creates a storage location for the return value:

```
stack: [..., arg_1, arg_2, ..., arg_n, 0]
```

Next, push the return address (`ret_addr`) onto the stack and jump unconditionally to the target function entry. When the program reaches the function entry, the stack **must** be in this state:

```
stack: [..., arg_1, arg_2, ..., arg_n, 0, ret_addr]
```

Inside the target function:
- You may copy and use `arg_1, ..., arg_n` as needed
- You **must** assign the function’s return value to the position of the `0` (we mandate all return values are integers)
- Avoid modifying `ret_addr` or any positions before it (except the return value storage location)

After the target function returns, the stack state becomes:

```
stack: [..., arg_1, arg_2, ..., arg_n, ret_ans]
```

Where `ret_ans` is the function’s computed result.

## Instruction Set

### 0. Do Nothing: NOP

This command will do nothing, the initial value in memory is zero.

```cpp
PC += 1;
```

### 1. Halt Instruction: HALT

```cpp
SP -= 8;
exit(make_interger(mem, SP, SP + 8) % 256);
```

### 2. Discard Top Stack Element: POP

The top value in stack will be erased, and the stack pointer (SP) will minus 8 bytes.

Stack status before: `[..., stk_top_val]`

Stack status after: `[...]`

```cpp
SP -= 8;
PC += 1;
```

### 3. Assign to Address Pointer: POPAP

The top value in stack will be poped and then saved into register address pointer (AP).

Stack status before: `[..., stk_top_val]`

Stack status after: `[...]`

```cpp
{
    SP -= 8;
    AP = make_interger(mem, SP, SP + 8);
}
PC += 1;
```

### 4. Push Immediate Value to Stack: PUSHIMM

This is the only command in this machine code to introduce an immediate integer into memory.

Stack status before: `[...]`

Stack status after: `[..., imm_val]`

```cpp
for(int i = 0; i < 8; i += 1) {
    mem[SP + i] = mem[PC + 1 + i];
}
SP += 8;
PC += 9; // Occupies 9 bytes in the program
```

### 5. Assign to Stack Pointer: POPSP

The top value in stack will be poped and then saved into register stack pointer (SP).

Stack status before: `[..., stk_top_val]`

Stack status after: `[...]`

```cpp
{
    SP -= 8;
    SP = make_interger(mem, SP, SP + 8);
}
PC += 1;
```

### 6. Push Stack Pointer Value to Stack: PUSHSP

Push the current value of register stack pointer (SP) into stack. Important fact is that, the new value in SP is greater then the value you pushed into stack.

Stack status before: `[...]`

Stack status after: `[..., sp_old_val]`

```cpp
save_interger(SP, mem, SP, SP + 8);
SP += 8; // which is sp_old_val + 8
PC += 1;
```

### 7. Push Program Counter Value to Stack: PUSHPC

Push the current address of machine code to the top of the stack.

Stack status before: `[...]`

Stack status after: `[..., old_pc]`

```cpp
save_interger(PC, mem, SP, SP + 8);
SP += 8;
PC += 1;
```

### 8. Function Call: CALL

Get an address from stack top and then jump to that address to execute a function, in the meanwhile, push the return address into stack. The return address is the position of the next command of current command `CALL`.

Stack status before: `[..., func_addr]`

Stack status after: `[..., ret_addr]`

```cpp
{
    long long old_pc = PC;
    SP -= 8;
    PC = make_interger(mem, SP, SP + 8);
    save_interger(old_pc + 1, mem, SP, SP + 8)
    SP += 8;
}
```

### 9. Load Memory to Stack Top: LOAD

Load a 64-bit interger from the address indicated by register AP, then send it to stack top.

```cpp
for(int i = 0; i < 8; i += 1) {
    mem[SP + i] = mem[AP + i];
}
SP += 8;
PC += 1;
```

### 10. Write Stack Top to Memory: SAVE

Save the 64-bit value on stack top to the address indicated by register AP, then erased the value in stack by modifying register SP.

```cpp
SP -= 8;
for(int i = 0; i < 8; i += 1) {
    mem[AP + i] = mem[SP + i];
}
PC += 1;
```

### 11. System Call: SYSCAL

Trigger system call. System call arguments are stored in `mem[8] ~ mem[63]`. After completion, `mem[0] ~ mem[3]` is cleared to 0. `mem[8] ~ mem[63]` may contain return results after system call returns.

```cpp
mem[0] = 1;

// system auto executing

PC += 1;
```

### 12. Signed Addition: ADD

Add two signed integer on stack top, and then push the result back to stack top.

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = val_1 + val_2;
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

### 13. Signed Subtraction: SUB

Subtract two signed integer on stack top, and then push the result back to stack top. Notice, the result is the second value on stack top subtracted by the first value on stack top.

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = val_1 - val_2;
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

### 14. Signed Multiplication: MUL

Multiply two signed integer on stack top, and then push the result back to stack top.

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = val_1 * val_2;
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

### 15. Signed Division: DIV

Divide two signed integer on stack top, and then push the result back to stack top. Notice, the result is the second value on stack top divided by the first value on stack top.

Stack Status Before: `[..., val_1, val_2]`

Stack Status After: `[..., val_1 % val_2, val_1 / val_2]`

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    // Sign of remainder is correspond to sign of val_2
    // ans1 is floor((double)val_1 / val_2)
    long long ans1 = val_1 / val_2;
    long long ans2 = val_1 % val_2;

    // save remainder
    save_interger(ans2, mem, SP, SP + 8);
    SP += 8;

    // save quotient
    save_interger(ans1, mem, SP, SP + 8);
    SP += 8;
}
PC += 1;
```

### 16. Unused

### 17. Negation: NEG

```cpp
{
    SP -= 8;
    long long val = make_interger(mem, SP, SP + 8);
    
    long long ans = -val;
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

### 18. Logical NOT: NOT

```cpp
{
    SP -= 8;
    long long val = make_interger(mem, SP, SP + 8);
    
    long long ans = (!val);
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

### 19. Bitwise AND: AND

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 & val_2);
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

### 20. Bitwise OR: OR

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 | val_2);
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

### 21. Bitwise XOR: XOR

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 ^ val_2);
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

### 22. Logical Right Shift: RSH

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = ((unsigned long long)val_1 >> val_2);
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

### 23. Logical Left Shift: LSH

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 << val_2);
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

### 24. Unconditional Jump: JMP

Pop the address value on stack top, and then jump to the address. This command is also used as function return.

Stack Status Before: `[..., aim_addr]`

Stack Status After: `[...]`

```cpp
SP -= 8;
PC = make_interger(mem, SP, SP + 8);
```

### 25. Conditional Jump: BR

Jump to aim address if `jump_flag` is not zero, then pop the top two value in stack.

Stack Status Before: `[..., jump_flag, aim_address]`

Stack Status After: `[...]`

```cpp
{
    SP -= 8;
    long long aim_address = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long jump_flag = make_interger(mem, SP, SP + 8);
    
    if(jump_flag != 0) {
        PC = aim_address - 1;
    }
}
PC += 1;
```

### 26. Less Than or Equal: LEQ

Compare the top two value (signed integer) in stack, erase them and push the result back to stack.

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 <= val_2);
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

### 27. Less Than: LT

Compare the top two value (signed integer) in stack, erase them and push the result back to stack.

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 < val_2);
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

### 28. Equal To: EQU

Compare the top two value (signed integer) in stack, erase them and push the result back to stack.

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = (val_1 == val_2);
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

### 29. Duplicate Stack Element: DUP

Duplicate a certain value in stack, the number of element in stack remains unchanged.

Stack Status Before: `[..., arr_i, ..., arr_1, arr_0, i]`

Stack Status After: `[..., arr_i, ..., arr_1, arr_0, arr_i]`

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

### 30. Set Stack Element: POPS

Pop an element from stack and then save it back to some position in stack, the position is indicated by an offset.

Stack Status Before: `[..., arr_i, ..., arr_1, arr_0, val, i]`

Stack Status After: `[..., val, ..., arr_1, arr_0]`

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

### 31. Swap Top Two Stack Elements: EXCH

Stack Status Before: `[..., v1, v2]`

Stack Status Before: `[..., v2, v1]`

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

## System Calls

Only three system calls are supported:

1. Read a character from standard input
2. Output a null-terminated string (`\0`) to standard output
3. Enable/disable debug mode

### Read a Character from Standard Input

```asm
PUSHIMM 8 // Address 8 stores the system call type
POPAP
PUSHIMM 1 // System call 1 = read a character from stdin
SAVE
SYSCAL

// After execution, the character's ASCII code is stored in the 64-bit variable at address 8
PUSHIMM 8
POPAP
LOAD // Push this value onto the stack
```

### Output a String

```asm
PUSHIMM 16 // Address 16 stores system call arguments
POPAP      
PUSHIMM str_ptr // Store the string's starting address here
SAVE

PUSHIMM 8 // Address 8 stores the system call type
POPAP
PUSHIMM 2 // System call 2 = output a string
SAVE
SYSCAL

// After execution, the number of successfully output characters is stored in the 64-bit variable at address 8
PUSHIMM 8
POPAP
LOAD // Push this value onto the stack
```

### Enable/Disable Debug Mode

```asm
PUSHIMM 16 // Address 16 stores system call arguments
POPAP      
PUSHIMM 1 // Non-zero = enable debug mode; 0 = disable debug mode
SAVE

PUSHIMM 8 // Address 8 stores the system call type
POPAP
PUSHIMM 3 // System call 3 = toggle debug mode
SAVE
SYSCAL
```
