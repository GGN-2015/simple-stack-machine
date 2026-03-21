// Program: Euclidean algorithm (division method)

// Describe the initial value of PC
0x0000000000000008:
    0x0000000100000000

// Describe the initial value of SP
0x0000000000000010:
    0x0000000200000010

// Code segment
0x0000000100000000:

    // Jump directly to the start of the main program
    PUSHIMM _main
    JMP

// Calculate the greatest common divisor
gcd:
    // Before function call, store function parameters before return address
    // stack: [..., a, b, 0, ret_addr]

    // Copy function parameters to current function's stack space
    PUSHIMM 3
    DUP
    // stack: [..., a, b, 0, ret_addr, a]

    PUSHIMM 3
    DUP
    // stack: [..., a, b, 0, ret_addr, a, b]

    PUSHIMM 0
    DUP
    PUSHIMM 0
    EQU
    // stack: [..., a, b, 0, ret_addr, a, b, (b == 0)]
    PUSHIMM gcd_ret
    BR
    // stack: [..., a, b, 0, ret_addr, a, b]

    EXCH
    // stack: [..., a, b, 0, ret_addr, b, a]

    PUSHIMM 1
    DUP
    // stack: [..., a, b, 0, ret_addr, b, a, b]

    MOD
    // stack: [..., a, b, 0, ret_addr, b, a % b]

    // Construct information for next function call
    PUSHIMM 0
    // stack: [..., a, b, 0, ret_addr, a_nxt, b_nxt, 0]

    // Recursively call gcd function
    PUSHPC
    PUSHIMM 21
    ADD
    PUSHIMM gcd
    // stack: [..., a, b, 0, ret_addr, a_nxt, b_nxt, 0, re_addr_nxt]
    JMP

    // After function returns
    // Write function return value back to the previous function call position
    // stack: [..., a, b, 0, ret_addr, a_nxt, b_nxt, ans_now]
    PUSHIMM 3
    POPS
    // stack: [..., a, b, ans_now, ret_addr, a_nxt, b_nxt]

    POP
    POP
    // stack: [..., a, b, ans_now, ret_addr]

    JMP
    // Function return
    // Stack space after return: [..., a, b, ans_now]

gcd_ret:
    // stack: [..., a, b, 0, ret_addr, a_now, b_now]

    POP
    // stack: [..., a, b, 0, ret_addr, a_now]

    // Set return value address
    PUSHIMM 1
    POPS
    // stack: [..., a, b, a_now, ret_addr]

    // Function return
    JMP
    // Stack space after return will be
    // stack: [..., a, b, a_now]

// Start of main program
_main:
    PUSHIMM 1081
    PUSHIMM 2231
    PUSHIMM 0
    // stack: [a, b, 0]

    // Recursively call gcd function
    PUSHPC
    PUSHIMM 21
    ADD
    PUSHIMM gcd
    // stack: [..., a, b, 0, ret_addr]
    JMP

    // After function returns
    // stack: [..., a, b, ans]
    HALT