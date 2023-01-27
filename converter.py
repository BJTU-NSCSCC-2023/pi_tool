import typing as typ
import argparse
import sys
from pathlib import Path

tblRegName2Id: typ.Dict[str, int] = {
	"zero": 0,
	"at": 1,
	**{f"v{i}": i + 2 for i in range(0, 2)},
	**{f"a{i}": i + 4 for i in range(0, 4)},
	**{f"t{i}": i + 8 for i in range(0, 8)},
	**{f"s{i}": i + 16 for i in range(0, 8)},
	**{f"t{i + 8}": i + 24 for i in range(0, 2)},
	**{f"k{i}": i + 26 for i in range(0, 2)},
	"gp": 28,
	"sp": 29,
	"fp": 30,
	"ra": 31,
}

tblRegId2Name: typ.Dict[int, str] = {i: name for (name, i) in tblRegName2Id.items()}

tblInstInfo: typ.Dict[str, typ.Tuple[str, int | typ.Tuple[int, int]]] = {
	"add": ("R", (0x0, 0x20)),
	"sub": ("R", (0x0, 0x22)),
	"addi": ("I", 0x8),
	"addu": ("R", (0x0, 0x21)),
	"subu": ("R", (0x0, 0x23)),
	"addiu": ("I", 0x9),
	"mult": ("R", (0x0, 0x18)),
	"div": ("R", (0x0, 0x1a)),
	"multu": ("R", (0x0, 0x19)),
	"divu": ("R", (0x0, 0x1b)),
	"mfhi": ("R", (0x0, 0x10)),
	"mflo": ("R", (0x0, 0x12)),
	"and": ("R", (0x0, 0x24)),
	"or": ("R", (0x0, 0x25)),
	"nor": ("R", (0x0, 0x27)),
	"xor": ("R", (0x0, 0x26)),
	"andi": ("I", 0xc),
	"ori": ("I", 0xd),
	"xori": ("I", 0xe),
	"sll": ("R", (0x0, 0x0)),
	"srl": ("R", (0x0, 0x2)),
	"sra": ("R", (0x0, 0x3)),
	"sllv": ("R", (0x0, 0x4)),
	"srlv": ("R", (0x0, 0x6)),
	"srav": ("R", (0x0, 0x7)),
	"slt": ("R", (0x0, 0x2a)),
	"sltu": ("R", (0x0, 0x2b)),
	"slti": ("I", 0xa),
	"sltiu": ("I", 0xb),
	"j": ("J", 0x2),
	"jal": ("J", 0x3),
	"jr": ("R", (0x0, 0x8)),
	"jalr": ("R", (0x0, 0x9)),
	"beq": ("I", 0x4),
	"bne": ("I", 0x5),
	"syscall": ("R", (0x0, 0xc)),
	"lui": ("I", 0xf),
	"lb": ("I", 0x20),
	"lbu": ("I", 0x24),
	"lh": ("I", 0x21),
	"lhu": ("I", 0x25),
	"lw": ("I", 0x23),
	"sb": ("I", 0x28),
	"sh": ("I", 0x29),
	"sw": ("I", 0x2b),
	"ll": ("I", 0x30),
	"sc": ("I", 0x38)
}


class Inst:
	def __init__(self, instName: str, instType: typ.Literal["R", "I", "J"]):
		if instName not in tblInstInfo.keys():
			raise LookupError(f"Invalid instruction name [{instName}].")
		match instType:
			case "R":
				if tblInstInfo[instName][0] != "R":
					raise LookupError(f"Instruction [{instName}] is not R-Type inst.")
				self.name = instName
				self.op = tblInstInfo[self.name][1][0]
				self.func = tblInstInfo[self.name][1][1]
			case "I":
				if tblInstInfo[instName][0] != "I":
					raise LookupError(f"Instruction [{instName}] is not I-Type inst.")
				self.name = instName
				self.op = tblInstInfo[self.name][1][0]
			case "J":
				if tblInstInfo[instName][0] != "J":
					raise LookupError(f"Instruction [{instName}] is not J-Type inst.")
				self.name = instName
				self.op = tblInstInfo[self.name][1][0]
			case _:
				raise ValueError(f"instType should be one of 'R', 'I' or 'J', but [{instType}] is found.")

	def to_bits(self, base: int = 2) -> str:
		raise NotImplementedError()

	def __str__(self) -> str:
		raise NotImplementedError()

	def to_detailed(self) -> str:
		raise NotImplementedError()

	@staticmethod
	def parse_reg(r: str):
		r: str = r.strip()
		if len(r) < 1 or r[0] != "$":
			raise ValueError(f"Error when parsing [{r}] for inst.")
		r = r[1:]
		if r.isnumeric():
			r: int = int(r)
		if isinstance(r, str):
			if r not in tblRegName2Id.keys():
				raise ValueError(f"Invalid reg name [{r}].")
			return r
		elif isinstance(r, int):
			if r not in tblRegId2Name.keys():
				raise ValueError(f"Invalid reg id [{r}].")
			return tblRegId2Name[r]
		else:
			raise TypeError(f"rs should be str or int!")

	@staticmethod
	def parse_imm(imm: str):
		imm = imm.strip()
		match imm[0:2]:
			case ["0x" | "0X"]:
				return int(imm, 16)
			case ["0b" | "0B"]:
				return int(imm, 2)
			case _:
				return int(imm, 10)


class InstRType(Inst):
	def __init__(self, instName: str, ctx: str):
		Inst.__init__(self, instName, "R")
		if not isinstance(ctx, str):
			raise ValueError(f"ctx should be str, not [{type(ctx)}]")
		rs = "zero"
		rt = "zero"
		rd = "zero"
		shamt = 0
		if self.name in ["mult", "div", "multu", "divu"]:
			rs, rt = ctx.split(",", 1)
			rs = Inst.parse_reg(rs)
			rt = Inst.parse_reg(rt)
		elif self.name in ["sll", "srl", "sra"]:
			rd, rt, shamt = ctx.split(",", 2)
			rd = Inst.parse_reg(rd)
			rt = Inst.parse_reg(rt)
			shamt = Inst.parse_imm(shamt)
		elif self.name in ["jr", "jalr"]:
			rs = Inst.parse_reg(ctx)
		elif self.name in ["sllv", "srlv", "srav"]:
			rd, rt, rs = ctx.split(",", 2)
			rd = Inst.parse_reg(rd)
			rt = Inst.parse_reg(rt)
			rs = Inst.parse_reg(rs)
		elif self.name in ["syscall"]:
			pass
		elif self.name in ["add", "sub", "addu", "subu", "and", "or", "nor", "xor", "andi", "ori", "xori"]:
			rd, rs, rt = ctx.split(",", 2)
			rd = Inst.parse_reg(rd)
			rt = Inst.parse_reg(rt)
			rs = Inst.parse_reg(rs)
		elif self.name in ["mfhi", "mflo"]:
			rd = Inst.parse_reg(ctx)
		else:
			raise LookupError()

		self.rs = rs
		self.rt = rt
		self.rd = rd
		self.shamt = shamt

	def __str__(self):
		if self.name in ["mult", "div", "multu", "divu"]:
			return f"{self.name} ${self.rs}, ${self.rt}"
		elif self.name in ["sll", "srl", "sra"]:
			return f"{self.name} ${self.rd}, ${self.rt}, ${hex(self.shamt)}"
		elif self.name in ["jr", "jalr"]:
			return f"{self.name} ${self.rs}"
		elif self.name in ["sllv", "srlv", "srav"]:
			return f"{self.name} ${self.rd}, ${self.rt}, ${self.rs}"
		elif self.name in ["syscall"]:
			return f"{self.name}"
		elif self.name in ["add", "sub", "addu", "subu", "and", "or", "nor", "xor", "andi", "ori", "xori"]:
			return f"{self.name} ${self.rd}, ${self.rs}, ${self.rt}"
		elif self.name in ["mfhi", "mflo"]:
			return f"{self.name} ${self.rd}"
		else:
			raise LookupError()

	def to_bits(self, base: int = 2) -> str:
		binaryFormS = f"{self.op:06b}{tblRegName2Id[self.rs]:05b}{tblRegName2Id[self.rt]:05b}{tblRegName2Id[self.rd]:05b}{self.shamt:05b}{self.func:06b}"
		match base:
			case 2:
				return binaryFormS
			case 16:
				return f"{int('0b' + binaryFormS, 2):08x}"
			case _:
				raise ValueError(f"Invalid base [{base}]")

	def to_detailed(self) -> str:
		return f"op={self.op:06b} rs={tblRegName2Id[self.rs]:05b} rt={tblRegName2Id[self.rt]:05b} " \
			   f"rd={tblRegName2Id[self.rd]:05b} sh={self.shamt:05b} func={self.func:06b}"
		pass


