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
# This code is a derivative work of the qiskit provided Statevector class
# See: https://github.com/Qiskit/qiskit/blob/stable/1.3/qiskit/quantum_info/states/statevector.py#L45-L966
# https://docs.quantum.ibm.com/api/qiskit/qiskit.quantum_info.Statevector#statevector
#


# pylint: disable=wrong-import-position,wrong-import-order

from qiskit import QuantumCircuit

import QuantumRingsLib

from quantumrings.toolkit.qiskit import QrTranslator
from qiskit.circuit.instruction import Instruction
from qiskit.quantum_info.operators.op_shape import OpShape

import numpy as np
from numpy.typing import NDArray


class QrStatevector():
    """ Implements the Quantum Rings Statevector class"""

    def __init__(
        self,
        data: np.ndarray | list | QuantumCircuit | Instruction,
        dims: int | tuple | list | None = None,
        *args, 
        **kwargs
    ):
        """Initialize a Quantum Rings statevector object.

        Args:
            data: Data from which the statevector can be constructed. This can be either a complex
                vector, another statevector, a ``Operator`` with only one column or a
                ``QuantumCircuit`` or ``Instruction``.  If the data is a circuit or instruction,
                the statevector is constructed by assuming that all qubits are initialized to the
                zero state.
            dims: The subsystem dimension of the state (usually 2).

        """
        if isinstance(data, (list, np.ndarray)):
            self._data = np.asarray(data, dtype=complex)
        elif isinstance(data, (QuantumCircuit, Instruction)):
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
            
            if isinstance(data, Instruction):
                data = data.definition


            max_qubits = 0
            for j in range (len(data.qregs)):
                max_qubits += data.qregs[0].size
        
            if ( max_qubits <= 0 ):
                raise Exception( "Submitted quantum circuit does not use any qubits")
                return
            
            max_clbits = 0
            for j in range (len(data.cregs)):
                max_clbits += data.cregs[0].size
        
            self._max_qubits = data.num_qubits #max_qubits
            self._max_clbits = data.num_clbits #max_clbits
            
                      
            # if we get here, the measurement instructions, if any, are at the end of the circuit
            # create the quantum circuit now
            
            #TODO: Check control loops
            qreg = QuantumRingsLib.QuantumRegister(self._max_qubits, "q")
            creg = QuantumRingsLib.ClassicalRegister(self._max_clbits, "meas")
            qc   = QuantumRingsLib.QuantumCircuit(qreg, creg, name = data.name,  global_phase = data.global_phase)
        
            self._is_final_layout = False

            if (True == hasattr(data, "_layout")):
                layout = data._layout
                if ( True == hasattr(layout, "final_layout")): 
                    self._is_final_layout = True

            # export the measurements to QuantumRings Structure
            QrTranslator.translate_quantum_circuit(data, 
                                                   qc,
                                                   False
                                                   ) 
        
            
            job = self._qr_backend.run(qc, shots = 1, mode = "sync", performance = "HighestAccuracy", quiet = True)
            job.wait_for_final_state(0.0, 5.0, self.job_call_back)
            self._results = job.result()
            self._data = np.array(self._results.get_statevector())
        else:
            raise Exception ("Invalid input data format for QrStatevector")
        ndim = self._data.ndim
        shape = self._data.shape
        if ndim != 1:
            if ndim == 2 and shape[1] == 1:
                self._data = np.reshape(self._data, shape[0])
                shape = self._data.shape
            elif ndim != 2 or shape[1] != 1:
                raise Exception("Invalid input: not a vector or column-vector.")
        
        return

    def job_call_back(self, job_id, state, job) -> None:
        pass
        
    @property
    def data(self) -> np.ndarray:
        """Return data."""
        return self._data

    def sample_memory(self, shots: int, qargs: None | list = None) -> np.ndarray:
        """Sample a list of qubit measurement outcomes in the computational basis.

        Args:
            shots (int): number of samples to generate.
            qargs (None or list): subsystems to sample measurements for,
                                if None sample measurement of all
                                subsystems (Default: None).

        Returns:
            np.array: list of sampled counts if the order sampled.

        Additional Information:

            This function *samples* measurement outcomes using the measure
            :meth:`probabilities` for the current state and `qargs`. It does
            not actually implement the measurement so the current state is
            not modified.

            The seed for random number generator used for sampling can be
            set to a fixed value by using the stats :meth:`seed` method.
        """

        # Get measurement probabilities for measured qubits
        probs = self._results.get_probabilities(0, 0, qargs)

        # Generate list of possible outcome string labels
        labels = self._index_to_ket_array(
            np.arange(len(probs)), self.dims(qargs), string_labels=True
        )
        return np.random.default_rng().choice(labels, p=probs, size=shots)
    

    @staticmethod
    def _index_to_ket_array(
        inds: np.ndarray, dims: tuple, string_labels: bool = False
    ) -> np.ndarray:
        """Convert an index array into a ket array.

        Args:
            inds (np.array): an integer index array.
            dims (tuple): a list of subsystem dimensions.
            string_labels (bool): return ket as string if True, otherwise
                                  return as index array (Default: False).

        Returns:
            np.array: an array of ket strings if string_label=True, otherwise
                      an array of ket lists.
        """
        shifts = [1]
        for dim in dims[:-1]:
            shifts.append(shifts[-1] * dim)
        kets = np.array([(inds // shift) % dim for dim, shift in zip(dims, shifts)])

        if string_labels:
            max_dim = max(dims)
            char_kets = np.asarray(kets, dtype=np.str_)
            str_kets = char_kets[0]
            for row in char_kets[1:]:
                if max_dim > 10:
                    str_kets = np.char.add(",", str_kets)
                str_kets = np.char.add(row, str_kets)
            return str_kets.T

        return kets.T
    
    def dims(self, qargs=None):
        """Return tuple of input dimension for specified subsystems."""
        return (2,) * len(qargs)
    