
## Overview
Registers are a fundamental building block of digital hardware, and the IO core provides a simple way of interacting with them from the host machine. It allows you to define inputs and outputs of arbitrary width, and then write values to the outputs and read values from the inputs.

This is a very, very simple task - however it's surprisingly useful in practice. Both the [Use Cases](../use_cases) page and the repository's [examples](https://github.com/fischermoseley/manta/tree/main/examples) folder contain examples of the IO Core for your reference.

!!! warning "It's not instantaneous!"

    If you're trying to read or write values in your design with cycle-accurate timing, this will not do that for you. The time taken by Python to evaluate an expression is not constant, nor is the amount of time it takes for your OS to put bytes on the wire. If you need cycle-accurate timing, the [Logic Analyzer Core](./logic_analyzer_core.md) and it's [Playback feature](./logic_analyzer_core.md#playback) may be helpful.

## Configuration

As explained in the [getting started](../getting_started) page, the IO Core must be configured and included in the FPGA design before it can be operated. Configuration is performed differently depending on if you're using a traditional Verilog-based workflow, or if you're building an Amaranth-native design.

### Verilog-Based Workflows

The IO Core is used by adding an entry in a `cores` section of a configuration file. This is best shown by example:

```yaml
---
cores:
  my_io_core:
    type: io

    inputs:
      kermit: 3
      piggy: 1
      animal: 38
      scooter:
        width: 4
        initial_value: 13

    outputs:
      fozzy: 1
      gonzo: 3

```
Inside this configuration, the following parameters may be set:

- `name` _(required)_: The name of the IO core, which is used when working with the API.
- `type` _(required)_: This denotes that this is an IO core. All cores contain a `type` field, which must be set to `io` to be recognized as an IO core.
- `inputs` _(optional)_: This lists all inputs from from the FPGA fabric to the host machine. Signals in this list may be read by the host, but ___cannot___ be written to. This parameter is somewhat optional as an IO Core must have at least one probe, but it need not be an input.
- `outputs` _(optional)_: This lists all outputs from the host machine to the FPGA fabric. Signals in this list are usually written to by the host, but they can also be read from. Doing so returns the value last written to the register. This parameter is somewhat optional as an IO Core must have at least one probe, but it need not be an output.
    - `initial_value` _(optional)_: This sets an initial value for an output probe to take after the FPGA powers on. This is done with an `initial` statement in Manta's Verilog, and is independent of the input clock or resets elsewhere in the FPGA. This parameter is optional, and defaults to zero.
<!-- - `user_clock` _(optional)_: If set to True, an extra input port will be added to the `manta` module for an clock input to run the IO core on. This lets the IO Core handle clock domain crossing through its internal buffers. If set to False, Manta will run the IO core from its internal clock (the one provided through `manta`'s `clk` port). This parameter is optional, and defaults to False. More information is available in the [architecture](../architecture#io-core) page. -->

!!! warning "Name things carefully!"

    The names of the core and its probes are referenced in the autogenerated Verilog. This means that while the names can be arbitrary, they must be unique within your project and not contain any characters that your synthesis engine won't appreciate.

### Amaranth-Native Designs

Since Amaranth modules are Python objects, the configuration of the IO Core is given by the arguments given during initialization. See the documentation for the `IOCore` [class constructor](#manta.IOCore) below, as well as the Amaranth [examples](https://github.com/fischermoseley/manta/tree/main/examples/amaranth) in the repo.

## Operation

Regardless of the technique you used to configure your IO Core, it is operated using the [`set_probe()`](#manta.IOCore.set_probe) and [`get_probe()`](#manta.IOCore.get_probe) methods. Documentation for these methods is available below.

These methods are members of the `IOCore` class, so if you're using Manta in a Verilog-based workflow, you'll first need to obtain a `Manta` object that contains an `IOCore` member. This is done with `Manta.from_config()`, as shown in the Verilog [examples](https://github.com/fischermoseley/manta/tree/main/examples/verilog).


## Python API Documentation

::: manta.IOCore
