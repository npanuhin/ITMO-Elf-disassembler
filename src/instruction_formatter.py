#                                    ┌───────────────────────────────────────────┐
#                                    │    Copyright (c) 2021 Nikita Paniukhin    │
#                                    │      Licensed under the MIT license       │
#                                    └───────────────────────────────────────────┘
#
# ======================================================================================================================

unmatched_label_count = 0


def format_instruction(instruction):
    label = find_label(instruction, instruction.addr)

    if instruction.unknown:
        return "%08x %11s %s" % (
            instruction.addr,
            label + ':' if label else '',
            "unknown_command"
        )

    if instruction.type == "I":
        return "%08x %11s %s %s, %s, %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[3],
            instruction.data[1],
            instruction.data[0]
        )

    if instruction.type == "J":
        target_label = find_label(instruction, instruction.data[0])
        return "%08x %11s %s %s, %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[1],
            instruction.data[0] if target_label is None else target_label
        )

    if instruction.type in ("JR", "I-load/store"):
        return "%08x %11s %s %s, %s(%s)" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[3],
            instruction.data[0],
            instruction.data[1]
        )

    if instruction.type == "U":
        return "%08x %11s %s %s, %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[1],
            instruction.data[0]
        )

    if instruction.type == "S-load/store":
        return "%08x %11s %s %s, %s(%s)" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[1],
            instruction.data[0],
            instruction.data[2]
        )

    if instruction.type == "R":
        return "%08x %11s %s %s, %s, %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[4],
            instruction.data[2],
            instruction.data[1]
        )

    if instruction.type == "B":
        target_label = find_label(instruction, instruction.data[0])
        return "%08x %11s %s %s, %s, %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[2],
            instruction.data[1],
            instruction.data[0] if target_label is None else target_label
        )

    if instruction.type in "C":
        return "%08x %11s %s %s, %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[2],
            instruction.data[1]
        )

    if instruction.type in "CB":
        target_label = find_label(instruction, instruction.data[1])
        return "%08x %11s %s %s, %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[2],
            instruction.data[1] if target_label is None else target_label
        )

    if instruction.type == "CSP":
        return "%08x %11s %s %s, %s(sp)" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[2],
            instruction.data[1]
        )

    if instruction.type == "CSP2":
        return "%08x %11s %s sp, %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[1]
        )

    if instruction.type in ("CSNG", "System"):
        return "%08x %11s %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower()
        )

    if instruction.type == "CJR":
        return "%08x %11s %s %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[2]
        )

    if instruction.type == "CI2R":
        return "%08x %11s %s %s, %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[2],
            instruction.data[3]
        )

    if instruction.type == "CS":
        return "%08x %11s %s %s, %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[3],
            instruction.data[5]
        )

    if instruction.type == "CJ":
        target_label = find_label(instruction, instruction.data[1])
        return "%08x %11s %s %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[1] if target_label is None else target_label
        )

    if instruction.type == "CIW":
        return "%08x %11s %s %s, sp, %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[2],
            instruction.data[1]
        )

    if instruction.type == "CI2":
        return "%08x %11s %s %s, %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[3],
            instruction.data[1]
        )

    if instruction.type == "CL":
        return "%08x %11s %s %s, %s(%s)" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[4],
            instruction.data[1],
            instruction.data[2]
        )

    if instruction.type == "CSR":
        return "%08x %11s %s %s, %s, %s" % (
            instruction.addr,
            label + ':' if label else '',
            instruction.name.lower(),
            instruction.data[3],
            instruction.data[0],
            instruction.data[1]
        )

    return "%08x" % (instruction.addr)


def find_label(instruction, address):
    if address in instruction.labels[1]:
        return instruction.labels[1][address]
    return None
