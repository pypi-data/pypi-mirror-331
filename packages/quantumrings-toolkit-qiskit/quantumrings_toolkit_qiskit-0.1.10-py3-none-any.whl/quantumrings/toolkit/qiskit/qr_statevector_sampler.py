# This code is part of Quantum Rings toolkit for qiskit.
#
# (C) Copyright IBM 2022, 2024.
# (C) Copyright Quantum Rings Inc, 2024.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

#
# This code is a derivative work of the qiskit provided StatevectorSampler class
# See: https://github.com/Qiskit/qiskit/blob/stable/1.3/qiskit/primitives/statevector_sampler.py#L52-L203
# https://docs.quantum.ibm.com/api/qiskit/qiskit.primitives.StatevectorSampler
#


# pylint: disable=wrong-import-position,wrong-import-order

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Iterable

import numpy as np
from numpy.typing import NDArray

from qiskit import ClassicalRegister, QiskitError, QuantumCircuit
from qiskit.circuit import ControlFlowOp
from qiskit.quantum_info import Statevector
from quantumrings.toolkit.qiskit import QrStatevector# as Statevector

from qiskit.primitives.base import BaseSamplerV2
from qiskit.primitives.base.validation import _has_measure
from qiskit.primitives.containers import (
    BitArray,
    DataBin,
    PrimitiveResult,
    SamplerPubResult,
    SamplerPubLike,
)
from qiskit.primitives.containers.sampler_pub import SamplerPub
from qiskit.primitives.containers.bit_array import _min_num_bytes
from qiskit.primitives.primitive_job import PrimitiveJob
from qiskit.primitives.utils import bound_circuit_to_instruction
from qiskit.primitives import StatevectorSampler
from qiskit.primitives.statevector_sampler import _preprocess_circuit


@dataclass
class _MeasureInfo:
    creg_name: str
    num_bits: int
    num_bytes: int
    qreg_indices: list[int]


class QrStatevectorSampler(StatevectorSampler):
    def __init__(self, *, default_shots: int = 1024, seed: np.random.Generator | int | None = None):
        """
        Args:
            default_shots: The default shots for the sampler if not specified during run.
            seed: The seed or Generator object for random number generation.
                If None, a random seeded default RNG will be used.
        """
        
        
        super().__init__(
            default_shots = default_shots, 
            seed = seed, 
            )
        return

    def _run_pub(self, pub: SamplerPub) -> SamplerPubResult:
        circuit, qargs, meas_info = _preprocess_circuit(pub.circuit)
        bound_circuits = pub.parameter_values.bind_all(circuit)
        arrays = {
            item.creg_name: np.zeros(
                bound_circuits.shape + (pub.shots, item.num_bytes), dtype=np.uint8
            )
            for item in meas_info
        }
        for index, bound_circuit in np.ndenumerate(bound_circuits):
            final_state = QrStatevector(bound_circuit_to_instruction(bound_circuit))
            if qargs:
                samples = final_state.sample_memory(shots=pub.shots, qargs=qargs)
            else:
                samples = [""] * pub.shots
            samples_array = np.array([np.fromiter(sample, dtype=np.uint8) for sample in samples])
            for item in meas_info:
                ary = self._samples_to_packed_array(samples_array, item.num_bits, item.qreg_indices)
                arrays[item.creg_name][index] = ary

        meas = {
            item.creg_name: BitArray(arrays[item.creg_name], item.num_bits) for item in meas_info
        }

        return SamplerPubResult(
            DataBin(**meas, shape=pub.shape),
            metadata={"shots": pub.shots, "circuit_metadata": pub.circuit.metadata},
        )

    def _samples_to_packed_array(
        self,
        samples: NDArray[np.uint8], num_bits: int, indices: list[int]
    ) -> NDArray[np.uint8]:
        # samples of `Statevector.sample_memory` will be in the order of
        # qubit_last, ..., qubit_1, qubit_0.
        # reverse the sample order into qubit_0, qubit_1, ..., qubit_last and
        # pad 0 in the rightmost to be used for the sentinel introduced by _preprocess_circuit.
        ary = np.pad(samples[:, ::-1], ((0, 0), (0, 1)), constant_values=0)
        # place samples in the order of clbit_last, ..., clbit_1, clbit_0
        ary = ary[:, indices[::-1]]
        # pad 0 in the left to align the number to be mod 8
        # since np.packbits(bitorder='big') pads 0 to the right.
        pad_size = -num_bits % 8
        ary = np.pad(ary, ((0, 0), (pad_size, 0)), constant_values=0)
        # pack bits in big endian order
        ary = np.packbits(ary, axis=-1)
        return ary