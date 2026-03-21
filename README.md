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
- Avoid modifying `ret_val` or any positions before it (except the return value storage location)

After the target function returns, the stack state becomes:

```
stack: [..., arg_1, arg_2, ..., arg_n, ret_ans]
```

Where `ret_ans` is the function’s computed result.

## Instruction Set

### 0. Do Nothing: NOP

```cpp
PC += 1;
```

### 1. Halt Instruction: HALT

```cpp
SP -= 8;
exit(make_interger(mem, SP, SP + 8));
```

### 2. Discard Top Stack Element: POP

```cpp
SP -= 8;
PC += 1;
```

### 3. Assign to Address Pointer: POPAP

```cpp
{
    SP -= 8;
    AP = make_interger(mem, SP, SP + 8);
}
PC += 1;
```

### 4. Push Immediate Value to Stack: PUSHIMM

```cpp
for(int i = 0; i < 8; i += 1) {
    mem[SP + i] = mem[PC + 1 + i];
}
SP += 8;
PC += 9; // Occupies 9 bytes in the program
```

### 5. Assign to Stack Pointer: POPSP

```cpp
{
    SP -= 8;
    SP = make_interger(mem, SP, SP + 8);
}
PC += 1;
```

### 6. Push Stack Pointer Value to Stack: PUSHSP

```cpp
save_interger(SP, mem, SP, SP + 8);
SP += 8;
PC += 1;
```

### 7. Push Program Counter Value to Stack: PUSHPC

```cpp
save_interger(PC, mem, SP, SP + 8);
SP += 8;
PC += 1;
```

### 8. Function Call: CALL

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

```cpp
for(int i = 0; i < 8; i += 1) {
    mem[SP + i] = mem[AP + i];
}
SP += 8;
PC += 1;
```

### 10. Write Stack Top to Memory: SAVE

```cpp
SP -= 8;
for(int i = 0; i < 8; i += 1) {
    mem[AP + i] = mem[SP + i];
}
PC += 1;
```

### 11. System Call: SYSCAL

```cpp
mem[0] = 1; // Trigger system call
            // System call arguments are stored in mem[8] ~ mem[63]
            // After completion, mem[0] is cleared to 0
            // mem[8] ~ mem[63] may contain return results
PC += 1;
```

### 12. Signed Addition: ADD

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

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = val_1 / val_2;
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

### 16. Signed Modulo: MOD

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    long long ans = val_1 % val_2;
    save_interger(ans, mem, SP, SP + 8); // Store result back to stack top
    SP += 8;
}
PC += 1;
```

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
    
    long long ans = (val_1 >> val_2);
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

```cpp
SP -= 8;
PC = make_interger(mem, SP, SP + 8);
```

### 25. Conditional Jump: BR

```cpp
{
    SP -= 8;
    long long val_2 = make_interger(mem, SP, SP + 8); // mem[SP] ... mem[SP + 7] form a 64-bit integer
    SP -= 8;
    long long val_1 = make_interger(mem, SP, SP + 8);
    
    if(val_1 != 0) {
        PC = val_2 - 1;
    }
}
PC += 1;
```

### 26. Less Than or Equal: LEQ

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
