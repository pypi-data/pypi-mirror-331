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
# This code is a derivative work of the qiskit provided BackendV2 class
# See: https://github.com/Qiskit/qiskit/blob/stable/1.3/qiskit/providers/backend.py
# https://docs.quantum.ibm.com/api/qiskit/qiskit.providers.BackendV2
#


# pylint: disable=wrong-import-position,wrong-import-order

from qiskit.circuit import QuantumCircuit, Instruction
from qiskit.circuit.library.standard_gates import get_standard_gate_name_mapping
from qiskit.transpiler import CouplingMap, Target, InstructionProperties, QubitProperties
from qiskit.providers import Options, JobV1, JobStatus
from qiskit.providers.backend import BackendV2
from qiskit.result import Result
from qiskit.circuit.controlflow import (
    IfElseOp,
    WhileLoopOp,
    ForLoopOp,
    SwitchCaseOp,
    BreakLoopOp,
    ContinueLoopOp,
    )


import QuantumRingsLib

from quantumrings.toolkit.qiskit import QrTranslator
from quantumrings.toolkit.qiskit import QrJobV1


class QrBackendV2(BackendV2):

    """
    Supporter class for a qiskit V2 compatible backend object for Quantum Rings, meant to be used along with qiskit packages.

    """
    
    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize a BackendV2 based backend for Quantum Rings. 

        Usage:
            If the user already has obtained the reference to the QuantumRingsLib.QuantumRingsProvider object, 
            the reference can be provided using the 'provider' argument.
            Otherwise, the user can provide the account's 'name' and 'token' as parameters.
            If the user has saved the account details locally using the QuantumRingsLib.QuantumRingsProvider.save_account api,
            this method can be called without any arguments.

        Examples:
            >>> backend = QrBackendV2()        # Uses the account information that is locally stored.
            >>> backend = QrBackendV2(num_qubits = 5)        # Uses the account information that is locally stored, sets the number of qubits to 5.

            >>> provider = QuantumRingsLib.QuantumRingsProvider(token = <YOUR_TOKEN>, name = <YOUR_ACCOUNT>)
            >>> backend  = QrBackendV2(provider)

            >>> backend = QrBackendV2(token = <YOUR_TOKEN>, name = <YOUR_ACCOUNT>)

        Args:
            provider   (QuantumRingsLib.QuantumRingsProvider): An optional backwards reference to the QuantumRingsLib.QuantumRingsProvider object.
            token      (str): An optional access key to the QuantumRingsLib.QuantumRingsProvider. 
            name       (str): An optional account name to be used to autenticate the user.
            num_qubits (int): The number of qubits the backend will use.

        Raises:
            Exception: If not able to obtain the Quantum Rings Provider or the backend.

        """

        if ( isinstance(kwargs.get('token'), str ) ) and ( isinstance(kwargs.get('name'), str ) ):
            self._qr_provider = QuantumRingsLib.QuantumRingsProvider(token = kwargs.get('token'), name = kwargs.get('name'))
        elif isinstance(kwargs.get('provider'), QuantumRingsLib.QuantumRingsProvider ):
            self._qr_provider = kwargs.get('provider')
        elif (len(args) > 1 ) and ( isinstance(args[0], str ) ) and ( isinstance(args[1], str ) ):
            self._qr_provider = QuantumRingsLib.QuantumRingsProvider(token = args[0], name = args[1])
        elif (len(args) > 0 ) and ( isinstance(args[0], QuantumRingsLib.QuantumRingsProvider ) ):
            self._qr_provider = args[0]
        else:
            self._qr_provider = QuantumRingsLib.QuantumRingsProvider()

        if ( self._qr_provider is None ):
            raise Exception ("Unable to obtain Quantum Rings Provider. Please check the arguments")
            return
        
        self._qr_backend = self._qr_provider.get_backend("scarlet_quantum_rings")
        
        if ( self._qr_backend is None ):
            raise Exception ("Unable to obtain backend. Please check the arguments")
            return
            
        super().__init__(
            provider = "Quantum Rings Provider",
            name= self._qr_backend.name,
            description = self._qr_backend.description,
            online_date = self._qr_backend.online_date,
            backend_version = self._qr_backend.backend_version,
            )

        if ( isinstance(kwargs.get('num_qubits'), int ) ):
            n = kwargs.get('num_qubits')
            if ( self._qr_backend.num_qubits >= n ):
                self._num_qubits = n
                self._coupling_map = self._qr_backend.get_coupling_map(self._num_qubits)
            else:
                raise Exception( f"Requested number of qubits {n} is more than the provisioned {self._qr_backend.num_qubits}." )
                return
        else:
             self._num_qubits = self._qr_backend.num_qubits
             self._coupling_map = self._qr_backend.coupling_map

        self._dt = self._qr_backend.dt
        self._dtm = self._qr_backend.dtm
       
        self._supported_gates = get_standard_gate_name_mapping()
        self._basis_gates = self._qr_backend._basis_gates
        
        self._build_target(self)
        return

    @staticmethod
    def _build_target(self) -> None:
        """
        Builds the Quantum Rings target associated with the backend. 

        Args:
            None

        Returns:
            None

        Raises:
            None

        """

        qubitproperties = []
        for i in range(self._num_qubits):
             qubitproperties.append(self._qr_backend.qubit_properties(i))
           
        self._target = Target(
            description = f"{self._qr_backend.description} with {self._num_qubits} qubits",
            num_qubits = self._num_qubits,
            dt = self._qr_backend.dt,
            qubit_properties = qubitproperties,
            concurrent_measurements = [list(range(self._num_qubits))],
            )

        for gate_name in self._basis_gates:
            if gate_name not in self._supported_gates:
                raise Exception(f"Provided basis gate {gate_name} is not valid.")
            gate = self._supported_gates[gate_name]
            if self._num_qubits < gate.num_qubits:
                raise Exception(f"Gate {gate_name} needs more qubits than the total qubits {self.num_qubits} enabled by the backend.")

            if gate.num_qubits > 1:
                qarg_set = self._coupling_map 
            else:
                qarg_set = range(self._num_qubits)
            

            props = {}
            for qarg in qarg_set:
                if isinstance(qarg, int):
                    key = (qarg,)  
                else:
                    key = (qarg[0], qarg[1])
                    
                props[key] = None

            self._target.add_instruction(gate, properties = props, name = gate_name)

        self._target.add_instruction(IfElseOp, name="if_else")
        self._target.add_instruction(WhileLoopOp, name="while_loop")
        self._target.add_instruction(ForLoopOp, name="for_loop")
        self._target.add_instruction(SwitchCaseOp, name="switch_case")
        self._target.add_instruction(BreakLoopOp, name="break")
        self._target.add_instruction(ContinueLoopOp, name="continue")
                  
        return

                    
    @property
    def target(self) -> Target:
        """
        Returns the Quantum Rings target associated with the backend. 
        """
        return self._target

    @classmethod
    def _default_options(cls) -> Options:
        """
        Returns the default configuration options. 

        Args:
            None

        Returns:
            Options

        Raises:
            None

        """
        op = Options(
            shots = 1024,
        	sync_mode = False,
        	performance = "HIGHESTEFFICIENCY",
        	quiet = True,
        	defaults = True,
        	generate_amplitude = False
        )
        return op


    #@classmethod
    def run(self, run_input, **run_options) -> QrJobV1:
        """
        Executes a qiskit quantum circuit using the Quantum Rings backend 

        Example:
            >>> from qiskit.circuit import QuantumCircuit
            >>> from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister, AncillaRegister
            >>> from qiskit.visualization import plot_histogram
            >>> from matplotlib import pyplot as plt
            >>> 
            >>> import QuantumRingsLib
            >>> from QuantumRingsLib import QuantumRingsProvider
            >>> from quantumrings.toolkit.qiskit import QrBackendV2
            >>> from quantumrings.toolkit.qiskit import QrJobV1
            >>> 
            >>> from matplotlib import pyplot as plt
            >>> 
            >>> qr_provider = QuantumRingsProvider(token =<YOUR_TOKEN>, name=<YOUR_ACCOUNT>)
            >>> 
            >>> shots = 1000
            >>> numberofqubits =  int(qr_provider.active_account()["max_qubits"])
            >>> q = QuantumRegister(numberofqubits , 'q')
            >>> c = ClassicalRegister(numberofqubits , 'c')
            >>> qc = QuantumCircuit(q, c)
            >>> 
            >>> 
            >>> # Create the GHZ state (Greenberger–Horne–Zeilinger)
            >>> qc.h(0);
            >>> for i in range (qc.num_qubits - 1):
            >>>     qc.cx(i, i + 1);
            >>> 
            >>> # Measure all qubits
            >>> qc.measure_all();
            >>> 
            >>> # Execute the quantum code
            >>> mybackend = QrBackendV2(qr_provider, num_qubits = qc.num_qubits)
            >>> qc_transpiled = transpile(qc, mybackend)
            >>> job = mybackend.run(qc_transpiled, shots = shots)
            >>> 
            >>> result = job.result()
            >>> counts = result.get_counts()
            >>> plot_histogram(counts)

        Args:
            run_input (QuantumCircuit): 
                A qiskit QuantumCircuit object.

            shots      (int):
                The number of times the circuit needs to be executed in repetition. The measurement counts are maintained only for the first 10,000 shots. If more execution cycles
                are required, a file name can be provided where the measurements are logged.

            sync_mode   (bool):
                | default - True  - The quantum circuit is executed synchronously.
                | False - The quantum circuit is executed asynchronously.

            performance (str):
                | One of the following strings that define the quality of the circuit execution.
                | default - "HighestEfficiency"
                | "BalancedAccuracy"
                | "HighestAccuracy"
                | "Automatic"
                | "Liberal"

            quiet (bool):
                | default - True - Does not print any message
                | False - Prints some messages, such as which instruction is executed, which may be of help in tracking large circuits

            defaults (bool):
                | default - True  - Uses standard internal settings.
                | False - Uses compact internal settings.
                
            generate_amplitude (bool):
                | True  - Generate amplitudes corresponding to the measurements and print them in the logging file for measurements.
                | (default)  False - Amplitudes are not printed in the logging file.


            file (str):
                An optional file name for logging the measurements.

        Returns:
            QrJobV1

        Raises:
            Exception: If not able to obtain the Quantum Rings Provider or the backend.

        """

        if not isinstance(run_input, QuantumCircuit):
            raise Exception( "Invalid argument passed for Quantum Circuit.")
            return
        
        #TODO: Check control loops
        qreg = QuantumRingsLib.QuantumRegister(run_input.num_qubits, "q")
        creg = QuantumRingsLib.ClassicalRegister(run_input.num_clbits, "meas")
        qc = QuantumRingsLib.QuantumCircuit(qreg, creg, name = run_input.name,  global_phase = run_input.global_phase)

        #
        # We expect the transpiler to do a decent jobs of using required qubits and classical bits
        # for each instruction properly.
        # So they are not value checked
        #

        self._is_final_layout = False

        if (True == hasattr(run_input, "_layout")):
            layout = run_input._layout
            if ( True == hasattr(layout, "final_layout")): 
                self._is_final_layout = True

        QrTranslator.translate_quantum_circuit(run_input, qc, False)
        

        #
        # parse the arguments and pickup the run parameters
        #
        
        if "shots" in run_options:
            shots = run_options.get("shots")
            if not isinstance(shots, int):
                raise Exception( "Invalid argument for shots")
                return
            if ( shots <= 0 ):
                raise Exception( "Invalid argument for shots")
                return
        else:
            shots = self._default_options().shots
            
        if "sync_mode" in run_options:
            sync_mode = run_options.get("sync_mode")
            if not isinstance(sync_mode, bool):
                raise Exception( "Invalid argument for sync_mode")
                return
        else:
            sync_mode = self._default_options().sync_mode

        if "performance" in run_options:
            performance = run_options.get("performance")
            performance = performance.upper()
            if (performance not in ["HIGHESTEFFICIENCY", "BALANCEDACCURACY", "HIGHESTACCURACY", "AUTOMATIC", "LIBERAL"] ):
                raise Exception( "Invalid argument for performance")
                return
        else:
            performance = self._default_options().performance

        if "quiet" in run_options:
            quiet = run_options.get("quiet")
            if not isinstance(quiet, bool):
                raise Exception( "Invalid argument for quiet")
                return
        else:
            quiet = self._default_options().quiet

        if "generate_amplitude" in run_options:
            generate_amplitude = run_options.get("generate_amplitude")
            if not isinstance(generate_amplitude, bool):
                raise Exception( "Invalid argument for generate_amplitude")
                return
        else:
            generate_amplitude = self._default_options().generate_amplitude

        log_file = ""
        if "file" in run_options:
            log_file = run_options.get("file")

        if ("" == log_file):
            generate_amplitude = False

        job = self._qr_backend.run(qc, shots = shots, sync_mode = sync_mode, performance = performance, quiet = quiet, file = log_file, generate_amplitude = generate_amplitude)
        job.wait_for_final_state(0.0, 5.0, self.job_call_back)
        my_job = QrJobV1(self._qr_backend, job)
        return my_job

    def job_call_back(self, job_id, state, job) -> None:
        pass

    @property
    def max_circuits(self) -> int:
        """
        Returns the maximum number of circuits the backend can run at a time. 
        """
        return self._qr_backend.max_circuits
    
    @property
    def num_qubits(self) -> int:
        """
        Returns the number of qubits the backend supports. 
        """
        return self._num_qubits


