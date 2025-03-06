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
# This code is a derivative work of the qiskit provided EstimatorV2 class
# See: https://github.com/Qiskit/qiskit-ibm-runtime/blob/stable/0.34/qiskit_ibm_runtime/estimator.py
# https://docs.quantum.ibm.com/api/qiskit-ibm-runtime/qiskit_ibm_runtime.EstimatorV2#estimatorv2
#

# pylint: disable=wrong-import-position,wrong-import-order

from typing import List, Union, Iterable, Tuple

from qiskit.circuit import QuantumCircuit, Instruction
from qiskit.providers import Options, JobV1, JobStatus
from qiskit.providers.backend import BackendV2

from qiskit.primitives import BackendEstimatorV2
from qiskit.result import Result
from qiskit.primitives.containers.estimator_pub import EstimatorPub
from qiskit.primitives.containers import EstimatorPubLike

import QuantumRingsLib

from qiskit.primitives import DataBin
from qiskit.primitives import PubResult
from qiskit.primitives import PrimitiveResult
from qiskit.primitives import PrimitiveJob

from dataclasses import dataclass
from quantumrings.toolkit.qiskit import QrTranslator
from quantumrings.toolkit.qiskit import QrBackendV2

from qiskit.quantum_info.operators.symplectic.sparse_pauli_op import SparsePauliOp as SparsePauliOp
import numpy

class QrEstimatorV2(BackendEstimatorV2):
    """
    Given an observable of the type
    :math:`O=\sum_{i=1}^Na_iP_i`, where :math:`a_i` is a complex number and :math:`P_i` is a
    Pauli operator, the estimator calculates the expectation :math:`\mathbb{E}(P_i)` of each
    :math:`P_i` and finally calculates the expectation value of :math:`O` as
    :math:`\mathbb{E}(O)=\sum_{i=1}^Na_i\mathbb{E}(P_i)`. The reported ``std`` is calculated
    as

    .. math::

        \frac{\sum_{i=1}^{n}|a_i|\sqrt{\textrm{Var}\big(P_i\big)}}{\sqrt{N}}\:,

    where :math:`\textrm{Var}(P_i)` is the variance of :math:`P_i`, :math:`N=O(\epsilon^{-2})` is
    the number of shots, and :math:`\epsilon` is the target precision [1].

    Each tuple of ``(circuit, observables, <optional> parameter values, <optional> precision)``,
    called an estimator primitive unified bloc (PUB), produces its own array-based result. The
    :meth:`~.QrEstimatorV2.run` method can be given a sequence of pubs to run in one call.

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
            | options: The options to control the defaults shots (``default_shots``)
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
        elif (circuits.num_parameters > len(params)):
            raise Exception ("The given number of parameters is less than the parameters in the circuit.")
            return

        #Assign parameters
        if (circuits.num_parameters):
            if (isinstance(params, numpy.float64)):
                subs_params = []
                subs_params.append(params)
                run_input = circuits.assign_parameters(subs_params)
            else:
                run_input = circuits.assign_parameters(params)
        else:
            run_input = circuits

        self._max_qubits = run_input.num_qubits
        self._max_clbits = run_input.num_clbits
        
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

        # export the measurements to QuantumRings Structure
        QrTranslator.translate_quantum_circuit(run_input, qc, True)
        
        # We must setup the Pauli operator now.
        # for each Pauli operator
        avg = 0.0

        pauli_list = observables.to_list()
        
        # first execute the circuit
        job = self._qr_backend.run(qc, shots = 1, mode = self._mode, performance = self._performance, quiet = True)
        job.wait_for_final_state(0.0, 5.0, self.job_call_back)
        self._job_id = job.job_id   # Store the last used job ID as the reference job id.
        results = job.result()
        qubit_list = [i for i in range(0, self._max_qubits)]


        for p in range(len(pauli_list)):
            weight = pauli_list[p][1].real
            pauli  = pauli_list[p][0]
        
            expectation_value = results.get_pauliexpectationvalue( pauli,qubit_list,0,0).real * weight

            avg = avg + expectation_value

        
        return avg
        
   
    def _process_pub_two(self, circuit, observable, param_, pub_data):
        if (isinstance(param_, numpy.ndarray)):
            params = param_
            pub_data.append(self.run_estimator(circuit, observable, params))
        elif (isinstance(param_, list)):
            if len(param_) == 0:
                pub_data.append(self.run_estimator(circuit, observable, param_))
            else:
                avg_exp = []
                for params in param_:
                    avg_exp.append(self.run_estimator(circuit, observable, params))
                pub_data.append(avg_exp)
        else:
            pub_data.append(self.run_estimator(circuit, observable, param_))
      
    
    def _run(self, pubs: list[EstimatorPub]) -> PrimitiveResult[PubResult]:
      
        results = [None] * len(pubs)
        metadata = [None] * len(pubs)

        for i, pub in enumerate(pubs):
            pub_data = []
            circuit = pub[0]
            if (isinstance(pub[1], list)):
                for observable_list in pub[1]:
                    if (isinstance(observable_list, list)):
                        for observ in observable_list:
                            observable = observ
                            # check what's up with pub[2]
                            self._process_pub_two(circuit, observable, pub[2], pub_data)
                    elif (isinstance(observable_list, SparsePauliOp)):
                        self._process_pub_two(circuit, observable_list, pub[2], pub_data)
                    else:
                        raise Exception("Ill formed pub[1]")
                        return
            elif (isinstance(pub[1], SparsePauliOp)):
                # QAOA type sample
                observable = pub[1]
                self._process_pub_two(circuit, observable, pub[2], pub_data)
            else:
                raise Exception("Ill formed pub[1]")
                return
    
            pub_result = DataBin(evs = pub_data,)
            results[i] = PubResult(pub_result)
            metadata[i] = {"version": 2}
        
        return PrimitiveResult(results, metadata=metadata)

    def run(
        self, pubs: Iterable[EstimatorPubLike], *, precision: float | None = None
        ) -> PrimitiveJob[PrimitiveResult[PubResult]]:
        """
        Executes the pubs and estimates all associated observables.

        Args:
            | pubs: The pub to preprocess.
            | precision: None

        Returns:
            The job associated with the pub
        """
        my_estimator_job = PrimitiveJob(self._run, pubs)
        my_estimator_job._submit()
        return  my_estimator_job

