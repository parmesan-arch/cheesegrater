from bitstring import BitArray
import eval_lookups


def eval_noarg(statement):
    return BitArray(uint=eval_lookups.NOARG_OPCODES[statement["opcode"]], length=16)


def eval_jcc(statement):
    opbits = BitArray(uint=0b10100, length=5)
    # get cnd code bits
    cc_int = eval_lookups.CC_BITS[statement["condition_code"]]
    cc_bits = BitArray(uint=cc_int, length=3)
    # get label offset
    dest = int(statement["branch_dest"]["dest"])
    pos = statement["address"]
    offset = dest - pos
    assert offset % 2 == 0
    jump_offset_bits = BitArray(int=(offset//2), length=8)
    return opbits + cc_bits + jump_offset_bits


def eval_jump_call(statement):
    # JMP  11000 imm______11
    # JMPR 11001 00000000 dst
    # CALL 11010 imm______11
    # CALR 11011 00000000 dst
    dest = statement["branch_dest"]["dest"]
    op_int = 0b11000 if statement["opcode"] == "JMP" else 0b11010
    if statement["branch_dest"]["type"] == "REGISTER":
        # reg-type branch
        op_int += 1
        pad = BitArray(uint=0, length=8)
        dest = eval_lookups.REG_BITS[dest]
        destbits = BitArray(uint=dest, length=3)
        opbits = BitArray(uint=op_int, length=5)
        return opbits + pad + destbits
    # label-type branch
    dest = int(statement["branch_dest"]["dest"])
    pos = statement["address"]
    offset = dest - pos
    assert offset % 2 == 0
    jump_offset_bits = BitArray(int=(offset//2), length=11)
    opbits = BitArray(uint=op_int, length=5)
    return opbits + jump_offset_bits


def eval_load_store(statement):
    op_int = eval_lookups.LOAD_STORE_BITS[statement["opcode"]]
    trf_int = eval_lookups.REG_BITS[statement["trf"]]
    trf_bits = BitArray(uint=trf_int, length=3)
    if statement["mem_operand"]["type"] == "base-offset":
        # add 2 to op int to reflect ___SPIX-type instr
        op_int += 2
        # must use either SP or IX as base
        if statement["mem_operand"]["source"] not in ["IX", "SP"]:
            raise SyntaxError(
                "Only register %ix or %sp can be used in base + offset addressing!"
            )
        s_int = 0 if statement["mem_operand"]["source"] == "IX" else 1
        sbit = BitArray(uint=s_int, length=1)
        imm_bits = BitArray(int=statement["mem_operand"]["offset"], length=7)
        op_bits = BitArray(uint=op_int, length=5)
        return op_bits + sbit + imm_bits + trf_bits
    # pre or post indexed
    # grab src reg
    src_int = eval_lookups.REG_BITS[statement["mem_operand"]["source"]]
    src_bits = BitArray(uint=src_int, length=3)
    # grab imm
    imm_bits = BitArray(int=statement["mem_operand"]["offset"], length=5)
    # correct opcode if post-indexed
    if statement["mem_operand"]["type"] == "post-index":
        op_int += 1
    op_bits = BitArray(uint=op_int, length=5)
    return op_bits + imm_bits + src_bits + trf_bits


def eval_rr_format(statement):
    # ALU_RR and also MOV
    src_int = eval_lookups.REG_BITS[statement["src"]]
    dst_int = eval_lookups.REG_BITS[statement["dst"]]
    src_bits = BitArray(uint=src_int, length=3)
    dst_bits = BitArray(uint=dst_int, length=3)

    if statement["opcode"] == "MOV":
        opbits = BitArray(uint=0b10101000, length=8)
        hwbits = BitArray(uint=0b00, length=2)
        return opbits + hwbits + src_bits + dst_bits

    # resolve aluop bits
    opbits = BitArray(uint=0b00001, length=5)
    alu_opint = eval_lookups.ALU_RR_ALUOP_BITS[statement["opcode"]]
    alu_opbits = BitArray(uint=alu_opint, length=4)
    h_bit = BitArray(uint=0, length=1)
    return opbits + alu_opbits + h_bit + src_bits + dst_bits


def eval_ri_format(statement):
    # ALU_RI
    dst_int = eval_lookups.REG_BITS[statement["dst"]]
    dst_bits = BitArray(uint=dst_int, length=3)
    imm_int = int(statement["immediate"])

    if statement["opcode"] in ["MOVH", "MOVL"]:
        opint = 0b00111 if statement["opcode"] == "MOVL" else 0b01011
        opbits = BitArray(uint=opint, length=5)
        imm_bits = BitArray(uint=imm_int, length=8)
        return opbits + imm_bits + dst_bits

    # resolve aluop bits
    opbits = BitArray(uint=0b00010, length=5)
    alu_opint = eval_lookups.ALU_RI_ALUOP_BITS[statement["opcode"]]
    if statement["opcode"] in ["LSL", "LSR"]:
        # shift amount is 4 bits
        imm_bits = BitArray(uint=imm_int, length=5)
    elif statement["opcode"] in ["AND", "OR", "XOR"]:
        # todo: this will be a table lookup.
        if imm_int not in eval_lookups.BITMASKS_LOOKUPS:
            raise SyntaxError(
                "Immediate 0x%X cannot be encoded for %s instruction!"
                % (imm_int, statement["opcode"])
            )
        imm_bits = BitArray(uint=eval_lookups.BITMASKS_LOOKUPS.index(imm_int), length=5)
    else:
        imm_bits = BitArray(uint=imm_int, length=5)
    alu_opbits = BitArray(uint=alu_opint, length=3)
    return opbits + alu_opbits + imm_bits + dst_bits


INSTR_TYPE_TO_EVAL_FN = {
    "noarg": eval_noarg,
    "jcc": eval_jcc,
    "jump_call": eval_jump_call,
    "load_store": eval_load_store,
    "rr_format": eval_rr_format,
    "ri_format": eval_ri_format,
}
