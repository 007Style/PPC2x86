"""
isa_trivia.py — Historical ISA facts, profiles, quotes, and easter egg content.

Exports
-------
ISA_FACTS          list[dict]   — trivia items (isa, text, category)
ISA_PROFILES       dict[str, dict] — one profile per architecture
COMPILER_QUOTES    list[str]    — memorable quotes from ISA/compiler luminaries
KONAMI_UNLOCK_TEXT str          — secret message revealed by Konami code
HIDDEN_MESSAGES    dict[str, str] — keyed by trigger string
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# ISA PROFILES
# ---------------------------------------------------------------------------

ISA_PROFILES: dict[str, dict] = {

    "sparc": {
        "name": "SPARC",
        "vendor": "Sun Microsystems (v8) / SPARC International",
        "year": 1987,
        "bits": 32,          # SPARC v9 extended to 64-bit in 1995
        "endian": "Big (v8); Bi-endian (v9)",
        "registers": 32,     # integer; windowed — 8 globals + 24 in-window
        "description": (
            "Scalable Processor ARChitecture. A clean RISC design from Sun "
            "Microsystems, notable for its register-window mechanism that "
            "eliminates most function-call save/restore overhead."
        ),
        "famous_for": (
            "Register windows; open-standard licensing model; "
            "powering Sun workstations and servers from 1987 to the Oracle era."
        ),
        "died": None,   # UltraSPARC T-series still in production until ~2017
    },

    "alpha": {
        "name": "Alpha AXP",
        "vendor": "Digital Equipment Corporation (DEC)",
        "year": 1992,
        "bits": 64,
        "endian": "Bi-endian",
        "registers": 32,
        "description": (
            "DEC's 64-bit RISC architecture, designed to be the fastest "
            "microprocessor in the world at its launch. Notably, there are no "
            "byte or halfword load/store instructions — all memory ops are "
            "word or doubleword."
        ),
        "famous_for": (
            "Being the first broadly available 64-bit commercial CPU; "
            "Windows NT port; Compaq acquisition; eventual absorption into HP."
        ),
        "died": 2004,
    },

    "mips": {
        "name": "MIPS",
        "vendor": "MIPS Computer Systems / MIPS Technologies",
        "year": 1985,
        "bits": 32,   # MIPS64 released 1999
        "endian": "Bi-endian",
        "registers": 32,
        "description": (
            "Microprocessor without Interlocked Pipeline Stages — the "
            "textbook RISC design. Originated at Stanford under John Hennessy. "
            "Famous for load-delay slots visible to the programmer."
        ),
        "famous_for": (
            "Patterson & Hennessy textbook; SGI workstations; Nintendo 64; "
            "PlayStation 1 & 2; countless embedded controllers."
        ),
        "died": None,   # MIPS64r6 still licensed for embedded
    },

    "pa-risc": {
        "name": "PA-RISC",
        "vendor": "Hewlett-Packard",
        "year": 1986,
        "bits": 32,   # PA-RISC 2.0 added 64-bit in 1996
        "endian": "Big",
        "registers": 32,
        "description": (
            "Precision Architecture RISC. HP's in-house RISC design, known "
            "for its nullification bits on every branch instruction (annulling "
            "the delay-slot instruction based on the branch outcome)."
        ),
        "famous_for": (
            "HP 9000 workstations and servers; nullification delay slots; "
            "being the architecture that Itanium was meant to replace."
        ),
        "died": 2008,
    },

    "itanium": {
        "name": "Itanium (IA-64)",
        "vendor": "Intel / Hewlett-Packard",
        "year": 2001,
        "bits": 64,
        "endian": "Bi-endian",
        "registers": 128,   # 128 integer + 128 FP
        "description": (
            "Explicitly Parallel Instruction Computing (EPIC). Instructions "
            "are grouped into 128-bit bundles of three, with a template "
            "field telling the processor which units each instruction uses. "
            "The compiler, not the hardware, schedules all parallelism."
        ),
        "famous_for": (
            "EPIC architecture; predicated execution on every instruction; "
            "rotating register file; being the most expensive compiler-dependent "
            "architecture ever shipped; gradual commercial failure despite "
            "extraordinary engineering."
        ),
        "died": 2021,
    },

    "68k": {
        "name": "Motorola 68000",
        "vendor": "Motorola",
        "year": 1979,
        "bits": 32,   # 32-bit internal, 24-bit address bus on original
        "endian": "Big",
        "registers": 16,   # 8 data + 8 address
        "description": (
            "A CISC 32-bit microprocessor with a clean, orthogonal instruction "
            "set. Unlike Intel's segmented memory model, the 68k offered a flat "
            "24-bit (later 32-bit) address space, making it the favourite of "
            "systems programmers of its era."
        ),
        "famous_for": (
            "Original Apple Macintosh; Amiga; Atari ST; Sun-1 workstation; "
            "embedded longevity in printers and industrial controllers; "
            "ColdFire derivatives still manufactured today."
        ),
        "died": None,   # ColdFire / MCF5xxx still in production
    },

    "vax": {
        "name": "VAX",
        "vendor": "Digital Equipment Corporation (DEC)",
        "year": 1977,
        "bits": 32,
        "endian": "Little",
        "registers": 16,
        "description": (
            "Virtual Address eXtension. The pinnacle of CISC design — an "
            "instruction set with over 300 opcodes, arbitrary addressing modes "
            "on every operand, and hardware support for queues, strings, and "
            "packed decimal arithmetic."
        ),
        "famous_for": (
            "OpenVMS operating system; scientific computing in the 1980s; "
            "inspiring the RISC movement by showing how complex hardware can "
            "become; DEC's most successful minicomputer line."
        ),
        "died": 2000,
    },

    "ppc": {
        "name": "PowerPC",
        "vendor": "IBM / Motorola / Apple (AIM alliance)",
        "year": 1992,
        "bits": 32,   # PowerPC 64 in 2001
        "endian": "Bi-endian",
        "registers": 32,
        "description": (
            "Performance Optimization With Enhanced RISC. Descended from IBM "
            "POWER, the AIM alliance (Apple, IBM, Motorola) designed PowerPC "
            "to challenge Intel's x86 dominance. Used a separate condition "
            "register file (CR0–CR7) and link register for call/return."
        ),
        "famous_for": (
            "Apple Power Mac and PowerBook lines (1994–2006); Nintendo GameCube "
            "and Wii; Microsoft Xbox 360; IBM POWER servers; AltiVec SIMD."
        ),
        "died": None,   # IBM POWER10 still in production
    },

    "x86": {
        "name": "x86 / x86-64",
        "vendor": "Intel (AMD64 extension by AMD)",
        "year": 1978,
        "bits": 16,   # extended to 32-bit (IA-32) in 1985, 64-bit in 2003
        "endian": "Little",
        "registers": 8,    # 8 in IA-32; 16 in x86-64
        "description": (
            "The most commercially successful CPU architecture in history. "
            "Started as the Intel 8086, grew through 286/386/486 to the "
            "Pentium era, and then had its 64-bit extension (AMD64/EM64T) "
            "standardized in 2003. Variable-length instructions, a segmented "
            "heritage, and remarkable backward compatibility to 1978."
        ),
        "famous_for": (
            "IBM PC and every descendant; backward compatibility spanning "
            "four decades; surviving every RISC challenge; dominating data "
            "centre and desktop compute."
        ),
        "died": None,
    },
}


# ---------------------------------------------------------------------------
# ISA FACTS
# ---------------------------------------------------------------------------

ISA_FACTS: list[dict] = [

    # SPARC (8 facts)
    {"isa": "sparc", "category": "design",
     "text": "SPARC's register windows mean that on a function call, the CPU "
             "simply slides a window pointer — renames registers — rather than "
             "spilling them to memory. A deeply nested call chain can exhaust "
             "all windows, causing a 'window overflow trap'."},
    {"isa": "sparc", "category": "history",
     "text": "The SPARC v8 specification was published as an open standard, "
             "allowing multiple vendors (Fujitsu, Ross Technology, Cypress "
             "Semiconductor) to build competing SPARC CPUs — rare for the era."},
    {"isa": "sparc", "category": "benchmark",
     "text": "SPARC-based Sun workstations dominated CAD and EDA workloads "
             "in the early 1990s. The SPARCstation 1 (1989) at $9,000 offered "
             "12 MIPS, roughly matching a $25,000 VAX 8530."},
    {"isa": "sparc", "category": "design",
     "text": "SPARC v9 made the architecture 64-bit and bi-endian in 1995, "
             "adding 64-bit registers while retaining all v8 integer instructions "
             "unchanged — a notably smooth ISA extension."},
    {"isa": "sparc", "category": "quirk",
     "text": "The SPARC architecture specifies a branch delay slot: the "
             "instruction after a branch always executes before the branch "
             "takes effect. Compilers learned to fill these slots productively, "
             "but it frequently surprises assembly programmers."},
    {"isa": "sparc", "category": "history",
     "text": "Oracle acquired Sun in 2010 and continued shipping SPARC T-series "
             "(Niagara) processors emphasising thread count over single-thread "
             "speed — a controversial strategy that eventually lost to x86 in "
             "the data centre."},
    {"isa": "sparc", "category": "compiler",
     "text": "GCC's SPARC backend has to handle 'leaf function optimisation': "
             "functions that make no calls can skip allocating a register "
             "window entirely, saving the window-slide overhead."},
    {"isa": "sparc", "category": "design",
     "text": "SPARC specifies NO multiply or divide instructions in the v8 "
             "base ISA — they are optional extensions. Early SPARC chips "
             "required a software trap to a firmware routine for integer "
             "multiply/divide."},

    # Alpha (8 facts)
    {"isa": "alpha", "category": "design",
     "text": "Alpha has no byte or halfword load/store instructions in the "
             "base ISA. All loads return a 64-bit value. Byte manipulation "
             "uses special 'byte zap' (ZAP/ZAPNOT) and 'extract' instructions "
             "to isolate sub-word fields."},
    {"isa": "alpha", "category": "history",
     "text": "Windows NT was ported to Alpha by 1993, making DEC's chip one "
             "of only four architectures NT ever ran on (alongside x86, MIPS, "
             "and PowerPC). NT/Alpha was discontinued in 1999 after the "
             "Compaq acquisition."},
    {"isa": "alpha", "category": "benchmark",
     "text": "The 21064 (EV4) launched in 1992 at 150–200 MHz and was "
             "measurably faster than any x86 processor for floating-point "
             "workloads until the Pentium Pro arrived in 1995."},
    {"isa": "alpha", "category": "design",
     "text": "Alpha's floating-point model explicitly exposes IEEE traps as "
             "software completions — the hardware can optionally deliver FP "
             "exceptions to software, or silently produce the IEEE-defined "
             "result. This fine-grained control was unusual for a RISC design."},
    {"isa": "alpha", "category": "history",
     "text": "Compaq acquired DEC in 1998, then HP acquired Compaq in 2002. "
             "HP killed Alpha development in 2004, directing customers to "
             "migrate to Itanium — a migration that many never completed."},
    {"isa": "alpha", "category": "quirk",
     "text": "Alpha integer registers are strictly 64-bit; there are no 32-bit "
             "register views. A 32-bit ADD instruction (ADDL) produces a "
             "sign-extended 64-bit result — keeping the upper 32 bits coherent."},
    {"isa": "alpha", "category": "compiler",
     "text": "The Alpha AXP port of GCC was notable for aggressive scheduling "
             "optimisations enabled by Alpha's in-order, dual-issue pipeline "
             "and the lack of interlocks — mis-schedule and you stall."},
    {"isa": "alpha", "category": "history",
     "text": "Several Alpha designs (EV6, EV7) were actually fabricated by "
             "Samsung under license, not by DEC/Compaq. The Samsung Alpha "
             "21264A ran at 1.25 GHz — among the highest clock rates of "
             "any CPU available in 2003."},

    # MIPS (8 facts)
    {"isa": "mips", "category": "history",
     "text": "MIPS stands for Microprocessor without Interlocked Pipeline "
             "Stages. The original R2000 (1985) truly had no interlocks — "
             "if you read a register one cycle after a load, you got garbage. "
             "The hardware assumed the compiler would insert a NOP or useful "
             "instruction in the load-delay slot."},
    {"isa": "mips", "category": "benchmark",
     "text": "The SGI Indigo² workstation with an R4400 (250 MHz, 1994) "
             "performed Jurassic Park's CGI dinosaur rendering and became "
             "the iconic workstation of the early 3D era."},
    {"isa": "mips", "category": "design",
     "text": "MIPS introduced the HI/LO register pair for multiply/divide — "
             "results land in HI (high word) and LO (low word), then MFHI/MFLO "
             "copy them to general registers. This avoids a wide result bus "
             "but requires a pipeline interlocking stall on early chips."},
    {"isa": "mips", "category": "quirk",
     "text": "The branch delay slot in MIPS means the instruction after every "
             "branch always executes. The MIPS32r6 / MIPS64r6 revision "
             "(2014) finally eliminated delay slots, breaking binary "
             "compatibility with all prior MIPS code."},
    {"isa": "mips", "category": "history",
     "text": "Nintendo used a custom MIPS R4300i (NEC VR4300) in the Nintendo "
             "64 (1996), running at 93.75 MHz. Its 64-bit MIPS core was largely "
             "used in 32-bit mode due to memory constraints."},
    {"isa": "mips", "category": "compiler",
     "text": "MIPS's calling convention assigns $a0–$a3 for function arguments, "
             "$v0–$v1 for return values, and $t0–$t9 as caller-saved temporaries. "
             "The explicit split between caller-saved and callee-saved registers "
             "became a model for subsequent RISC ABIs."},
    {"isa": "mips", "category": "history",
     "text": "Wave Computing acquired the MIPS architecture in 2018 and "
             "briefly open-sourced the MIPS ISA in 2019, before financial "
             "difficulties led to bankruptcy and acquisition by MIPS Tech LLC."},
    {"isa": "mips", "category": "design",
     "text": "MIPS16 and microMIPS are compressed 16-bit instruction encodings "
             "designed for embedded code density, similar in spirit to ARM "
             "Thumb. MicroMIPS can reduce code size by 30–40% vs standard MIPS."},

    # PA-RISC (8 facts)
    {"isa": "pa-risc", "category": "design",
     "text": "Every PA-RISC branch instruction has a nullification bit (the 'n' "
             "bit). When set, the instruction in the branch delay slot is "
             "annulled (turned into a NOP) if the branch is not taken — the "
             "opposite of SPARC's always-execute model."},
    {"isa": "pa-risc", "category": "history",
     "text": "HP introduced PA-RISC with the HP 9000/840 in 1986 as a "
             "replacement for their HP 3000 (stack-based) and HP 9000 "
             "(Motorola 68k) lines. It powered HP's workstations and servers "
             "for over two decades."},
    {"isa": "pa-risc", "category": "design",
     "text": "PA-RISC 2.0 (1996) extended the architecture to 64-bit with a "
             "fully backward-compatible ISA. The 64-bit PA-RISC 8000 processor "
             "implemented out-of-order execution with a very large (56-entry) "
             "reorder buffer for a RISC design of that era."},
    {"isa": "pa-risc", "category": "compiler",
     "text": "HP's optimising compiler for PA-RISC pioneered several techniques "
             "later adopted broadly: software pipelining, modulo scheduling, "
             "and predicated execution (via the nullification mechanism)."},
    {"isa": "pa-risc", "category": "history",
     "text": "PA-RISC was the primary architecture for HP-UX. When HP partnered "
             "with Intel on Itanium, they promised PA-RISC customers a binary "
             "translation layer (IA-32 EL / HP-UX on Itanium) — it worked but "
             "with significant performance penalties."},
    {"isa": "pa-risc", "category": "quirk",
     "text": "PA-RISC stores function pointers as pointers to a descriptor "
             "structure (a 'plabel'), not directly to code. This indirection "
             "enables position-independent code and shared library support, "
             "but surprises C programmers expecting a function pointer to "
             "equal the instruction address."},
    {"isa": "pa-risc", "category": "history",
     "text": "The last PA-RISC processor, the PA-8900, was introduced in 2005 "
             "and produced until 2008. HP shipped PA-RISC-based Integrity "
             "servers until 2008, then migrated HP-UX entirely to Itanium."},
    {"isa": "pa-risc", "category": "design",
     "text": "PA-RISC has a 'space register' model for memory protection — "
             "each memory reference includes an implicit space register "
             "selecting which protection domain the address belongs to, "
             "without changing the virtual address itself."},

    # Itanium (8 facts)
    {"isa": "itanium", "category": "design",
     "text": "Every Itanium instruction is 41 bits wide. Three instructions "
             "are packed into a 128-bit bundle alongside a 5-bit template "
             "field that tells the processor which execution units each slot "
             "targets. The compiler fills all three slots or inserts NOPs."},
    {"isa": "itanium", "category": "design",
     "text": "Itanium has 64 integer registers arranged as a rotating register "
             "file for software-pipelined loops — on each BRLC (branch with "
             "loop count), the register base pointer advances, eliminating "
             "the need to copy accumulators between iterations."},
    {"isa": "itanium", "category": "history",
     "text": "Intel and HP announced Itanium in 1994, originally called 'Merced'. "
             "It shipped in 2001 — seven years of development. Critics noted "
             "that x86-64 (AMD64) shipped in 2003, two years later, and ran "
             "all existing x86 software natively."},
    {"isa": "itanium", "category": "compiler",
     "text": "Itanium's performance is almost entirely compiler-dependent. "
             "Without a world-class optimising compiler performing EPIC "
             "scheduling, IA-64 hardware idles on NOPs. Intel's own icc "
             "produced measurably better Itanium code than GCC for years."},
    {"isa": "itanium", "category": "design",
     "text": "Itanium's predication system lets every instruction carry a "
             "1-bit predicate register. If the predicate is false, the "
             "instruction becomes a NOP. This enables if-conversion: entire "
             "if/else blocks execute in parallel with no branches."},
    {"isa": "itanium", "category": "history",
     "text": "Microsoft dropped Itanium support in Windows with Windows Server "
             "2008 R2 (2010). Red Hat dropped it in RHEL 6 (2010). The last "
             "Itanium chip, the Kittson (9700 series), shipped in 2017 for "
             "HP-UX customers with nowhere else to go."},
    {"isa": "itanium", "category": "quirk",
     "text": "Itanium's IA-32 compatibility mode (executing legacy x86 code) "
             "was spectacularly slow — hardware emulation on a chip designed "
             "for EPIC scheduling produced x86 performance 5–10× slower than "
             "contemporary Pentium 4 processors."},
    {"isa": "itanium", "category": "benchmark",
     "text": "At peak, Itanium 2 Montecito (dual-core, 2006) achieved excellent "
             "floating-point throughput on HPC workloads compiled with Intel's "
             "compiler — competitive with Opteron. The hardware was capable; "
             "the ecosystem was not."},

    # 68k (8 facts)
    {"isa": "68k", "category": "design",
     "text": "The 68000 is often called the first 'programmer-friendly' CISC: "
             "8 data registers and 8 address registers, every instruction "
             "working on any register, and a flat 24-bit address space — no "
             "segments, no pages visible to the programmer."},
    {"isa": "68k", "category": "history",
     "text": "The original Apple Macintosh (1984) used a Motorola 68000 at "
             "8 MHz. Apple stuck with the 68k family (68020, 68030, 68040) "
             "until 1994, when they switched to PowerPC. The Mac OS ran on "
             "68k for a full decade."},
    {"isa": "68k", "category": "history",
     "text": "The Amiga 1000 (1985) used a 68000 with a companion set of "
             "custom chips (Agnus, Denise, Paula) for graphics, DMA, and "
             "sound. The architecture was far ahead of contemporary PCs for "
             "multimedia tasks."},
    {"isa": "68k", "category": "design",
     "text": "The 68020 introduced a 32-bit address bus, a 256-byte instruction "
             "cache, and a proper barrel shifter. It also added the BFEXTU / "
             "BFINS bit-field instructions that are still unmatched in "
             "expressiveness in any RISC ISA."},
    {"isa": "68k", "category": "quirk",
     "text": "The 68000 trap mechanism executes a trap handler for almost "
             "everything: divide-by-zero, illegal instruction, privilege "
             "violation, address error, and even unimplemented floating-point "
             "instructions (caught by the 68881 coprocessor protocol)."},
    {"isa": "68k", "category": "compiler",
     "text": "GCC's 68k port was one of the first non-VAX targets, written "
             "by Richard Stallman himself. The register-rich orthogonal ISA "
             "made code generation comparatively straightforward versus x86's "
             "constrained register file."},
    {"isa": "68k", "category": "history",
     "text": "The ColdFire processor family (1994) is a trimmed-down 68k "
             "subset targeting embedded markets. It removed some addressing "
             "modes and instructions for die-size reasons but retains binary "
             "compatibility with a subset of 68k code."},
    {"isa": "68k", "category": "design",
     "text": "Unlike x86, which grows flags organically, the 68k Condition "
             "Code Register (CCR) is a clean 5-bit field: C (carry), V "
             "(overflow), Z (zero), N (negative), X (extend). The X bit "
             "acts as a sticky carry for multi-precision arithmetic."},

    # VAX (5 facts)
    {"isa": "vax", "category": "design",
     "text": "VAX instructions can reference memory operands with any of "
             "twelve addressing modes — including auto-increment, "
             "auto-decrement, and indexed deferred — on every operand of "
             "every instruction. This orthogonality was the envy of "
             "programmers and the nightmare of microcode engineers."},
    {"isa": "vax", "category": "history",
     "text": "VMS (Virtual Memory System), developed by Dave Cutler and his "
             "team at DEC, shipped in 1977 alongside the VAX 11/780. It is "
             "still maintained and sold as OpenVMS and ran on Alpha and "
             "Itanium after VAX hardware was discontinued."},
    {"isa": "vax", "category": "benchmark",
     "text": "The VAX 11/780 (1977) was informally defined as '1 MIPS' — "
             "one million instructions per second. For years, 'VAX MIPS' was "
             "used as the baseline unit of compute across the industry."},
    {"isa": "vax", "category": "quirk",
     "text": "VAX has native hardware support for packed BCD arithmetic, "
             "string operations, and queue manipulation — not traps to "
             "microcode, but actual machine instructions. The MATCHC "
             "instruction finds a substring in memory."},
    {"isa": "vax", "category": "history",
     "text": "The VAX architecture directly inspired the RISC movement: "
             "Andrew Patterson and David Ditzel's 1980 paper 'The Case for "
             "the Reduced Instruction Set Computer' explicitly used VAX as "
             "the cautionary CISC example, kickstarting RISC research at "
             "Berkeley and Stanford."},

    # PPC (extra facts)
    {"isa": "ppc", "category": "history",
     "text": "The AIM alliance (Apple, IBM, Motorola) formed in 1991 to create "
             "a common RISC platform that could challenge Intel. The first "
             "PowerPC chip, the 601, shipped in 1993 and powered the first "
             "Power Macintosh in 1994."},
    {"isa": "ppc", "category": "design",
     "text": "PowerPC has eight 4-bit condition register fields (CR0–CR7). "
             "Integer comparisons set CR0 by default; floating-point ops set "
             "CR1. The other six fields are available for arbitrary use, "
             "enabling complex boolean expressions without branches."},
    {"isa": "ppc", "category": "quirk",
     "text": "PPC's load-store architecture means there is no 'ADD [mem], reg' "
             "instruction. Every computation touches registers only; memory "
             "access is strictly load/store. This forced x86 programmers to "
             "rethink idioms but simplified processor design significantly."},
    {"isa": "ppc", "category": "history",
     "text": "Apple's transition from PowerPC to Intel (2006) was announced "
             "at WWDC 2005. Steve Jobs revealed that Mac OS X had been compiled "
             "for x86 since its inception — a 'secret Intel project' — and "
             "showed a working Intel Mac on stage."},

    # x86 (extra facts)
    {"isa": "x86", "category": "history",
     "text": "The Intel 8086 was designed in 1976 by a small team led by "
             "Stephen Morse. The segmented memory model — four 64 KB segments "
             "addressable at once — was chosen to allow 20-bit addresses with "
             "16-bit registers, and has haunted x86 programmers ever since."},
    {"isa": "x86", "category": "design",
     "text": "The x86-64 (AMD64) ISA extension, designed by AMD and shipped "
             "in the Athlon 64 (2003), solved decades of register starvation: "
             "eight new general-purpose registers (R8–R15), 64-bit addresses, "
             "and SSE2 mandatory. Intel adopted it under the name EM64T."},
    {"isa": "x86", "category": "quirk",
     "text": "Writing to a 32-bit register on x86-64 (e.g. EAX) implicitly "
             "zero-extends the result to the full 64-bit RAX. Writing to a "
             "16-bit register (AX) does NOT zero-extend — a legacy compatibility "
             "quirk that continues to surprise code generators."},
    {"isa": "x86", "category": "compiler",
     "text": "x86 has a 'partial register stall' hazard: writing to AL then "
             "reading RAX causes a pipeline merge operation that can cost "
             "several cycles on some microarchitectures. Modern compilers "
             "avoid partial-register writes through movzx idioms."},
]


# ---------------------------------------------------------------------------
# COMPILER / ISA QUOTES
# ---------------------------------------------------------------------------

COMPILER_QUOTES: list[str] = [
    # Patterson & Hennessy
    '"The most important computer languages of the future will be those that '
    'emphasize simplicity." — David Patterson',

    '"RISC is not just a style; it is a discipline." — John Hennessy',

    '"A computer is a machine that can be instructed to carry out sequences '
    'of arithmetic or logical operations automatically. The amazing thing '
    'is how much humans disagree about how those instructions should look." '
    '— Andrew Tanenbaum',

    '"The VAX is designed to make everything the same: any instruction can '
    'reference any addressing mode on any operand. RISC makes everything '
    'different: fast paths and slow paths are explicit." — David Patterson, '
    '"The Case for the Reduced Instruction Set Computer" (1980)',

    '"Compatibility means deliberately repeating other people\'s mistakes." '
    '— David Wheeler',

    '"Measuring programming progress by lines of code is like measuring '
    'aircraft building progress by weight." — Bill Gates',

    '"Premature optimization is the root of all evil." — Donald Knuth',

    '"The most effective debugging tool is still careful thought, coupled '
    'with judiciously placed print statements." — Brian Kernighan',

    '"There are only two kinds of programming languages: those that people '
    'always complain about and those that nobody uses." — Bjarne Stroustrup',

    '"Software is a great combination between artistry and engineering." '
    '— Bill Gates',

    # Jim Keller (chip architect)
    '"We kept adding complexity to x86 and then hiding it. Microcode, '
    'out-of-order engines, reorder buffers — all to make a 1978 ISA run '
    'fast in 2005. That\'s both an impressive engineering achievement and '
    'a profound architectural tragedy." — Jim Keller (paraphrased)',

    '"Every instruction set extension is a mortgage on future chip area." '
    '— Jim Keller',

    # Dave Cutler
    '"A good operating system is one that doesn\'t get in your way." '
    '— Dave Cutler, architect of VMS and Windows NT',

    '"I designed VMS on VAX because VAX was the right architecture at the '
    'time. I designed NT to be portable because I\'d learned that no '
    'architecture is right forever." — Dave Cutler',

    # Fred Brooks
    '"There is no single development, in either technology or management '
    'technique, which by itself promises even one order of magnitude '
    'improvement within a decade in productivity, in reliability, in '
    'simplicity." — Fred Brooks, "No Silver Bullet" (1986)',

    '"The programmer, like the poet, works only slightly removed from pure '
    'thought-stuff. He builds his castles in the air, from air, creating '
    'by exertion of the imagination." — Fred Brooks, "The Mythical Man-Month"',

    # Chuck Thacker
    '"The Alto was a thought experiment: what if every programmer had a '
    'personal machine? The instruction set was almost incidental." '
    '— Chuck Thacker, on the Xerox Alto',

    # General ISA wisdom
    '"An instruction set is a contract between hardware and software that '
    'outlasts both." — Anonymous',

    '"The tragedy of Itanium was not that it failed. The tragedy was that '
    'it worked exactly as designed — and the design was wrong." — Anonymous',

    '"Every RISC architecture is a reaction to VAX. Every CISC defence '
    'is a concession to compatibility." — Anonymous',

    '"Delay slots are the assembly programmer\'s way of saying: \'I noticed '
    'you were about to waste a cycle, so I moved my problem forward in '
    'time.\'" — Anonymous',

    '"The condition register file is what PowerPC got right that x86 still '
    'hasn\'t copied." — Anonymous',

    '"Endianness is not a religious war. It is an engineering error that '
    'metastasized into a religious war." — Anonymous',
]


# ---------------------------------------------------------------------------
# EASTER EGG CONTENT
# ---------------------------------------------------------------------------

KONAMI_UNLOCK_TEXT: str = """\
╔══════════════════════════════════════════════════════════════════╗
║          ★  KONAMI CODE ACCEPTED  ★                              ║
║                                                                  ║
║   You have unlocked the ISA GRAVEYARD.                           ║
║                                                                  ║
║   Here lie the architectures that dared to challenge x86:        ║
║                                                                  ║
║   † Alpha AXP     (1992–2004)  "Fastest ever. Gone too soon."   ║
║   † PA-RISC       (1986–2008)  "Precision was its middle name." ║
║   † Itanium       (2001–2021)  "Explicitly parallel in failure."║
║   † MIPS (desktop)(1985–2002)  "Textbook perfect, market lost." ║
║   † VAX           (1977–2000)  "CISC pinnacle. RISC casualty."  ║
║                                                                  ║
║   Still alive:                                                   ║
║   ♥ PowerPC / POWER  (in your Xbox, your car, and IBM cloud)    ║
║   ♥ ARM             (in your pocket right now)                  ║
║   ♥ RISC-V          (the next challenger)                       ║
║   ♥ x86-64          (the immortal cockroach of ISAs)            ║
║                                                                  ║
║   "Any sufficiently successful ISA is indistinguishable         ║
║    from a mistake that won." — PPC2x86 Fortune Cookie           ║
╚══════════════════════════════════════════════════════════════════╝
"""

HIDDEN_MESSAGES: dict[str, str] = {

    "title_7clicks": (
        "You clicked the title 7 times.\n\n"
        "Congratulations. You have discovered the ISA Graveyard.\n"
        "A place where retired architectures rest in silicon peace.\n\n"
        "Alpha. PA-RISC. Itanium. They all believed they would win.\n"
        "They were not wrong about performance. They were wrong about timing."
    ),

    "status_bar_quote": (
        "\"The best ISA is the one that ships.\" — Anonymous chipmaker"
    ),

    "about_hidden_zone": (
        "══════════════════════════════════════\n"
        "  HALL OF FAME: ISA LUMINARIES\n"
        "══════════════════════════════════════\n"
        "  John Cocke      — RISC pioneer, IBM 801\n"
        "  David Patterson — Berkeley RISC, SPARC\n"
        "  John Hennessy   — Stanford MIPS\n"
        "  Jim Keller      — Alpha EV6, K8, A4/A5\n"
        "  Dave Cutler     — VMS, Windows NT\n"
        "  Fred Brooks     — OS/360, Mythical Man-Month\n"
        "  Andy Bechtolsheim — Sun-1, SPARC hardware\n"
        "  Bob Colwell     — Intel P6 microarchitect\n"
        "  Gerry Emery     — Itanium lead architect\n"
        "  Eric Traut      — Apple/NeXT x86 emulator (Rosetta)\n"
        "══════════════════════════════════════\n"
        "  \"An ISA is forever. Choose wisely.\"\n"
        "══════════════════════════════════════"
    ),

    "compiler_quotes_unlock": (
        "Secret menu unlocked: Show Compiler Quotes.\n"
        "Check the Help menu."
    ),

    "random_instruction_fact": (
        "Did you know? The NOP instruction on x86 is actually XCHG EAX, EAX "
        "— a single-byte encoding (0x90) that was originally the XCHG opcode "
        "with EAX as both operands. It became the canonical NOP by accident."
    ),

    "isa_graveyard_epitaphs": (
        "ALPHA : 'I computed π to 50 decimal places before your JVM loaded.'\n"
        "ITANIUM: 'The compiler was supposed to do this part.'\n"
        "PA-RISC: 'HP promised Itanium would be better. HP was wrong.'\n"
        "VAX    : 'MATCHC, LOCC, MOVC5 — features x86 still doesn\\'t have.'\n"
        "MIPS   : 'I taught a generation of CS students. Then they all bought Intel.'"
    ),
}
