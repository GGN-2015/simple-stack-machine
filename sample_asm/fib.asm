// 程序：计算斐波那契数列




// 描述 PC 的初始值
0x0000000000000008:
    0x0000000100000000



// 描述 SP 的初始值
0x0000000000000010:
    0x0000000200000010



// 代码段
0x0000000100000000:

    // 计算第 n 个斐波那契数
    PUSHIMM 10
    // stack: [n]

    PUSHIMM 0
    // stack: [n, a]

    PUSHIMM 1
    // stack: [n, a, b]

loop_begin:

    EXCH
    // stack: [n, b, a]

    PUSHIMM 1
    DUP
    // stack: [n, b, a, b]

    ADD
    // stack: [n, b, a + b]

    PUSHIMM 2
    DUP
    PUSHIMM 1
    SUB
    // stack: [n, b, a + b, n - 1]

    PUSHIMM 2
    POPS
    // stack: [n - 1, b, a + b]

    PUSHIMM 2
    DUP
    PUSHIMM 0
    EQU
    NOT
    // stack: [n - 1, b, a + b, n - 1 != 0]

    PUSHIMM loop_begin
    BR
    // stack: [0, a, b]

    POP
    // stack: [0, a]

    HALT
