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
# This code is a derivative work of the qiskit provided Sampler V1 class
# See: https://github.com/Qiskit/qiskit/blob/stable/1.3/qiskit/primitives/sampler.py#L39-L162
# https://docs.quantum.ibm.com/api/qiskit/qiskit.primitives.Sampler
#


# pylint: disable=wrong-import-position,wrong-import-order

from typing import List, Union, Iterable, Tuple
from collections.abc import Iterable, Sequence

from qiskit import QuantumCircuit
from qiskit.circuit import Instruction
from qiskit.providers import Options, JobV1, JobStatus
from qiskit.providers.backend import BackendV2
from qiskit.primitives import BackendSampler
from qiskit.result import Result
from qiskit.primitives.containers import SamplerPubLike,  SamplerPubResult
from qiskit.primitives.containers.sampler_pub import SamplerPub
from qiskit.result import QuasiDistribution
from qiskit.transpiler.passmanager import PassManager

import QuantumRingsLib

from qiskit.primitives import DataBin
from qiskit.primitives import PubResult
from qiskit.primitives import PrimitiveResult, SamplerResult
from qiskit.primitives import PrimitiveJob


from quantumrings.toolkit.qiskit import meas
from quantumrings.toolkit.qiskit import QrTranslator
from quantumrings.toolkit.qiskit import QrBackendV2


import numpy
        
