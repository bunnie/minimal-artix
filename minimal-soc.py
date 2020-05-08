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

from litex.soc.integration.soc_core import *
from litex.soc.cores.clock import S7MMCM
from litex.soc.interconnect.csr import *
from litex.soc.integration.doc import AutoDoc
import litex.soc.doc as lxsocdoc

_io = [
    ("clk12", 0, Pins("J19"), IOStandard("LVCMOS33")),
    ("led", 0, Pins("J20"), IOStandard("LVCMOS33")),
]

class Platform(XilinxPlatform):
    def __init__(self, toolchain="vivado", programmer="vivado", part="35"):
        part = "xc7a" + part + "t-fgg484-2"
        XilinxPlatform.__init__(self, part, _io, toolchain=toolchain)

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)

class Gpio(Module, AutoCSR, AutoDoc):
    def __init__(self, ledpad):
        self.led = CSRStorage(fields=[
            CSRField("ledstate", size=1, description="writing `1` lights an LED", reset=1),
            CSRField("ledpulse", size=1, description="Writing `1` sends a single clock pulse to the LED", pulse=1)
        ])
        self.comb += ledpad.eq(self.led.fields.ledstate | self.led.fields.ledpulse)

class Blink(SoCCore):
    def __init__(self, platform, **kwargs):
        sys_clk_freq=100e6
        SoCCore.__init__(self, platform, sys_clk_freq, csr_data_width=32,
            integrated_rom_size  = 0x8000,
            ident                = "LiteX Base SoC soft blink",
            cpu_type             = "vexriscv",
            with_uart            = False,
            **kwargs)

        clk12_bufg = Signal()
        self.specials += Instance("BUFG", i_I=platform.request("clk12"), o_O=clk12_bufg)

        self.submodules.mmcm = mmcm = S7MMCM(speedgrade=-1)
        mmcm.register_clkin(clk12_bufg, 12e6)
        self.clock_domains.cd_sys = ClockDomain()
        mmcm.create_clkout(self.cd_sys, sys_clk_freq)

        self.submodules.led_example = Gpio(platform.request("led"))
        self.add_csr("led_example")

def main():
    platform = Platform()
    soc = Blink(platform)
    builder = Builder(soc, output_dir="build", compile_software=False)
    vns = builder.build()
    soc.do_exit(vns)
    lxsocdoc.generate_docs(soc, "build/documentation", note_pulses=True)

if __name__ == "__main__":
    main()
