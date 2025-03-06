# This code is part of Quantum Rings toolkit for qiskit-machine-learning.
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
# This code is a derivative work of the qiskit provided FidelityQuantumKernel class
# See: https://qiskit-community.github.io/qiskit-machine-learning/stubs/qiskit_machine_learning.kernels.FidelityQuantumKernel.html#qiskit_machine_learning.kernels.FidelityQuantumKernel
# https://qiskit-community.github.io/qiskit-machine-learning/_modules/qiskit_machine_learning/kernels/fidelity_quantum_kernel.html#FidelityQuantumKernel
#

# pylint: disable=wrong-import-position,wrong-import-order

from __future__ import annotations

from collections.abc import Sequence
from typing import List, Tuple

import numpy as np
from qiskit import QuantumCircuit

from qiskit_machine_learning.state_fidelities import BaseStateFidelity, ComputeUncompute

from qiskit_machine_learning.kernels.base_kernel import BaseKernel

KernelIndices = List[Tuple[int, int]]

from qiskit_machine_learning.kernels import FidelityQuantumKernel

from quantumrings.toolkit.qiskit import QrSamplerV1 as Sampler

class QrFidelityQuantumKernel(FidelityQuantumKernel):
     def __init__(
        self,
        *,
        feature_map: QuantumCircuit | None = None,
        fidelity: BaseStateFidelity | None = None,
        enforce_psd: bool = True,
        evaluate_duplicates: str = "off_diagonal",
        max_circuits_per_job: int = None,
        ) -> None:

        fidelity = ComputeUncompute(sampler=Sampler())
        
        super().__init__(
            feature_map = feature_map,
            fidelity   = fidelity,
            enforce_psd = enforce_psd,
            evaluate_duplicates = evaluate_duplicates,
            max_circuits_per_job = max_circuits_per_job,   
        )