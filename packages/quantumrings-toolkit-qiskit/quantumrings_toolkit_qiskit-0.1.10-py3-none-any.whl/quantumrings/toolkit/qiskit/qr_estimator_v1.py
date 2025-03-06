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
# This code is a derivative work of the qiskit provided EstimatorV1 class
# See: https://github.com/Qiskit/qiskit/blob/stable/1.3/qiskit/primitives/estimator.py#L38-L172
# https://docs.quantum.ibm.com/api/qiskit/qiskit.primitives.Estimator
#

# pylint: disable=wrong-import-position,wrong-import-order

from typing import List, Union, Tuple
from collections.abc import Iterable, Sequence

from qiskit.circuit import QuantumCircuit, Instruction
from qiskit.providers import Options, JobV1, JobStatus
from qiskit.providers.backend import BackendV2

from qiskit.primitives import BackendEstimator
from qiskit.result import Result
from qiskit.primitives.containers.estimator_pub import EstimatorPub
from qiskit.primitives.containers import EstimatorPubLike

from qiskit.primitives import DataBin
from qiskit.primitives import PubResult
from qiskit.primitives import PrimitiveResult, EstimatorResult
from qiskit.primitives import PrimitiveJob

from qiskit.quantum_info import Pauli
from qiskit.quantum_info.operators.symplectic.sparse_pauli_op import SparsePauliOp as SparsePauliOp
from qiskit.quantum_info.operators.base_operator import BaseOperator

import QuantumRingsLib

from quantumrings.toolkit.qiskit import QrTranslator
from quantumrings.toolkit.qiskit import QrBackendV2

from dataclasses import dataclass
import numpy

import threading
import time

