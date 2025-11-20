#!/usr/bin/env python3
from bitstring import BitArray
import sys
import os
import parse
import eval_fns

WHEEL_VERSION = 2
PROCESSOR_START_ADDR = 0xF000

# Handle arguments
if "-h" in sys.argv:
    print(
        "Run with 2 arguments. Arg1 is the input file path, arg2 is the output file path."
    )
    exit(0)

if len(sys.argv) < 3:
    print(
        "Run with at least 2 arguments. Arg1 is the input file path, arg2 is the output file path. Additional args are memdump files to add."
    )
    exit(1)

in_path = sys.argv[1]
# in_path = "sws/multiple_strlen.sws"
out_path = sys.argv[2]
# out_path = "out"
if not os.path.exists(in_path):
    print("No such file exists for input file of:\n\t%s" % in_path)
    exit(1)

labels = {}
current_offset = PROCESSOR_START_ADDR

print("parsing")
statements = []
# 1. Parse file, list of statements
# As we parse, keep the current offset.
# This allows us to determine label locations, needed during eval.
# We also build the label table here.
with open(in_path, "r") as infile:
    for line in infile:
        # print(current_offset)
        try:
            statement = parse.parse_line(line.strip())
        except SyntaxError as e:
            print(e)
            sys.exit(1)
        if statement is None:
            continue
        if "size" not in statement:
            statement["size"] = 0
        if statement["type"] == "label":
            label = statement["label"]
            if label in labels:
                raise SyntaxError("Duplicate label %s!" % statement["label"])
            labels[label] = current_offset
        elif statement["type"] == "seek":
            current_offset = statement["seek"]
        elif statement["type"] == "align":
            current_offset = (
                (current_offset + statement["align"] - 1) // statement["align"]
            ) * statement["align"]
        else:
            current_offset += statement["size"]

        statements.append(statement)
        # print("\t", parsed)

# pprint.pprint(statements)
print("==============================")
# pprint.pprint(labels)
# exit()

# 2. Evaluate file
#   b. Loop over a second time, this time evaluating each instruction.
#      This step emits instructions to be written to the file.

current_offset = PROCESSOR_START_ADDR


with open(out_path, "wb") as file:
    # Write WHEEL header
    #   char magic_identifier[4]; // should be "whee"
    #   uint8_t version;
    #   uint8_t num_of_segments;
    #   uint16_t reserved;
    file.write(b"whee")
    file.write(BitArray(uint=WHEEL_VERSION, length=8).bytes)
    file.write(BitArray(uint=1, length=8).bytes)
    file.write(BitArray(uint=0, length=16).bytes)

    # having written the header, now we write each segment, starting with the main code segment
    # format of each header:
    # uint16_t start_address;
    # uint16_t length;
    # uint32_t checksum; // currently unimplemented, but might eventually be
    file.write(BitArray(uintle=0, length=16).bytes)  # start address is always 0xF000
    length = 65535

    file.write(BitArray(uintle=length, length=16).bytes)
    file.write(BitArray(uint=0, length=32).bytes)  # checksum

    block_start = file.tell()

    file.seek(block_start + current_offset)

    # assemble
    print("assembling")

    for statement in statements:
        if statement["type"] == "instruction":
            # patch label jumps if needed
            if (
                "branch_dest" in statement
                and statement["branch_dest"]["type"] == "LABEL"
            ):
                statement["branch_dest"]["dest"] = labels[
                    statement["branch_dest"]["dest"]
                ]
            statement["address"] = current_offset
            insnbits = eval_fns.INSTR_TYPE_TO_EVAL_FN[statement["instr_type"]](
                statement
            )

            insnbits.byteswap()
            file.write(insnbits.bytes)
            current_offset += 2
        elif statement["type"] == "directive":
            # handle directive
            # bytes-type things
            if statement["subtype"] == "bytes":
                file.write(statement["bytes"])
                current_offset += statement["size"]
            elif statement["subtype"] == "seek":
                file.seek(block_start + statement["seek"])
                current_offset = statement["seek"]
            elif statement["subtype"] == "align":
                current_offset = (
                    (current_offset + statement["align"] - 1) // statement["align"]
                ) * statement["align"]
                diff = current_offset - (file.tell() - 16)
                file.write(statement["fill"] * diff)
            else:
                print("Unknown directive subtype", statement)
        elif statement["type"] == "label":
            # nothing to do for label definitions at this stage
            pass

        else:
            print("Unknown statement type", statement)

    file.seek(65535 + block_start)
    file.write(b"\0")
