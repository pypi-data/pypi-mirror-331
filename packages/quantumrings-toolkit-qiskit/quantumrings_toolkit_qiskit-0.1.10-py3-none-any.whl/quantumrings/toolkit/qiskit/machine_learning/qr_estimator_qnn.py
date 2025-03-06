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
# This code is a derivative work of the qiskit provided EstimatorQNN class
# See: https://qiskit-community.github.io/qiskit-machine-learning/_modules/qiskit_machine_learning/neural_networks/estimator_qnn.html#EstimatorQNN
# https://qiskit-community.github.io/qiskit-machine-learning/stubs/qiskit_machine_learning.neural_networks.EstimatorQNN.html
#

# pylint: disable=wrong-import-position,wrong-import-order

from typing import Sequence

from qiskit_machine_learning.neural_networks import EstimatorQNN
from quantumrings.toolkit.qiskit import QrEstimatorV1

from qiskit.primitives import BaseEstimator, BaseEstimatorV2
from qiskit.transpiler.passmanager import BasePassManager
from qiskit.quantum_info.operators.base_operator import BaseOperator

from qiskit_machine_learning.gradients import (
    BaseEstimatorGradient,
    EstimatorGradientResult,
    ParamShiftEstimatorGradient,
)

from qiskit.circuit import Parameter, QuantumCircuit

class QrEstimatorQNN(EstimatorQNN):
    def __init__(
        self,
        *,
        circuit: QuantumCircuit,
        estimator: BaseEstimator | BaseEstimatorV2 | None = None,
        observables: Sequence[BaseOperator] | BaseOperator | None = None,
        input_params: Sequence[Parameter] | None = None,
        weight_params: Sequence[Parameter] | None = None,
        gradient: BaseEstimatorGradient | None = None,
        input_gradients: bool = False,
        default_precision: float = 0.015625,
        pass_manager: BasePassManager | None = None,
    ):
        qr_estimator = QrEstimatorV1()
        super().__init__(
            circuit = circuit, 
            estimator = qr_estimator, 
            observables = observables,
            input_params = input_params, 
            weight_params = weight_params, 
            gradient = gradient, 
            input_gradients = input_gradients,
            default_precision = default_precision,
            pass_manager = pass_manager,
            )
        return
        
