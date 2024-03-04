from amaranth import *
from amaranth_boards.nexys4ddr import Nexys4DDRPlatform
from amaranth_boards.icestick import ICEStickPlatform
from manta import Manta
from manta.utils import *
import pytest


class LogicAnalyzerCounterTest(wiring.Component):
    def __init__(self, platform, port):
        self.platform = platform
        self.port = port

        self.config = self.platform_specific_config()
        self.manta = Manta(self.config)

    def platform_specific_config(self):
        return {
            "cores": {
                "la": {
                    "type": "logic_analyzer",
                    "sample_depth": 1024,
                    "trigger_mode": "immediate",
                    "probes": {"larry": 1, "curly": 3, "moe": 9},
                },
            },
            "uart": {
                "port": self.port,
                "baudrate": 3e6,
                "clock_freq": self.platform.default_clk_frequency,
            },
        }

    def elaborate(self, platform):
        m = Module()
        m.submodules.manta = self.manta
        uart_pins = platform.request("uart")

        larry = self.manta.la._probes[0]
        curly = self.manta.la._probes[1]
        moe = self.manta.la._probes[2]

        m.d.sync += larry.eq(larry + 1)
        m.d.sync += curly.eq(curly + 1)
        m.d.sync += moe.eq(moe + 1)

        m.d.comb += [
            self.manta.interface.rx.eq(uart_pins.rx.i),
            uart_pins.tx.o.eq(self.manta.interface.tx),
        ]

        return m

    def build_and_program(self):
        self.platform.build(self, do_program=True)

    def verify(self):
        self.build_and_program()
        cap = self.manta.la.capture()

        # check that VCD export works
        cap.export_vcd("out.vcd")

        # check that CSV export works
        cap.export_csv("out.csv")

        # check that Verilog export works
        cap.export_playback_verilog("out.v")

        # verify that each signal is just a counter modulo the width of the signal
        for name, width in self.manta.la._config["probes"].items():
            trace = cap.get_trace(name)

            for i in range(len(trace) - 1):
                if trace[i + 1] != (trace[i] + 1) % (2**width):
                    raise ValueError("Bad counter!")


@pytest.mark.skipif(not xilinx_tools_installed(), reason="no toolchain installed")
def test_logic_analyzer_core_xilinx():
    port = "/dev/serial/by-id/usb-Digilent_Digilent_USB_Device_210292696307-if01-port0"
    LogicAnalyzerCounterTest(Nexys4DDRPlatform(), port).verify()


@pytest.mark.skipif(not ice40_tools_installed(), reason="no toolchain installed")
def test_logic_analyzer_core_ice40():
    port = "/dev/serial/by-id/usb-Lattice_Lattice_FTUSB_Interface_Cable-if01-port0"
    LogicAnalyzerCounterTest(ICEStickPlatform(), port).verify()
