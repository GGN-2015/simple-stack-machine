// 程序：计算 1 ~ 100 的和



// 描述 PC 的初始值
0x0000000000000008:
    0x0000000100000000



// 描述 SP 的初始值
0x0000000000000010:
    0x0000000200000000



// 代码段
0x0000000100000000:



    // 立即数 100 进栈
    PUSHIMM 0x0000000000000064
    // stack: [i=100]



    // 立即数零进栈
    // 用来存储目前的计算结果
    PUSHIMM 0x0000000000000000
    // stack: [i=100, ans=0]



    // 循环体
begin_of_loop:
    // stack: [i, ans]



    // 在 ans 身上加 i
    PUSHIMM 0x0000000000000001
    DUP
    ADD
    // stack: [i, new_ans]


    PUSHIMM 0x0000000000000001
    // stack: [i, new_ans, 1]


    // 拷贝 i 到栈顶
    PUSHIMM 0x0000000000000002
    DUP
    // stack: [i, new_ans, 1, i]



    // i = i - 1
    PUSHIMM 0x0000000000000001
    SUB
    // stack: [i, new_ans, 1, new_i]
    POPS 
    // stack: [new_i, new_ans]



    // 拷贝 new_i 到栈顶
    PUSHIMM 0x0000000000000001
    DUP
    // stack: [new_i, new_ans, new_i]



    // 判断栈顶元素是否等于零
    PUSHIMM 0x0000000000000000
    EQU
    NOT
    PUSHIMM begin_of_loop
    // stack: [new_i, new_ans, (new_i != 0), begin_of_loop]
    BR



    // 循环结束
    // stack: [0, ans]

    // 使用三号系统调用打开单步调试输出
    // 调试模式下运行每条指令之前输出系统状态
    // 用户回车确认后系统继续运行
    // mem[8 .. 15] = 3
    // mem[16 .. 23] = 1
    PUSHIMM 0x0000000000000008
    POPAP
    PUSHIMM 0x0000000000000003
    SAVE
    PUSHIMM 0x0000000000000010
    POPAP
    PUSHIMM 0x0000000000000001
    SAVE
    SYSCAL
    HALT



// 栈段
// 不设置默认全是零
0x0000000200000000:
