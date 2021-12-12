#                                    ┌───────────────────────────────────────────┐
#                                    │    Copyright (c) 2021 Nikita Paniukhin    │
#                                    │      Licensed under the MIT license       │
#                                    └───────────────────────────────────────────┘
#
# ======================================================================================================================

import sys
import os

sys.path.append("src")

from instructions import Instruction
from section_constants import *
from symbol_constants import *
from asserts import *
from utils import *

# ======================================================================================================================


class Program:
    def __init__(self, data=None):
        # Segment type
        self.p_type = data[0x00:0x04] if data is not None else None

        # Offset of the segment in the file image
        self.p_offset = bytes2int(data[0x04:0x08]) if data is not None else None

        # Virtual address of the segment in memory
        self.p_vaddr = data[0x08:0x0C] if data is not None else None

        # Segment's physical address
        self.p_paddr = data[0x0C:0x10] if data is not None else None

        # Size in bytes of the segment in the file image. May be 0
        self.p_filesz = bytes2int(data[0x10:0x14]) if data is not None else None

        # Size in bytes of the segment in memory. May be 0
        self.p_memsz = bytes2int(data[0x14:0x18]) if data is not None else None

        # Segment-dependent flags (position for 32-bit structure)
        self.p_flags = data[0x18:0x1C] if data is not None else None

        # Alignment
        self.p_align = data[0x1C:0x20] if data is not None else None


class Section:
    def __init__(self, data=None):
        # This code is PEP8 compliant but unreadable
        self.sh_name = data[0x00:0x04] if data is not None else None
        self.sh_type = data[0x04:0x08] if data is not None else None
        self.sh_flags = data[0x08:0x0C] if data is not None else None
        self.sh_addr = data[0x0C:0x10] if data is not None else None
        self.sh_offset = data[0x10:0x14] if data is not None else None
        self.sh_size = data[0x14:0x18] if data is not None else None
        self.sh_link = data[0x18:0x1C] if data is not None else None
        self.sh_info = data[0x1C:0x20] if data is not None else None
        self.sh_addralign = data[0x20:0x24] if data is not None else None
        self.sh_entsize = data[0x24:0x28] if data is not None else None

        self.sh_name = bytes2int(self.sh_name)
        self.sh_type = bytes2int(self.sh_type)
        self.sh_addr = bytes2int(self.sh_addr)
        self.sh_offset = bytes2int(self.sh_offset)
        self.sh_size = bytes2int(self.sh_size)


class Elf32_Sym:
    def __init__(self, data=None):
        self.st_name = bytes2int(data[0x00:0x04])  # Elf32_Word
        self.st_value = bytes2int(data[0x04:0x8])  # Elf32_Addr
        self.st_size = bytes2int(data[0x8:0x0C])  # Elf32_Word
        self.st_info = bytes2int(data[0x0C:0x0D])  # unsigned char
        self.st_other = bytes2int(data[0x0D:0x0E])  # unsigned char
        self.st_shndx = bytes2int(data[0x0E:0x10])  # Elf32_Half

        self.st_bind = self.st_info >> 4
        self.st_type = self.st_info & 0xF
        self.st_info = (self.st_bind << 4) + (self.st_type & 0xF)

        self.st_visibility = self.st_other & 0x3


Elf32_Sym_SIZE = 0x10

# ======================================================================================================================


def strtab_extract(data, strtab, offset):
    string_pos = strtab.sh_offset + offset
    string = ""
    while data[string_pos + len(string)] != 0x00:
        string += chr(data[string_pos + len(string)])
    return string


def parse(input_path, output_path):
    input_path, output_path = mkpath(input_path), mkpath(output_path)

    print("Parsing \"{}\"...".format(input_path))
    assert_cond(os.path.isfile(input_path), "File not found")

    with open(input_path, 'rb') as fin:
        data = fin.read()

    # =================================================== ELF HEADER ===================================================

    assert_equal(data[0x00], 0x7F, "ELF file not detected")
    assert_equal(data[0x01], ord('E'), "ELF file not detected")
    assert_equal(data[0x02], ord('L'), "ELF file not detected")
    assert_equal(data[0x03], ord('F'), "ELF file not detected")

    # data[04] = {1: 32-bit, 2: 64-bit}
    assert_equal(data[0x04], 1, "Should be 32-bit elf file")

    # data[05] = {1: little-endian, 2: big-endian}
    assert_equal(data[0x05], 1, "Should be coded in little-endian")

    # data[06] = Version (always 1)
    assert_equal(data[0x06], 1)

    # data[07-08] = ABI
    skip(data[0x07])
    skip(data[0x08])

    # data[09-0F] = Unused, should be 0
    assert_all_equal(data[0x09:0x0F], 0)

    # data[10-11] = File type
    skip(data[0x10])
    skip(data[0x11])

    # data[12-13] = Instruction set architecture
    skip(data[0x12:0x14])

    # data[14-17] = Elf version
    e_version = data[0x14:0x18]
    # assert_equal(e_version, b'\x01\x00\x00\x00', "Warning: elf version {} != 1".format(e_version))

    # data[18-1B] = Memory address of the entry point
    e_entry = data[0x18:0x1C]

    # data[1C-1F] = Program header offset (for 32-bit = 0x34 = 52)
    e_phoff = bytes2int(data[0x1C:0x1F])
    assert_equal(e_phoff, 52, "Warning: program header not after file header for 32-bit")

    # data[20-23] = Section header offset
    e_shoff = bytes2int(data[0x20:0x24])

    # data[24-27] = Smth, depends on the target architecture
    skip(data[0x24:0x28])

    # data[28-29] = Size of this header (for 32-bit = 0x34 = 52)
    e_ehsize = bytes2int(data[0x28:0x29])
    assert_equal(e_ehsize, 52, "Warning: elf header size normally should be 52 bytes, not {}".format(e_ehsize))

    # data[2A-2B] = Size of a program header
    e_phentsize = bytes2int(data[0x2A:0x2C])
    assert_equal(e_phentsize, 32, "Warning: program header size normally should be 32 bytes, not {}".format(e_phentsize))

    # data[2C-2D] = Number of entries in the program header
    e_phnum = bytes2int(data[0x2C:0x2E])

    # data[2E-2F] = Size of a section header
    e_shentsize = bytes2int(data[0x2E:0x30])
    assert_equal(e_shentsize, 0x28, "Warning: can only parse sections with size = {value2}, got size = {value1}")

    # data[30-31] = Number of entries in the section header
    e_shnum = bytes2int(data[0x30:0x32])

    # data[32-33] = Index of the section header that contains the section names
    e_shstrndx = bytes2int(data[0x32:0x34])

    # ================================================ PROGRAM HEADER ==================================================

    # offset = e_phoff
    # programs = []
    # for _ in range(e_phnum):
    #     programs.append(Program(data[offset:offset + e_phentsize]))
    #     offset += e_phentsize

    # del offset

    # =================================================== SECTIONS =====================================================

    unmapped_sections = []
    offset = e_shoff
    for _ in range(e_shnum):
        unmapped_sections.append(Section(data[offset:offset + e_shentsize]))
        offset += e_shentsize

    # Finding .strtab by type (SHT_STRTAB):
    strtab = None
    for section in unmapped_sections:
        if section.sh_type == SHT_STRTAB:
            name_pos = section.sh_offset + section.sh_name
            if data[name_pos:name_pos + len(".shstrtab")] == b".shstrtab":
                strtab = section
                break

    assert_cond(strtab is not None, "Can not find .strtab")

    # Assign a name to every section:
    sections = {strtab_extract(data, strtab, section.sh_name): section for section in unmapped_sections}

    assert_cond(".text" in sections, "Can not find .text")
    assert_cond(".strtab" in sections, "Can not find .strtab")
    assert_cond(".symtab" in sections, "Can not find .symtab")

    del unmapped_sections, offset, strtab, name_pos

    # ==================================================== SYMTAB ======================================================

    symtab = sections[".symtab"]
    symbols = []
    for symbol_offset in range(symtab.sh_offset, symtab.sh_offset + symtab.sh_size, Elf32_Sym_SIZE):
        symbol = Elf32_Sym(data[symbol_offset:symbol_offset + Elf32_Sym_SIZE])
        symbol.st_name = strtab_extract(data, sections[".strtab"], symbol.st_name)
        symbols.append(symbol)

    # ===================================================== TEXT =======================================================

    labels = [0, {}]
    for symbol in symbols:
        if symbol.st_type == STT_FUNC and symbol.st_name:
            labels[1][symbol.st_value] = symbol.st_name

    instructions = []

    offset = sections[".text"].sh_offset
    while offset < sections[".text"].sh_offset + sections[".text"].sh_size:

        instruction_size = 4 if int2bits(data[offset]).endswith("11") else 2

        instruction = Instruction(
            sections[".text"].sh_addr + offset - sections[".text"].sh_offset,
            bytes2bits(data[offset:offset + instruction_size]).zfill(instruction_size * 8),
            labels  # Reference to `labels`
        )

        instructions.append(instruction)
        offset += instruction_size

    # ==================================================== RESULT ======================================================

    with open(output_path, 'w', encoding="utf-8") as fout:
        # print("; формат строк указан по правилам printf (Си)", file=fout)
        print(".text", file=fout)
        # print("; строки оформляются в следующем формате", file=fout)
        # print("; с меткой: \"%08x %10s: %s %s, %s, %s\"", file=fout)
        # print("; без метки: метка является пустой строкой", file=fout)
        # print("; числа - десятичная запись", file=fout)
        # print("; load/store", file=fout)
        # print("; \"%08x %10s: %s %s, %s(%s)\"", file=fout)
        # print("; для c.addi*sp* команд sp регистр прописывается явно", file=fout)
        # print("; примеры:", file=fout)
        # print("00010078     _start: addi a0, zero, 0", file=fout)
        # print("0001007a             lui a1, 65536", file=fout)
        # print("00010080             lw a0, -24(s0)", file=fout)
        # print("00010088             c.addi4spn a0, sp, 8", file=fout)

        for instruction in instructions:
            instruction.print(file=fout)

        print(file=fout)
        # print("; между секциями text и symtab одна пустая строка", file=fout)
        print(".symtab", file=fout)
        # print("; заголовок таблицы", file=fout)
        # print("; \"%s %-15s %7s %-8s %-8s %-8s %6s %s\\n\"", file=fout)
        # print("; строки таблицы", file=fout)
        # print("; \"[%4i] 0x%-15X %5i %-8s %-8s %-8s %6s %s\\n\"", file=fout)
        print(
            "%s %-15s %7s %-8s %-8s %-8s %6s %s" %
            ("Symbol", "Value", "Size", "Type", "Bind", "Vis", "Index", "Name"),
            file=fout
        )
        for symbol_index, symbol in enumerate(symbols):
            print(
                "[%4i] 0x%-15X %5i %-8s %-8s %-8s %6s %s" %
                (
                    symbol_index, symbol.st_value, symbol.st_size, st_type2string[symbol.st_type],
                    st_bind2string[symbol.st_bind], st_visibility2string[symbol.st_visibility],
                    shndx2string[symbol.st_shndx] if symbol.st_shndx in shndx2string else symbol.st_shndx,
                    symbol.st_name
                ),
                file=fout
            )

    # ==================================================== CLEANUP =====================================================
    # To cleanup, make variables not unused and linter happy

    del data, e_version, e_entry, e_phoff, e_shoff, e_ehsize,
    e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx


def main():
    print(MSG["welcome"])

    if len(sys.argv) > 1:
        input_path = mkpath(sys.argv[1].strip())
        output_path = mkpath(sys.argv[2].strip())
        print("Detected command line arguments, running parse(\"{}\", \"{}\")...".format(input_path, output_path), end="\n\n")
        parse(input_path, output_path)

    else:
        print()
        parse(mkpath("elfs", "test1.elf"), "result.txt")


if __name__ == "__main__":
    main()
