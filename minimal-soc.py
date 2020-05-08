#!/usr/bin/env python3
# This variable defines all the external programs that this module
# relies on.  lxbuildenv reads this variable in order to ensure
# the build will finish without exiting due to missing third-party
# programs.
LX_DEPENDENCIES = ["riscv", "vivado"]

# Import lxbuildenv to integrate the deps/ directory
import lxbuildenv

# Disable pylint's E1101, which breaks completely on migen
#pylint:disable=E1101

from migen import *
from litex.build.xilinx import VivadoProgrammer, XilinxPlatform
from litex.build.generic_platform import Pins, IOStandard
from litex.soc.integration.builder import Builder
from migen.genlib.cdc import MultiReg

_io = [
    ("clk100", 0, Pins("J19"), IOStandard("LVCMOS33")),
    ("led", 0, Pins("J20"), IOStandard("LVCMOS33")),
    ("clkslow", 0, Pins("L19"), IOStandard("LVCMOS33")),
    ("button", 0, Pins("F18"), IOStandard("LVCMOS33")),
]

class Platform(XilinxPlatform):
    def __init__(self, toolchain="vivado", programmer="vivado", part="35"):
        part = "xc7a" + part + "t-fgg484-2"
        XilinxPlatform.__init__(self, part, _io, toolchain=toolchain)

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)

class Blink(Module):
    def __init__(self, platform, **kwargs):
        self.platform = platform
        self.sys_clk_freq = 100e6
        self.cpu_type = None
        self.mem_regions = {}
        self.constants = {}
        self.csr_regions = {}

        self.clock_domains.cd_sys   = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk100"))
        self.clock_domains.cd_slow  = ClockDomain()
        self.comb += self.cd_slow.clk.eq(platform.request("clkslow"))

        example = ClockDomainsRenamer({"sys":"slow"})(FSM(reset_state="IDLE"))
        self.submodules += example

        button = Signal()
        self.specials += MultiReg(platform.request("button"), button, odomain="slow")
        buttonpress = Signal()
        counter = Signal(max=400, reset=400)
        example.act("IDLE",
            NextValue(buttonpress, 0),
            If(button,
                NextState("DEBOUNCE"),
                NextValue(counter, 400),
            ),
        )
        example.act("DEBOUNCE",
            NextValue(counter, counter - 1),
            If(counter == 0,
                NextValue(buttonpress, 1),
                NextState("IDLE"),
            ),
            If(~button,
                NextState("IDLE"),
            )
        )

        self.sync += [
            platform.request("led").eq(buttonpress)
        ]

    def build(self, *args, **kwargs):
        return self.platform.build(self, *args, **kwargs)

def main():
    platform = Platform()
    soc = Blink(platform)
    builder = Builder(soc, output_dir="build", compile_software=False)
    vns = builder.build()
    soc.do_exit(vns)

if __name__ == "__main__":
    main()
