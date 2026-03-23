
# The largest value (plus 1)
VAL_RANGE = (1 << 64)

# Map function function
# From asm code to machine code
INSTURCTION_MAP = {
    "NOP": 0,
    "HALT": 1,
    "POP": 2,
    "POPAP": 3,
    "PUSHIMM": 4,
    "POPSP": 5,
    "PUSHSP": 6,
    "PUSHPC": 7,
    "CALL": 8,
    "LOAD": 9,
    "SAVE": 10,
    "SYSCAL": 11,
    "ADD": 12,
    "SUB": 13,
    "MUL": 14,
    "DIV": 15,
    "PLACEHOLDER_16": 16,
    "NEG": 17,
    "NOT": 18,
    "AND": 19,
    "OR": 20,
    "XOR": 21,
    "RSH": 22,
    "LSH": 23,
    "JMP": 24,
    "BR": 25,
    "LEQ": 26,
    "LT": 27,
    "EQU": 28,
    "DUP": 29,
    "POPS": 30,
    "EXCH": 31,
}

# reversed map function
DEASM_INSTURCTION_MAP = {
    INSTURCTION_MAP[item]: item
    for item in INSTURCTION_MAP
}

# if two dict share not the same length
# means duplicated name or machine code
assert len(INSTURCTION_MAP) == len(DEASM_INSTURCTION_MAP)
