NOARG_OPCODES = {
    "HALT": 0b0000000000000000,
    "RET": 0b0000000100000000,
    "EI": 0b0000001100000000,
    "DI": 0b0000010000000000,
    "NOP": 0b0000011100000000,
}

CC_BITS = {
    "EQ": 0b000,
    "NE": 0b001,
    "GE": 0b010,
    "GT": 0b011,
    "LT": 0b100,
    "LE": 0b101,
    "CS": 0b110,
    "CC": 0b111,
}

REG_BITS = {
    "AX": 0b000,
    "BX": 0b001,
    "CX": 0b010,
    "DX": 0b011,
    "IX": 0b100,
    "BP": 0b101,
    "SP": 0b110,
    "LR": 0b111,
}


LOAD_STORE_BITS = {
    "LOADW": 0b00100,
    "STOREW": 0b01000,
    "LOADB": 0b01100,
    "STOREB": 0b10000,
}

ALU_RR_ALUOP_BITS = {
    "ADD": 0b0000,
    "SUB": 0b0001,
    "AND": 0b0010,
    "OR": 0b0011,
    "XOR": 0b0100,
    "CMP": 0b0101,
    "LSL": 0b0110,
    "LSR": 0b0111,
    "ADC": 0b1000,
    "SBC": 0b1001,
    "TEST": 0b1010,
    "ASR": 0b1011,
}

ALU_RI_ALUOP_BITS = {
    "ADD": 0b000,
    "SUB": 0b001,
    "AND": 0b010,
    "OR": 0b011,
    "XOR": 0b100,
    "CMP": 0b101,
    "LSL": 0b110,
    "LSR": 0b111,
}

BITMASKS_LOOKUPS = [0x0000, 0x1111, 0x2222, 0x3333, 0x4444, 0x5555, 0x6666, 0x7777,
  0x8888, 0x9999, 0xAAAA, 0xBBBB, 0xCCCC, 0xDDDD, 0xEEEE, 0xFFFF,
  0x00FF, 0xFF00, 0x0FF0, 0xF00F, 0x0F0F, 0xF0F0, 0x0000, 0x0000,
  0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000]
