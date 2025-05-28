import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.clock import Clock
from cocotb.log import SimLog
from cocotb_coverage.coverage import coverage_db, CoverPoint, CoverCross
import random


@CoverPoint("top.a", xf=lambda a, b: a, bins=[0, 1])
@CoverPoint("top.b", xf=lambda a, b: b, bins=[0, 1])
@CoverCross("top.cross.ab", items=["top.a", "top.b"])
def sample_fnc(a, b):
    pass


@cocotb.test()
async def dut_test(dut):
    log = SimLog("cocotb.test")
    cocotb.start_soon(Clock(dut.CLK, 2, units="ns").start())

    dut.RST_N.value = 0
    dut.write_en.value = 0
    dut.read_en.value = 0
    await ClockCycles(dut.CLK, 5)
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)
    log.info("Reset completed")

    test_vectors = [(0, 0), (0, 1), (1, 0), (1, 1)]

    for a, b in test_vectors:
        while dut.write_rdy.value != 1:
            await RisingEdge(dut.CLK)
        dut.write_address.value = 4
        dut.write_data.value = a
        dut.write_en.value = 1
        await RisingEdge(dut.CLK)
        dut.write_en.value = 0

        while dut.write_rdy.value != 1:
            await RisingEdge(dut.CLK)
        dut.write_address.value = 5
        dut.write_data.value = b
        dut.write_en.value = 1
        await RisingEdge(dut.CLK)
        dut.write_en.value = 0

        while dut.read_rdy.value != 1:
            await RisingEdge(dut.CLK)
        dut.read_address.value = 3
        dut.read_en.value = 1
        await RisingEdge(dut.CLK)
        dut.read_en.value = 0
        await RisingEdge(dut.CLK)
        y = dut.read_data.value.integer

        log.info(f"a={a}, b={b}, y={y}")
        sample_fnc(a, b)

    coverage_db.report_coverage(log.info, bins=True)
    log.info(f"AB Coverage: {coverage_db['top.cross.ab'].cover_percentage:.2f}%")
