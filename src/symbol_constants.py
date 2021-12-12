STT_NOTYPE = 0
STT_OBJECT = 1
STT_FUNC = 2
STT_SECTION = 3
STT_FILE = 4
STT_COMMON = 5
STT_TLS = 6
STT_LOOS = 10
STT_HIOS = 12
STT_LOPROC = 13
STT_SPARC_REGISTER = 13
STT_HIPROC = 15

st_type2string = {
    STT_NOTYPE: "NOTYPE",
    STT_OBJECT: "OBJECT",
    STT_FUNC: "FUNC",
    STT_SECTION: "SECTION",
    STT_FILE: "FILE",
    STT_COMMON: "COMMON",
    STT_TLS: "TLS",
    STT_LOOS: "LOOS",
    STT_HIOS: "HIOS",
    STT_LOPROC: "LOPROC",
    STT_SPARC_REGISTER: "SPARC_REGISTER",
    STT_HIPROC: "HIPROC"
}


# ======================================================================================================================

STB_LOCAL = 0
STB_GLOBAL = 1
STB_WEAK = 2
STB_LOOS = 10
STB_HIOS = 12
STB_LOPROC = 13
STB_HIPROC = 15

st_bind2string = {
    STB_LOCAL: "LOCAL",
    STB_GLOBAL: "GLOBAL",
    STB_WEAK: "WEAK",
    STB_LOOS: "LOOS",
    STB_HIOS: "HIOS",
    STB_LOPROC: "LOPROC",
    STB_HIPROC: "HIPROC"
}


# ======================================================================================================================

STV_DEFAULT = 0
STV_INTERNAL = 1
STV_HIDDEN = 2
STV_PROTECTED = 3
STV_EXPORTED = 4
STV_SINGLETON = 5
STV_ELIMINATE = 6

st_visibility2string = {
    STV_DEFAULT: "DEFAULT",
    STV_INTERNAL: "INTERNAL",
    STV_HIDDEN: "HIDDEN",
    STV_PROTECTED: "PROTECTED",
    STV_EXPORTED: "EXPORTED",
    STV_SINGLETON: "SINGLETON",
    STV_ELIMINATE: "ELIMINATE"
}
