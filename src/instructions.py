from instruction_formatter import format_instruction
from traceback import print_exc
from os.path import isfile
from asserts import *
from utils import *

from registors import REGS_BIT4, REGS_BIT2
from CSR import csr2string


RV32_PATH = "RV32.txt" if isfile("RV32.txt") else mkpath("src", "RV32.txt")
RVC_PATH = "RVC.txt" if isfile("RVC.txt") else mkpath("src", "RVC.txt")

with open(RV32_PATH, 'r', encoding="utf-8") as file:
    RV32 = [line.strip().split() for line in file if not line.startswith('#') and line.strip()]
with open(RVC_PATH, 'r', encoding="utf-8") as file:
    RVC = [line.strip().split() for line in file if not line.startswith('#') and line.strip()]


def remove_comments(data):
    for line_index, line in enumerate(data):
        for i in range(len(line)):
            if line[i].startswith('#'):
                del line[i:]
                break


def gen_reg_checks(source):
    checks = []

    if "!=" in source:
        i = source.find("!=") + 2
        while i < len(source) and ('0' <= source[i] <= '9' or source[i] in "{, }"):
            i += 1

        right_operand = source[source.find('!=') + 2:i]

        if right_operand.startswith('{'):
            right_operand = tuple(map(int, right_operand.lstrip('{').rstrip('}').split(',')))
            checks.append(lambda x, right_operand=right_operand: x not in right_operand)
        else:
            right_operand = int(right_operand)
            checks.append(lambda x, right_operand=right_operand: x != int(right_operand))

    return tuple(checks)


def preprocess_templates(templates):
    for template_instruction in templates:
        for i, item in enumerate(template_instruction):
            if any(item.startswith(x) for x in ("imm", "uimm", "nzimm", "nzuimm")):
                imm_type, item = item.split('[', 1)
                imm = tuple(
                    tuple(map(int, x.split(':'))) if ':' in x else int(x)
                    for x in item.rstrip("]").split('|')
                )

                imm_length = 0
                for x in imm:
                    if isinstance(x, int):
                        imm_length += 1
                    else:
                        imm_length += abs(x[0] - x[1]) + 1

                template_instruction[i] = (imm, imm_length, imm_type)

            elif item.startswith("rd") or item.startswith("rs"):
                reg_size = 3 if "′" in item else 5
                checks = gen_reg_checks(item)
                template_instruction[i] = ("REG", reg_size, checks)

            elif item.startswith("int"):
                num, size = map(int, item.lstrip("int").lstrip('(').rstrip(')').split(','))
                template_instruction[i] = (
                    "INT",
                    int(size),
                    tuple([lambda x, num=num: x == int(num)])
                )


remove_comments(RV32)
preprocess_templates(RV32)

remove_comments(RVC)
preprocess_templates(RVC)


class Instruction:
    def __init__(self, addr, source, labels):
        '''
        Params:
            addr, source, labels (lables should be passed by-reference)

        Attributes:
            addr   - [int] instruction address
            source - [str] source bits
            labels
            uknown - [bool] if command is unknown
            data
            name   - [str] command name
            type   - [str] command type
        '''

        self.addr = addr
        self.labels = labels
        self.source = source

        if source.endswith("11"):
            instructions = RV32
            self.command_size = 4
        else:
            instructions = RVC
            self.command_size = 2

        self.unknown = True
        last_match_template = None
        for template_instruction in instructions:
            try:
                match = self.parse(source, template_instruction)
            except Exception as e:
                print_exc()
                skip(e)
                continue

            if match is not None:
                assert_cond(
                    self.unknown,
                    "One instruction (#{}) ({}) refers to multiple templates: {} and {}".format(
                        int2hex(self.addr).zfill(8), source, last_match_template, template_instruction
                    )
                )
                self.unknown = False
                last_match_template = template_instruction
                self.data, self.name, self.type = match

        if self.unknown:
            print("Instruction(#{:08x}) does not match any template: {}".format(self.addr, source))

    def parse(self, source, template):
        type = template[-1]
        name = template[-2]
        data = []

        imm_parts = []
        imm_size = 0
        imm_type = None

        cur_pos = 0
        for item in template[:-2]:

            # REG
            if isinstance(item, tuple) and item[0] == "REG":
                _, reg_size, checks = item

                reg = bits2int(source[cur_pos:cur_pos + reg_size])
                if not all(check(reg) for check in checks):
                    return None

                data.append(REGS_BIT2[reg] if reg_size == 3 else REGS_BIT4[reg])
                cur_pos += reg_size

            # REG
            elif isinstance(item, tuple) and item[0] == "INT":
                _, int_size, checks = item

                num = bits2int(source[cur_pos:cur_pos + int_size])
                if not all(check(num) for check in checks):
                    return None

                data.append(num)
                cur_pos += int_size

            # Imm
            elif isinstance(item, tuple):
                imm, cur_imm_length, imm_type = item

                for x in imm:
                    if isinstance(x, int):
                        imm_size = max(imm_size, x)
                    else:
                        imm_size = max(imm_size, *map(int, x))

                imm_parts.append((imm, source[cur_pos:cur_pos + cur_imm_length]))
                data.append("imm")
                cur_pos += cur_imm_length

            # Const
            elif all('0' <= i <= '9' for i in item):
                if item != source[cur_pos:cur_pos + len(item)]:
                    return None

                data.append(item)
                cur_pos += len(item)

            # Unsigned imm
            elif item == "zimm":
                data.append(bits2int(source[cur_pos:cur_pos + 5]))
                cur_pos += 5

            # Const
            elif item == "shamt":
                data.append(bits2int(source[cur_pos:cur_pos + 5]))
                cur_pos += 5

            # CSR const
            elif item == "csr":
                if bits2int(source[cur_pos:cur_pos + 12]) not in csr2string:
                    return None
                data.append(csr2string[bits2int(source[cur_pos:cur_pos + 12])])
                cur_pos += 12

        if imm_parts:
            imm_size += 1
            imm = [0] * imm_size

            for imm_template, imm_source in imm_parts:
                cur_pos = 0
                for x in imm_template:
                    if isinstance(x, int):
                        imm[-x - 1] = imm_source[cur_pos]
                        cur_pos += 1
                    else:
                        for i in range(x[0], x[1] - 1, -1):
                            imm[-i - 1] = imm_source[cur_pos]
                            cur_pos += 1

            imm = "".join(map(str, imm))

            if 'u' not in imm_type and imm[0] == '1':  # Negative integers
                imm = int(imm, 2) - (1 << imm_size)
            else:
                imm = int(imm, 2)

            if type in ("J", "CJ", "B", "CB"):
                imm += self.addr

            for i, item in enumerate(data):
                if item == "imm":
                    data[i] = imm

        if type in ("J", "B"):
            if data[0] not in self.labels[1]:
                self.labels[1][data[0]] = "LOC_%05x" % (self.labels[0])
                data[0] = "LOC_%05x" % (self.labels[0])
                self.labels[0] += 1

        elif type in ("CB", "CJ"):
            if data[1] not in self.labels[1]:
                self.labels[1][data[1]] = "LOC_%05x" % (self.labels[0])
                data[1] = "LOC_%05x" % (self.labels[0])
                self.labels[0] += 1

        return data, name, type

    def __str__(self):
        return format_instruction(self)

    def print(self, *args, **kwargs):
        return print(self, *args, **kwargs)