class InstIType(Inst):
	def __init__(self, instName: str, ctx: str):
		Inst.__init__(self, instName, "I")
		if not isinstance(ctx, str):
			raise ValueError(f"ctx should be str, not [{type(ctx)}]")
		rs = "zero"
		rt = "zero"
		imm = 0
		if self.name in ["addi", "addiu", "andi", "ori", "xori", "slti", "sltiu", "beq", "bne"]:
			rt, rs, imm = ctx.split(",", 2)
			rt = Inst.parse_reg(rt)
			rs = Inst.parse_reg(rs)
			imm = Inst.parse_imm(imm)
		elif self.name in ["lui"]:
			rt, imm = ctx.split(",", 1)
			rt = Inst.parse_reg(rt)
			imm = Inst.parse_imm(imm)
		elif self.name in ["lb", "lbu", "lh", "lhu", "lw", "sb", "sh", "sw", "ll", "sc"]:
			rt, imm_rs = ctx.split(",", 1)
			imm, rs = ctx.split("(", 1)
			rs, tmp = ctx.split(")", 1)
			tmp: str
			if len(tmp.strip()) != 0:
				raise ValueError(f"[{imm_rs}] format error!")
			rt = Inst.parse_reg(rt)
			imm = Inst.parse_imm(imm)
			rs = Inst.parse_reg(rs)
		else:
			raise LookupError()
		self.rs = rs
		self.rt = rt
		self.imm = imm

	def __str__(self):
		if self.name in ["addi", "addiu", "andi", "ori", "xori", "slti", "sltiu", "beq", "bne"]:
			return f"{self.name} ${self.rt}, ${self.rs}, ${hex(self.imm)}"
		elif self.name in ["lui"]:
			return f"{self.name} ${self.rt}, {hex(self.imm)}"
		elif self.name in ["lb", "lbu", "lh", "lhu", "lw", "sb", "sh", "sw", "ll", "sc"]:
			return f"{self.name} ${self.rt}, {hex(self.imm)}(${self.rs})"
		else:
			raise LookupError()

	def to_bits(self, base: int = 2) -> str:
		binaryFormS = f"{self.op:06b}{tblRegName2Id[self.rs]:05b}{tblRegName2Id[self.rt]:05b}{self.imm:016b}"
		match base:
			case 2:
				return binaryFormS
			case 16:
				return f"{int('0b' + binaryFormS, 2):08x}"
			case _:
				raise ValueError(f"Invalid base [{base}]")

	def to_detailed(self) -> str:
		return f"op={self.op:06b} rs={self.rs:05b} rt={self.rt:05b} imm={self.imm:016b}"


class InstJType(Inst):
	def __init__(self, instName: str, ctx: str):
		Inst.__init__(self, instName, "J")
		if not isinstance(ctx, str):
			raise ValueError(f"ctx should be str, not [{type(ctx)}]")
		addr = 0
		if self.name in ["j", "jal"]:
			addr = Inst.parse_imm(ctx)
		else:
			raise LookupError()
		self.addr = addr

	def __str__(self):
		if self.name in ["j", "jal"]:
			return f"{self.name} {hex(self.addr)}"
		else:
			raise LookupError()

	def to_bits(self, base: int = 2) -> str:
		binaryFormS = f"{self.op:06b}{self.addr:026b}"
		match base:
			case 2:
				return binaryFormS
			case 16:
				return f"{int('0b' + binaryFormS, 2):08x}"
			case _:
				raise ValueError(f"Invalid base [{base}]")

	def to_detailed(self) -> str:
		return f"op={self.op:06b} addr={self.addr:026b}"


argParser = argparse.ArgumentParser(
	prog="mips-converter",
	description="Hex form <=> MIPS instructions",
)
argParser.add_argument("srcFilePath", action="store", help="Source file path.", nargs=1)
argParser.add_argument("-o", action="store", dest="outputFilePath", default="a.txt", help="Where to save output file.")
argParser.add_argument(
	"--func", choices=["h2i", "i2h"], required=True,
	help="'h2i': hex => instruction, 'i2h': instruction => hex"
)
argParser.add_argument("--verbose", action="store_true", default=False, dest="verbose", help="Verbose process.")


def check_args(args):
	srcFilePath = Path(args.srcFilePath[0])
	dstFilePath = Path(args.outputFilePath)
	if not srcFilePath.is_file():
		raise FileNotFoundError(f"Not found srcFile{srcFilePath}")
	dstFilePath.touch(exist_ok=True)
	if not dstFilePath.is_file():
		raise PermissionError("Can not create file.")
	return srcFilePath, dstFilePath, args.func, args.verbose


def hex2inst(srcFilePath: Path, dstFilePath: Path):
	raise NotImplementedError("TODO")


def inst2hex(srcFilePath: Path, dstFilePath: Path, verbose: bool):
	fp = dstFilePath.open(mode="w")
	instList: typ.List[str] = []
	for line in srcFilePath.open().readlines():
		for inst in line.strip().split(";"):
			inst = inst.strip().lower()
			if len(inst) > 0:
				instList.append(inst)
	for inst in instList:
		instName, instCtx = inst.split(" ", 1)
		if instName not in tblInstInfo.keys():
			raise LookupError(f"Invalid instruction name [{instName}].")
		match tblInstInfo[instName][0]:
			case "R":
				inst = InstRType(instName, ctx=instCtx)
			case "I":
				inst = InstIType(instName, ctx=instCtx)
			case "J":
				inst = InstJType(instName, ctx=instCtx)
		if verbose:
			print(f"[{str(inst):->30}] {inst.to_bits(16)}")
			print(f"\t\t{inst.to_detailed()}")
		fp.write(inst.to_bits(base=16) + "\n")
	fp.close()


def main():
	args = argParser.parse_args(sys.argv[1:])
	srcFilePath, dstFilePath, func, verbose = check_args(args)
	match func:
		case "h2i":
			hex2inst(srcFilePath, dstFilePath)
		case "i2h":
			inst2hex(srcFilePath, dstFilePath, verbose)
		case _:
			raise Exception()


if __name__ == '__main__':
	main()
