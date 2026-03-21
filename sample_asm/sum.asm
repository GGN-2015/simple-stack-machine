// Program: Calculate the sum of numbers from 1 to 100

// Describe the initial value of PC
0x0000000000000008:
    0x0000000100000000

// Describe the initial value of SP
0x0000000000000010:
    0x0000000200000000

// Code segment
0x0000000100000000:

    // Push immediate value 100 onto the stack
    PUSHIMM 0x0000000000000064
    // stack: [i=100]

    // Push immediate value zero onto the stack
    // Used to store the current calculation result
    PUSHIMM 0x0000000000000000
    // stack: [i=100, ans=0]

    // Loop body
begin_of_loop:
    // stack: [i, ans]

    // Add i to ans
    PUSHIMM 0x0000000000000001
    DUP
    ADD
    // stack: [i, new_ans]

    // Copy i to the top of the stack
    PUSHIMM 0x0000000000000001
    DUP
    // stack: [i, new_ans, i]

    // i = i - 1
    PUSHIMM 0x0000000000000001
    SUB
    // stack: [i, new_ans, new_i]

    PUSHIMM 1
    POPS 
    // stack: [new_i, new_ans]

    // Copy new_i to the top of the stack
    PUSHIMM 0x0000000000000001
    DUP
    // stack: [new_i, new_ans, new_i]

    // Check if the top element of the stack is equal to zero
    PUSHIMM 0x0000000000000000
    EQU
    NOT
    PUSHIMM begin_of_loop
    // stack: [new_i, new_ans, (new_i != 0), begin_of_loop]
    BR

    // End of loop
    // stack: [0, ans]
    HALT

// Stack segment
// No default settings, all values are zero
0x0000000200000000: