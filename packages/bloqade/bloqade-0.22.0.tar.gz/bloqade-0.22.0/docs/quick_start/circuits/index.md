!!! warning
    This page is under construction. The content may be incomplete or incorrect. Submit an issue
    on [GitHub](https://github.com/QuEraComputing/bloqade/issues/new) if you need help or want to
    contribute.

# Digital Quantum Computing

This section provides the quick start guide for programming digital quantum circuits using Bloqade.


## Open Quantum Assembly Language (QASM2)

Bloqade provides a set of dialects for QASM2 and our custom extensions to model parallel gates in neutral atom architectures. The QASM2 dialect is a simple quantum assembly language that allows you to write quantum circuits in a human-readable format. However, one should note that QASM2 is a very restricted language and does not support all the features of a high-level language.

For example, there is a separation of **gate routines** declared with `gate` and main program written as a sequence of gate applications. While the gate routine is similar to a function in many ways, it does not support high-level features such as recursions (due to lack of `if` statement support inside) or control flows.

While in our initial release, we support QASM2 as the first eDSL, we plan to use it as a compile target instead of a programming language for long-term development. We are working on a more expressive language that will be more suitable for quantum programming at error-corrected era.


!!! warning
    This page is under construction. The content may be incomplete or incorrect. Submit an issue
    on [GitHub](https://github.com/QuEraComputing/bloqade/issues/new) if you need help or want to
    contribute.

# QASM2 and its extensions

Bloqade provides a set of [dialects (missing link)]() for QASM2 and our custom extensions to model parallel gates in neutral atom architectures. The basic QASM2 functionality can be enabled via

```bash
pip install bloqade[qasm2]
```

## Quick Example

When programming with QASM2, the most common usage is via the `qasm2.extended` decorator, e.g the following Quantum Fourier Transform (QFT) circuit:

```python
import math
from bloqade import qasm2

@qasm2.extended
def qft(qreg: qasm2.QReg, n: int):
    if n == 0:
        return qreg

    qasm2.h(qreg[0])
    for i in range(1, n):
        qasm2.cu1(qreg[i], qreg[0], 2 * math.pi / 2**i)
    qft(qreg, n - 1)
    return qreg
```

While the syntax is similar to Python, the `qasm2.extended` decorator actually compiles the `qft` function
into lower-level intermediate representation (IR) code that can be later executed on a simulator (available via PyQrack) or a quantum computer.

You can inspect the initial IR code by calling the pretty printer:

```python
qft.print()
```

![QFT IR](qft-pprint.png)

## Running simulations

The program can be executed via a simulator backend, e.g. PyQrack, you can install it via

```bash
pip install bloqade[pyqrack]
# or if you want to use the CPU only version
pip install bloqade[pyqrack-cpu]
```

```python
@qasm2.extended
def main():
    return qft(qasm2.qreg(3), 3)

device = PyQrack()
qreg = device.run(main)
print(qreg)
```

## Emitting QASM2 code

You can also emit QASM2 code from the IR code:

```python
from bloqade.qasm2.emit import QASM2 # the QASM2 target
from bloqade.qasm2.parse import pprint # the QASM2 pretty printer

target = QASM2()
ast = target.emit(main)
pprint(ast)
```

![QFT QASM2](qft-qasm2.png)

## Understanding the compilation process

The compilation process is divided into several stages:

1. **Lowering**: the decorator `qasm2.extended` takes Python Abstract Syntax Tree (AST) and lowers it into Kirin IR in the Static Single Assignment (SSA) form.
2. **Interpretation**: when invoking the PyQrack backend, the IR code is interpreted via Kirin's IR interpreter (missing link) with the PyQrack runtime backend.
3. **Target code generation**: when emitting QASM2 code:
   1. The IR code gets aggressively inlined and all constant expressions are evaluated.
   2. All loops and control flow are unrolled.
   3. All compatible Python expressions (e.g `sin`, arithmetics) are translated into QASM2 expression.
   4. The QASM2 code is emitted as QASM2 AST for pretty printing.

In fact, the decorator `qasm2.extended` is a group of smaller dialects:

```python
extended = structural_no_opt.union(
     [
         inline,
         uop,
         glob,
         noise,
         parallel,
         core,
     ]
 )
```

where `structural_no_opt` is the base dialect group that provides the basic control flow, common Python expressions (but not all), then:

- `core` provides the core QASM2 operations such as register allocation, measurement and reset.
- `uop` provides the unary operations, such as standard Pauli gates, rotation gates, etc.

The following dialects are specific to neutral atom quantum computing as an extension:

- `glob` provides the global gates (Rydberg specific)
- `noise` provides the noise channels
- `parallel` provides the parallel gate support (Rydberg specific).
- `inline` dialect provides the inline QASM string

## Strict QASM2 mode

While the `qasm2.extended` decorator provides a lot of high-level features as an extension of QASM2, you may want to program in strict QASM2 mode for compatibility reasons. You can do this by using the `qasm2.main` and `qasm2.gate` decorators:

```python
@qasm2.main
def main():
    qasm2.h(0)
    qasm2.cx(0, 1)
    qasm2.measure(0)
    qasm2.measure(1)
    return qasm2.qreg(2)
```

which corresponding to the following QASM2 code:

```qasm
OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
creg c[2];

h q[0];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
```

Note that the `return` values are all ignored due to lack of equivalent in QASM2.