class QrSamplerV1(BackendSampler):
    """
    Creates a QrSamplerV1 object that calculates quasi-probabilities of bitstrings from quantum circuits.
    Derives from the qiskit SamplerV1 class.

    When the quantum circuit is executed using the method :meth:`quantumrings.toolkit.qiskit.QrSamplerV1.run()`, this class returns a
    :class:`quantumrings.toolkit.qiskit.QrJobV1` object. 
   
    This method is called with the following parameters

    * quantum circuits (:math:`\psi_i(\theta)`): list of (parameterized) quantum circuits.
      (a list of :class:`~qiskit.circuit.QuantumCircuit` objects)

    * parameter values (:math:`\theta_k`): list of sets of parameter values
      to be bound to the parameters of the quantum circuits.
      (list of list of float)

    Calling the method :meth:`quantumrings.toolkit.qiskit.QrJobV1.result()` yields a :class:`~qiskit.primitives.SamplerResult`
    object, which contains probabilities or quasi-probabilities of bitstrings.

    Example:
    
    .. code-block:: python

        from  quantumrings.toolkit.qiskit import QrSamplerV1 as Sampler
        from qiskit import QuantumCircuit
        from qiskit.circuit.library import RealAmplitudes

        # a Bell circuit
        bell = QuantumCircuit(2)
        bell.h(0)
        bell.cx(0, 1)
        bell.measure_all()

        # two parameterized circuits
        pqc = RealAmplitudes(num_qubits=2, reps=2)
        pqc.measure_all()
        pqc2 = RealAmplitudes(num_qubits=2, reps=3)
        pqc2.measure_all()

        theta1 = [0, 1, 1, 2, 3, 5]
        theta2 = [0, 1, 2, 3, 4, 5, 6, 7]

        # initialization of the sampler
        sampler = Sampler()

        # Sampler runs a job on the Bell circuit
        job = sampler.run(circuits=[bell], parameter_values=[[]], parameters=[[]])
        job_result = job.result()
        print([q.binary_probabilities() for q in job_result.quasi_dists])

        # Sampler runs a job on the parameterized circuits
        job2 = sampler.run(
            circuits=[pqc, pqc2],
            parameter_values=[theta1, theta2],
            parameters=[pqc.parameters, pqc2.parameters])
        job_result = job2.result()
        print([q.binary_probabilities() for q in job_result.quasi_dists])

    """
    def __init__(self, 
        backend: QrBackendV2 = None,
        options: dict | None = None,
        run_options: dict | None = None,
        bound_pass_manager: PassManager | None = None,
        skip_transpilation: bool = False,
        ):
        """
        Args:
            backend: The QrBackendV2 backend.
            options: The options to control the default shots(``shots``)
            run_options: See options above.
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
        
        shots_ = 1024
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
          




        # Dynamical decoupling options
        self._default_options.dynamical_decoupling = Options()
        self._default_options.dynamical_decoupling.enable = False
        self._default_options.dynamical_decoupling.sequence_type = "XY4"
        
        # Twirling options
        self._default_options.twirling = Options()
        self._default_options.twirling.enable_gates = False
        self._default_options.twirling.num_randomizations = 1
        
        self._default_options.shots = shots_
        self._default_options.mode = mode_
        self._default_options.performance = performance_
        self._default_options.quiet = True
        self._default_options.defaults = True
        self._default_options.generate_amplitude = False

        super().__init__(backend = backend)

    @property
    def options(self) -> Options:
        """Return the options"""
        return self._default_options
        
       
    def job_call_back(self, job_id, state, job) -> None:
        pass

    def run_sampler(self, circuits, **run_options):
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


        max_qubits = 0
        for j in range (len(circuits.qregs)):
            max_qubits += circuits.qregs[0].size

        if ( max_qubits <= 0 ):
            raise Exception( "Submitted quantum circuit does not use any qubits")
            return
        
        max_clbits = 0
        for j in range (len(circuits.cregs)):
            max_clbits += circuits.cregs[0].size

        self._max_qubits = circuits.num_qubits #max_qubits
        self._max_clbits = circuits.num_clbits #max_clbits
        
                  
        # if we get here, the measurement instructions, if any, are at the end of the circuit
        # create the quantum circuit now
        
        #TODO: Check control loops
        qreg = QuantumRingsLib.QuantumRegister(self._max_qubits, "q")
        creg = QuantumRingsLib.ClassicalRegister(self._max_clbits, "meas")
        qc   = QuantumRingsLib.QuantumCircuit(qreg, creg, name = circuits.name,  global_phase = circuits.global_phase)

        self._is_final_layout = False

        if (True == hasattr(circuits, "_layout")):
            layout = circuits._layout
            if ( True == hasattr(layout, "final_layout")): 
                self._is_final_layout = True


        # export the measurements to QuantumRings Structure
        QrTranslator.translate_quantum_circuit(circuits, 
                                               qc,
                                               False,
                                               ) 

        
        job = self._qr_backend.run(qc, shots = self._shots, mode = self._mode, performance = self._performance, quiet = True)
        job.wait_for_final_state(0.0, 5.0, self.job_call_back)
        results = job.result()
        counts = results.get_counts()
        self._job_id = job.job_id
        
        return counts
                
       
    def _run(self,
        circuits: tuple[QuantumCircuit, ...],
        parameter_values: tuple[tuple[float, ...], ...],
        **run_options,):
        results = []
        metadata = []

        index = 0

        for circuit in circuits:

            #
            # Check if it is a parametrized circuit. If so, assign parameters
            #

            if (circuit.num_parameters):
                if (parameter_values is not None):
                    if (len(parameter_values) != len(circuits)):
                        raise Exception ("Invalid number of parameter_values object passed. Must be equal to the number of circuits submitted")
                    else:
                        run_input = circuit.assign_parameters(parameter_values[index])
                else:
                    raise Exception ("None object is passed for parameter_values, whereas circuit is parametrized")
            else:
                run_input = circuit
            

            if "shots" in run_options:
                shots = run_options["shots"]
            else:
                shots = self._default_options.shots
 
            counts_org = self.run_sampler(run_input, shots = shots)

            counts = {}
            cbits_to_retain = 0

            for j in range (len(circuit.cregs)):
                cbits_to_retain += circuit.cregs[j].size

            for key, value in counts_org.items():
                counts[key[-cbits_to_retain:]]=value

            quasi_dist = QuasiDistribution({outcome: freq / shots for outcome, freq in counts.items()})
            index += 1
    
            results.append(quasi_dist)
            metadata.append({"shots": shots})
        
        return SamplerResult(results, metadata=metadata )

    def run(
        self,
        circuits: QuantumCircuit | Sequence[QuantumCircuit],
        parameter_values: Sequence[float] | Sequence[Sequence[float]] | None = None,
        **run_options,
        ):
        """
        Run the sampling job.

        Args:
            circuits: One of more circuit objects.
            parameter_values: Parameters to be bound to the circuit.
            run_options: Backend runtime options used for circuit execution.

        Returns:
            The job object of the result of the sampler. The i-th result corresponds to
            ``circuits[i]`` evaluated with parameters bound as ``parameter_values[i]``.

        Raises:
            ValueError: Invalid arguments are given.
        """
        run_input = []     
        if(isinstance(circuits, QuantumCircuit)):
            run_input.append(circuits)
        else:
            run_input = circuits
        my_sampler_job = PrimitiveJob(self._run, run_input, parameter_values, **run_options)
        my_sampler_job._submit()
        return  my_sampler_job
    