class QrEstimatorV1(BackendEstimator):
    """
    A derivative of the BackendEstimatorV1 class, to estimates expectation values of quantum circuits and observables using the Quantum Rings backend.

    An estimator is initialized with an empty parameter set. The estimator is used to
    create a :class:`~qiskit.providers.JobV1`, via the
    :meth:`qiskit.primitives.Estimator.run()` method. This method is called
    with the following parameters

    * quantum circuits (:math:`\psi_i(\theta)`): list of (parameterized) quantum circuits
      (a list of :class:`~qiskit.circuit.QuantumCircuit` objects).

    * observables (:math:`H_j`): a list of :class:`~qiskit.quantum_info.SparsePauliOp`
      objects.

    * parameter values (:math:`\theta_k`): list of sets of values
      to be bound to the parameters of the quantum circuits
      (list of list of float).

    The method returns a :class:`~qiskit.providers.JobV1` object, calling
    :meth:`qiskit.providers.JobV1.result()` yields the
    a list of expectation values plus optional metadata like confidence intervals for
    the estimation.

    """
    def __init__(
        self,
        *,
        backend: QrBackendV2 = None,
        options: dict | None = None,
        run_options: dict | None = None
        ):
        """
        Args:
            | backend: The Quantum Rings backend to run the primitive on.
            | options: The options to control the defaults
            | run_options: See options.
        """
        if (backend is None):
            qr_provider = QuantumRingsLib.QuantumRingsProvider()
            backend = QrBackendV2(qr_provider)
            if (backend._qr_backend.num_qubits == 0):
                raise Exception("Either provide a valid QrBackendV2 object as a parameter or save your account credentials using QuantumRingsLib.QuantumRingsProvider.save_account method")
                return
        elif (False == isinstance(backend, QrBackendV2)):
            raise Exception ("The backend for this class should be a Quantum Rings Backend.")
            return
        self._qr_backend = backend._qr_backend
        self._num_circuits = 1
        self._default_options = Options()

        self.lock = threading.Lock()
        
        # Dynamical decoupling options
        self._default_options.dynamical_decoupling = Options()
        self._default_options.dynamical_decoupling.enable = False
        self._default_options.dynamical_decoupling.sequence_type = "XY4"
        
        # Twirling options
        self._default_options.twirling = Options()
        self._default_options.twirling.enable_gates = False
        self._default_options.twirling.num_randomizations = 1
        
        shots_ = 1
        mode_ = "sync"
        performance_ = "HIGHESTACCURACY"

        #
        # Check for configuration parameters through the options dictionary
        #

        if ( options is not None):
            if ("shots" in options ):
                if isinstance( options["shots"], (int, numpy.int64)):
                    shots_ = options["shots"]
                else:
                    raise Exception( "Invalid argument for shots")
                    return
                
            if ("mode" in options ):
                if isinstance( options["mode"], str):
                    if (options["mode"] not in ["sync", "async"]):
                        raise Exception( "Invalid argument for mode")
                        return
                    else:
                        mode_ = options["mode"]
                else:
                    raise Exception( "Invalid argument for mode")
                    return
                
            if ("performance" in options ):
                if isinstance( options["performance"], str):
                    if (options["performance"] not in ["HIGHESTEFFICIENCY", "BALANCEDACCURACY", "HIGHESTACCURACY", "AUTOMATIC"]):
                        raise Exception( "Invalid argument for performance")
                        return
                    else:
                        performance_ = options["performance"]
                else:
                    raise Exception( "Invalid argument for performance")
                    return

        #
        # Check for configuration parameters through the run_options dictionary
        #
                    
        if ( run_options is not None):
            if ("shots" in run_options ):
                if isinstance( run_options["shots"], (int, numpy.int64)):
                    shots_ = run_options["shots"]
                else:
                    raise Exception( "Invalid argument for shots")
                    return
                
            if ("mode" in run_options ):
                if isinstance( run_options["mode"], str):
                    if (run_options["mode"] not in ["sync", "async"]):
                        raise Exception( "Invalid argument for mode")
                        return
                    else:
                        mode_ = run_options["mode"]
                else:
                    raise Exception( "Invalid argument for mode")
                    return
                
            if ("performance" in run_options ):
                if isinstance( run_options["performance"], str):
                    if (run_options["performance"] not in ["HIGHESTEFFICIENCY", "BALANCEDACCURACY", "HIGHESTACCURACY", "AUTOMATIC"]):
                        raise Exception( "Invalid argument for performance")
                        return
                    else:
                        performance_ = run_options["performance"]
                else:
                    raise Exception( "Invalid argument for performance")
                    return

        self._default_options.shots = shots_
        self._default_options.mode = mode_
        self._default_options.performance = performance_
        self._default_options.quiet = True
        self._default_options.defaults = True
        self._default_options.generate_amplitude = False

        super().__init__(backend = backend)
     
    @property
    def options(self) -> Options:
        """Returns the options"""
        return self._default_options
        
    def job_call_back(self, job_id, state, job) -> None:
        pass

    def run_estimator(self, circuits, observables,  params, **run_options):
        results = []
        
        with self.lock:
            # Validate the circuits parameter.
            if not isinstance(circuits, QuantumCircuit):
                raise Exception( "Invalid argument passed for Quantum Circuit.")
                return

            # Fetch run time options
            if "shots" in run_options:
                self._shots = run_options.get("shots")
                if not isinstance(self._shots, (int, numpy.int64)):
                    raise Exception( "Invalid argument for shots")
                    return
                if ( self._shots <= 0 ):
                    raise Exception( "Invalid argument for shots")
                    return
            else:
                self._shots = self._default_options.shots
                
            if "mode" in run_options:
                self._mode = run_options.get("mode")
                if not isinstance(self._mode, str):
                    raise Exception( "Invalid argument for mode")
                    return
                else:
                    self._mode = self._mode.lower()
                    if (self._mode not in ["sync", "async"]):
                        raise Exception( "Invalid argument for mode")
                        return
            else:
                self._mode = self._default_options.mode

            if "performance" in run_options:
                self._performance = run_options.get("performance")
                if not isinstance(self._performance, str):
                    raise Exception( "Invalid argument for performance")
                    return
                else:
                    self._performance = self._mode.upper()
                    if (self._performance not in ["HIGHESTEFFICIENCY", "BALANCEDACCURACY", "HIGHESTACCURACY", "AUTOMATIC"]):
                        raise Exception( "Invalid argument for performance")
                        return
            else:
                self._performance = self._default_options.performance


            # Confirm we have the right number of params
            if (isinstance(params, numpy.float64)):
                if (circuits.num_parameters != 1 ):
                    raise Exception ("The given number of parameters is less than the parameters in the circuit.")
                    return
            else:
                if params is not None: 
                    if (circuits.num_parameters > len(params)):
                        raise Exception ("The given number of parameters is less than the parameters in the circuit.")
                        return

            #Assign parameters
            if (circuits.num_parameters):
                if (isinstance(params, numpy.float64)):
                    subs_params = []
                    subs_params.append(params)
                    run_input = circuits.assign_parameters(subs_params)
                else:
                    if params is not None:
                        run_input = circuits.assign_parameters(params)
                    else:
                        raise Exception ("Invalid parameters passed.")
                        return
            else:
                run_input = circuits

            self._max_qubits = run_input.num_qubits
            self._max_clbits = run_input.num_clbits
            
            if (isinstance(observables, Pauli)):
                pauli_string = observables.to_label()
                if (self._max_qubits != len(pauli_string)):
                    raise Exception( "The Pauli operator length is not matching number of qubits")
                    return
            else:
                # check whether the Pauli operator sizes match  max_qubit
                if (self._max_qubits != len(observables.paulis[0])):
                    raise Exception( "The Pauli operator length is not matching number of qubits")
                    return
            
            # Check sanity of the measurement instructions
            # There shouldn't be any other instruction after the last measurement instruction
            ins_found = False
            for instruction in reversed(run_input):
                if ( instruction.operation.name == "measure" ):
                    if ( False == ins_found ):
                        continue
                    else:
                        raise Exception( "Invalid Instruction sequence. Measurement preceeds a gate operation")
                        return
                elif ( instruction.operation.name == "barrier" ):
                    continue
                else:
                    ins_found = True 
                        
            # if we get here, the measurement instructions, if any, are at the end of the circuit
            # create the quantum circuit now
         
            qreg = QuantumRingsLib.QuantumRegister(self._max_qubits, "q")
            if ( self._max_clbits > 0):
                creg = QuantumRingsLib.ClassicalRegister(self._max_clbits, "meas")
                qc   = QuantumRingsLib.QuantumCircuit(qreg, creg, name = run_input.name,  global_phase = run_input.global_phase)
            else:
                qc   = QuantumRingsLib.QuantumCircuit(qreg, name = run_input.name,  global_phase = run_input.global_phase)

            
            self._is_final_layout = False

            if (True == hasattr(run_input, "_layout")):
                layout = run_input._layout
                if ( True == hasattr(layout, "final_layout")): 
                    self._is_final_layout = True

            # Export the qiskit QuantumCircuit to QuantumRings Structure
            QrTranslator.translate_quantum_circuit(run_input, qc, True)
            
            # We must setup the Pauli operator now.
            # for each Pauli operator
            avg = 0.0

            if (isinstance(observables, Pauli)):
                sp = SparsePauliOp([observables.to_label()],coeffs=[1])
                pauli_list = sp.to_list()
            else:
                pauli_list = observables.to_list()


            # first execute the circuit
            job = self._qr_backend.run(qc, shots = 1, mode = self._mode, performance = self._performance, quiet = True)
            job.wait_for_final_state(0, 5, self.job_call_back)
            self._job_id = job.job_id   # Store the last used job ID as the reference job id.
            results = job.result()
            qubit_list = [i for i in range(0, self._max_qubits)]

            for p in range(len(pauli_list)):
                weight = pauli_list[p][1].real
                pauli  = pauli_list[p][0]

                expectation_value = results.get_pauliexpectationvalue( pauli,qubit_list,0,0).real * weight
                            
                avg = avg + expectation_value

            return avg
        
    def _run(
        self,
        circuits: tuple[QuantumCircuit, ...],
        observables: tuple[BaseOperator, ...],
        parameter_values: tuple[tuple[float, ...], ...],
        **run_options,):

        loop_index = 0
        #results_data = []
        results_data = numpy.array([])
        metadata = []

        if "shots" in run_options:
            shots = run_options["shots"]
        else:
            shots = self._default_options.shots
            run_options["shots"] = shots

        for circuit in circuits:
            observable_ = observables[loop_index]
            if parameter_values is not None:
                param_ = parameter_values[loop_index]
            else:
                param_ = None

            results_data = numpy.append(results_data, self.run_estimator(circuit, observable_, param_, **run_options))

            loop_index += 1
            metadata.append({"shots": shots})

        return EstimatorResult(results_data, metadata=metadata )
    

    def run(
        self,
        circuits: Sequence[QuantumCircuit] | QuantumCircuit,
        observables: Sequence[BaseOperator | str] | BaseOperator | str,
        parameter_values: Sequence[Sequence[float]] | Sequence[float] | float | None = None,
        **run_options,
        ) -> PrimitiveJob[PrimitiveResult[PubResult]]:
        """
        Executes the pubs and estimates all associated observables.

        Args:
            | pubs: The pub to preprocess.
            | precision: None

        Returns:
            The job associated with the pub
        """
        circuit_list = []
        observable_list = []
        parameter_list = []

        if(isinstance(circuits, QuantumCircuit)):
            circuit_list.append(circuits)
        else:
            circuit_list = circuits

        if((isinstance(observables, str)) or (isinstance(observables, BaseOperator))):
            observable_list.append(observables)
        else:
            observable_list = observables

        if(isinstance(parameter_values, float)):
            parameter_list.append(parameter_values)
        else:
            parameter_list = parameter_values

        num_circuits_ = len(circuit_list)
        
        if (num_circuits_ != len(observable_list)):
            raise Exception (f"Insufficient number of observables. Circuits: {num_circuits_}  Observables: {len(observable_list)}")
        
        if (parameter_list is not None):
            if ( len(parameter_list) > 0):
                # there are some parameters. The list should be equal to the number of circuits
                if (num_circuits_ != len(parameter_list)):
                    raise Exception (f"Insufficient number of parameters. Circuits: {num_circuits_}  Observables: {len(parameter_list)}")

        # We have preprocessed the arguments and arranged them in right order

        my_estimator_job = PrimitiveJob(self._run, circuit_list, observable_list, parameter_list, **run_options)
        my_estimator_job._submit()
        return  my_estimator_job

