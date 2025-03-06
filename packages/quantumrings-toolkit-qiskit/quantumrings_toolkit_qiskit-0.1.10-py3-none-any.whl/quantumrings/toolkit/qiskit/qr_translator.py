# This code is part of Quantum Rings SDK.
#
# (C) Copyright Quantum Rings Inc, 2024.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# pylint: disable=wrong-import-position,wrong-import-order

from qiskit.circuit import QuantumCircuit, QuantumRegister
from qiskit.providers import JobStatus

import QuantumRingsLib


class QrTranslator:
    """
    A helper class that translates qiskit components into equivalent QuantumRingsLib's components.
    """
    def __init__(self):
        """
        Class initializer.
        """
        pass

    def check_add_if_condition (
            gate, 
            operation
            ) -> None:
        """
        Checks if an IF condition is to be added to a quantum gate created using QuantumRingsLib's circuit building functions.

        Args:
            | gate: Quantum gate created using a QuantumRingsLib's circuit building function.
            | operation: qiskit operation that was used to generate the gate.

        Returns:
            None
        """
        if (None != operation.condition):
            creg_bit = operation.condition[0]._index
            creg_condition = operation.condition[1]
            gate.c_if(creg_bit, creg_condition)
        return
    
    
    def translate_qiskit_instruction( run_input,
                        qc: QuantumRingsLib.QuantumCircuit, 
                        instruction,
                        qregs : list[QuantumRegister],
                        qubit_lookup_vector,
                        clbit_lookup_vector,
                        is_controlled : bool = False,
                        number_of_control_qubits = 0,
                        ignore_meas : bool = False,
                        is_at_root : bool = True, 
                        ) -> None:
        """
        Translates a given qiskit instruction into a QuantumRingsLib.QuantumCircuit quantum gate.

        Args:
            | run_input : the user defined gate or the qiskit quantumcircuit to be translated to
            | qc : QuantumRingsLib.QuantumCircuit to use.
            | instruction : qiskit instruction to be translated from
            | qubit_lookup_vector - List of qubits this qubit access to. If the gate is directly on the
            | main quantum wires, usually this list is the entire list of qubits. If the gate is stubbed inside a user defined gate,
            | this will be the list of qubits where the user defined gate is placed on the main quantum wires.
            | clbit_lookup_vector : List of classical bits used by the instruction
            | is_controlled : Is this a controlled instruction?
            | number_of_control_qubits : total number of control qubits
            | ignore_meas : Ignore measurement instructions. If set to True, measurement instructions are not translated.
            | is_at_root : Whether the quantum gate is placed directly on the main quantum wires. If so, the qubits involved in the gate are absolute qubits.
            | If not, the qubits involved are relative to the parent gate.
            
        Returns:
            Nothing
        """
        name = instruction.operation.name
        opn = instruction.operation
        remapped_qubit_list = []

        root_qubit_count = 0
        for j in range (len(qregs)):
            root_qubit_count += qregs[j].size
        root_qubit_list = [i for i in range(0, root_qubit_count)]

        if ( True == is_controlled ):
            for i in range (len(instruction.qubits)):
                if (instruction.qubits[i]._register.name == "control"):
                    remapped_qubit_list.append(qubit_lookup_vector[instruction.qubits[i]._index])
                elif (instruction.qubits[i]._register.name == "target"):
                    remapped_qubit_list.append(qubit_lookup_vector[number_of_control_qubits + instruction.qubits[i]._index])
                else:
                    remapped_qubit_list.append(qubit_lookup_vector[instruction.qubits[i]._index])
        else:
            if ( True == is_at_root ): #root_qubit_list == qubit_lookup_vector):
                # if we get here, we are probably placed directly on the root of the circuit (not inside or as a sub circuit)
                # try to fill the remap vector based on the qubit register names
                
                # Check if this was a transpiled circuit. Such circuits will have a layout.
                if (True == hasattr(run_input, "_layout")):
                    for i in range (len(instruction.qubits)):
                        remapped_qubit_list.append(qubit_lookup_vector[instruction.qubits[i]._index])
                else:
                    for i in range (len(instruction.qubits)):
                        reg_base = 0
                        for j in range (len(qregs)):
                            if ( instruction.qubits[i]._register.name == qregs[j].name ):
                                remapped_qubit_list.append(reg_base + instruction.qubits[i]._index)
                            reg_base += qregs[j].size

            # check if we were able to fill in the remap vector based on the above logic. If not, just fill from the lookup vector sent through the function
            if (len(instruction.qubits) != len(remapped_qubit_list)):

                remapped_qubit_list = []    # I dont know, if there will be partial fills from the above step.

                for i in range (len(instruction.qubits)):
                  
                    if (instruction.qubits[i]._index is None):
                        # Handle a case with qiskit 1.3.0 finance tutorial #01, where the qubit object's index is missing

                        qubit_id = id(instruction.qubits[i])
                       
                        b_found = False
                        reg_base = 0
                        for j in range (len(qregs)):
                            for jj in range (qregs[j].size):
                                if ( qubit_id  == id(qregs[j][jj]) ):
                                    remapped_qubit_list.append(reg_base + jj)
                                    b_found = True
                            reg_base += qregs[j].size

                        if False == b_found:
                            # search in the user gate
                            reg_base = 0
                            for j in range (len(run_input.qregs)):
                                for jj in range (run_input.qregs[j].size):
                                    if ( qubit_id  == id(run_input.qregs[j][jj]) ):
                                        remapped_qubit_list.append(reg_base + jj)
                                        b_found = True
                                reg_base += qregs[j].size

                        if False == b_found:
                            raise Exception ("Unable to map the instruction qubits into the circuit space.")
                    else:    
                        remapped_qubit_list.append(qubit_lookup_vector[instruction.qubits[i]._index])

        # when we get here the remapped_qubit_list contains the list of qubits remapped in the order they appear in the instructions.
        
        # Now, the classical bits
        remapped_clbit_list = []
        for i in range (len(instruction.clbits)):
                remapped_clbit_list.append(clbit_lookup_vector[instruction.clbits[i]._index])

        
        #QrTranslator.print_instruction(instruction, qubit_lookup_vector, remapped_qubit_list)

        #
        # Instructions dispatcher
        #
    
        if (name == "h"):
            gate = qc.h(remapped_qubit_list[0])
        elif (name == "x"):
            gate = qc.x(remapped_qubit_list[0])
        elif (name == "id"):
            gate = qc.id(remapped_qubit_list[0])
        elif (name == "t"):
            gate = qc.t(remapped_qubit_list[0]) 
        elif (name == "s"):
            gate = qc.s(remapped_qubit_list[0]) 
        elif (name == "tdg"):
            gate = qc.tdg(remapped_qubit_list[0])
        elif (name == "sdg"):
            gate = qc.sdg(remapped_qubit_list[0])
        elif (name == "sx"):
            gate = qc.sx(remapped_qubit_list[0])
        elif (name == "sxdg"):
            gate = qc.sxdg(remapped_qubit_list[0])                  
        elif (name == "p"):
            gate = qc.p(instruction.params[0], remapped_qubit_list[0])   
        elif (name == "r"):
            gate = qc.r(instruction.params[0], instruction.params[1], remapped_qubit_list[0])   
        elif (name == "rx"):
            gate = qc.rx(instruction.params[0], remapped_qubit_list[0])   
        elif (name == "ry"):
            gate = qc.ry(instruction.params[0], remapped_qubit_list[0]) 
        elif (name == "rz"):
            gate = qc.rz(instruction.params[0], remapped_qubit_list[0]) 
        elif (name == "u"):
            gate = qc.u(instruction.params[0], instruction.params[1], instruction.params[2], remapped_qubit_list[0])   
        elif (name == "y"):
            gate = qc.y(remapped_qubit_list[0])  
        elif (name == "z"):
            gate = qc.z(remapped_qubit_list[0])  
        elif (name == "delay"):
            gate = qc.delay(instruction.params[0], remapped_qubit_list[0]) 
        elif (name == "cx"):
            gate = qc.cx(remapped_qubit_list[0], remapped_qubit_list[1])
        elif (name == "cy"):
            gate = qc.cy(remapped_qubit_list[0], remapped_qubit_list[1])
        elif (name == "cz"):
            gate = qc.cz(remapped_qubit_list[0], remapped_qubit_list[1])
        elif (name == "ch"):
            gate = qc.ch(remapped_qubit_list[0], remapped_qubit_list[1])
        elif (name == "cp"):
            gate = qc.cp(instruction.params[0], remapped_qubit_list[0], remapped_qubit_list[1])
        elif (name == "crx"):
            gate = qc.crx(instruction.params[0], remapped_qubit_list[0], remapped_qubit_list[1])            
        elif (name == "cry"):
            gate = qc.cry(instruction.params[0], remapped_qubit_list[0], remapped_qubit_list[1])        
        elif (name == "crz"):
            gate = qc.crz(instruction.params[0], remapped_qubit_list[0], remapped_qubit_list[1])  
        elif (name == "cs"):
            gate = qc.cs(remapped_qubit_list[0], remapped_qubit_list[1])
        elif (name == "csdg"):
            gate = qc.csdg(remapped_qubit_list[0], remapped_qubit_list[1])           
        elif (name == "csx"):
            gate = qc.csx(remapped_qubit_list[0], remapped_qubit_list[1])  
        elif (name == "cu"):
            gate = qc.cu(instruction.params[0], instruction.params[1], instruction.params[2], instruction.params[3], remapped_qubit_list[0], remapped_qubit_list[1])  
        elif (name == "dcx"):
            gate = qc.dcx(remapped_qubit_list[0], remapped_qubit_list[1]) 
        elif (name == "ecr"):
            gate = qc.ecr(remapped_qubit_list[0], remapped_qubit_list[1])                
        elif (name == "iswap"):
            gate = qc.iswap(remapped_qubit_list[0], remapped_qubit_list[1])   
        elif (name == "rxx"):
            gate = qc.rxx(instruction.params[0], remapped_qubit_list[0], remapped_qubit_list[1])  
        elif (name == "ryy"):
            gate = qc.ryy(instruction.params[0], remapped_qubit_list[0], remapped_qubit_list[1])  
        elif (name == "rzx"):
            gate = qc.rzx(instruction.params[0], remapped_qubit_list[0], remapped_qubit_list[1]) 
        elif (name == "rzz"):
            gate = qc.rzz(instruction.params[0], remapped_qubit_list[0], remapped_qubit_list[1]) 
        elif (name == "swap"):
            gate = qc.swap(remapped_qubit_list[0], remapped_qubit_list[1])   
        elif (name == "measure"):
            if ( False == ignore_meas):
                gate = qc.measure(remapped_qubit_list[0], instruction.clbits[0]._index)
            else:
                gate = qc.id(remapped_qubit_list[0])
        elif (name == "reset"):
            gate = qc.reset(remapped_qubit_list[0])   
        elif (name == "cu1"):
            gate = qc.cu1(instruction.params[0], remapped_qubit_list[0], remapped_qubit_list[1]) 
        elif (name == "cu3"):
            gate = qc.cu3(instruction.params[0], instruction.params[1], instruction.params[2], remapped_qubit_list[0], remapped_qubit_list[1]) 
        elif (name == "u1"):
            gate = qc.u1(instruction.params[0], remapped_qubit_list[0])
        elif (name == "u2"):
            gate = qc.u2(instruction.params[0], instruction.params[1], remapped_qubit_list[0])                
        elif (name == "barrier"):
            gate = qc.barrier(remapped_qubit_list)
        elif (name == "ms"):
            gate = qc.ms(instruction.params[0], remapped_qubit_list)
        elif (name == "rv"):
            gate = qc.rv(instruction.params[0], instruction.params[1], instruction.params[2], remapped_qubit_list[0])
        elif (name == "mcp"):
            gate = qc.mcp(instruction.params[0], remapped_qubit_list[:-1], remapped_qubit_list[-1])
        elif (name == "rccx"):
            gate = qc.rccx(remapped_qubit_list[0], remapped_qubit_list[1], remapped_qubit_list[2])
        elif (name == "rcccx"):
            gate = qc.rcccx(remapped_qubit_list[0], remapped_qubit_list[1], remapped_qubit_list[2], remapped_qubit_list[3])
        elif (name == "cswap"):
            gate = qc.cswap(remapped_qubit_list[0], remapped_qubit_list[1], remapped_qubit_list[2])
        elif (name == "ccx"):
            gate = qc.ccx(remapped_qubit_list[0], remapped_qubit_list[1], remapped_qubit_list[2])
        elif (name == "ccz"):
            gate = qc.ccz(remapped_qubit_list[0], remapped_qubit_list[1], remapped_qubit_list[2])
        elif (name == "mcx"):
            gate = qc.mcx(remapped_qubit_list[:-1], remapped_qubit_list[-1])
        elif (name == "unitary"):
            unitary_matrix = instruction.params[0]
            gate = qc.unitary(unitary_matrix[0][0], unitary_matrix[0][1], unitary_matrix[1][0], unitary_matrix[1][1], remapped_qubit_list[0])
        else:
            return False
                
        QrTranslator.check_add_if_condition(gate, opn)
        return True


    def emit_quantum_circuit_(run_input : QuantumCircuit, 
                              qc: QuantumRingsLib.QuantumCircuit,
                              qregs : list[QuantumRegister],
                              qubit_lookup_vector,
                              clbit_lookup_vector,
                              is_controlled : bool = False,
                              number_of_control_qubits = 0,
                              ignore_meas : bool = False,
                              is_at_root : bool = True 
                              ) -> None:
        for instruction in run_input:
            
            if ( True == QrTranslator.translate_qiskit_instruction( run_input, qc, instruction, qregs, qubit_lookup_vector, clbit_lookup_vector, is_controlled, number_of_control_qubits, ignore_meas, is_at_root) ):
                continue

            # check if it is a non-standard gate
            if instruction.operation._standard_gate is None:
                gate_name_ = instruction.name

                is_this_gate_controlled_ = instruction.is_controlled_gate()
                if (True == is_this_gate_controlled_):
                    number_of_controls_in_this_gate_ = instruction.operation.num_ctrl_qubits
                else:
                    number_of_controls_in_this_gate_ = 0
                
                qubits_in_the_gate = []
                clbits_in_the_gate = []

                root_qubit_count = 0
                for j in range (len(qregs)):
                    root_qubit_count += qregs[j].size

                #
                # Construct the instructions under this gate into it
                #
                if ( True == is_this_gate_controlled_):

                    full_range_qubit = [i for i in range(0, root_qubit_count)]
                    full_range_clbit = [i for i in range(0, run_input.num_clbits)]

                    if ( True == is_at_root):
                        for i in range (len(instruction.qubits)):
                            qubits_in_the_gate.append(full_range_qubit[instruction.qubits[i]._index])
                    else:
                        for i in range (len(instruction.qubits)):
                            if (instruction.qubits[i]._register.name == "control"):
                                qubits_in_the_gate.append(qubit_lookup_vector[instruction.qubits[i]._index])
                            elif (instruction.qubits[i]._register.name == "target"):
                                qubits_in_the_gate.append(qubit_lookup_vector[number_of_control_qubits + instruction.qubits[i]._index])
                            else:
                                qubits_in_the_gate.append(qubit_lookup_vector[instruction.qubits[i]._index])
                
                    for i in range (len(instruction.clbits)):
                        clbits_in_the_gate.append(full_range_clbit[instruction.clbits[i]._index])

                    QrTranslator.emit_quantum_circuit_(instruction.operation.definition,
                                              qc,
                                              qregs,
                                              qubits_in_the_gate,
                                              clbits_in_the_gate,
                                              is_this_gate_controlled_,
                                              number_of_controls_in_this_gate_,
                                              ignore_meas,
                                              False
                                             )
                else:
                    
                    full_range_qubit = [i for i in range(0, root_qubit_count)]

                    if ( full_range_qubit == qubit_lookup_vector):
                        for i in range (len(instruction.qubits)):
                            reg_base = 0
                            for j in range (len(run_input.qregs)):
                                if ( instruction.qubits[i]._register.name == run_input.qregs[j].name ):
                                    qubits_in_the_gate.append(reg_base + instruction.qubits[i]._index)
                                reg_base += qregs[j].size
                        
                        # At times a user defined gate may use a qubit naming convention different from the parent quantum circuit
                        # If so, take it from the lookup vector
                        if ( len(qubits_in_the_gate) != len(instruction.qubits) ) :
                            for i in range (len(instruction.qubits)):
                                qubits_in_the_gate.append(qubit_lookup_vector[instruction.qubits[i]._index])

                        for i in range (len(instruction.clbits)):
                            clbits_in_the_gate.append(clbit_lookup_vector[instruction.clbits[i]._index])
                        
                    else:   

                        for i in range (len(instruction.qubits)):
                            qubits_in_the_gate.append(qubit_lookup_vector[instruction.qubits[i]._index])
                    
                        for i in range (len(instruction.clbits)):
                            clbits_in_the_gate.append(clbit_lookup_vector[instruction.clbits[i]._index])

                    QrTranslator.emit_quantum_circuit_(instruction.operation.definition,
                                              qc,
                                              qregs,
                                              qubits_in_the_gate, 
                                              clbits_in_the_gate, 
                                              is_this_gate_controlled_,
                                              number_of_controls_in_this_gate_,
                                              ignore_meas,
                                              False
                                             )
            else:
                raise Exception( f"Instruction {gate_name_} is not supported.")
        return
        
    def translate_quantum_circuit(run_input : QuantumCircuit, 
                                   qc: QuantumRingsLib.QuantumCircuit,
                                   ignore_meas = False,
                                   ) -> None:
        """
        The main function to be called to translate a qiskit QuantumCircuit into a QuantumRings' QuantumCircuit.

        Args:
            | run_input : qiskit developed QuantumCircuit
            | qc : QuantumRingsLib.QuantumCircuit to which the translation is to be done.
            | ignore_meas : True -- ignore measurement gates
            |             : False -- process measurement gates
        Returns:
            None

        """

        qubit_layout = [i for i in range(0, run_input.num_qubits)]
        final_layout = []

        if (True == hasattr(run_input, "_layout")):
            layout = run_input._layout

            if ( True == hasattr(layout, "initial_layout")):
                if (layout.initial_layout is not None):
                    l = layout.initial_layout.get_physical_bits()
                    input_permutation = [i for i in range(0, len(l))]

                    for key, value in l.items():
                        input_permutation[key] = value._index
                    
                    for i in range (0, len(qubit_layout)):
                        final_layout.append(input_permutation[qubit_layout[i]])

            if ( True == hasattr(layout, "final_layout")):      
                if (layout.final_layout is not None):
                    l = layout.final_layout.get_physical_bits()
                    input_permutation = [i for i in range(0, len(l))]
                    
                    for key, value in l.items():
                        input_permutation[key] = value._index

                    final_layout = []
                    for i in range (0, len(qubit_layout)):
                        final_layout.append(input_permutation[qubit_layout[i]])
            
            # Check if the final_layout has got all the qubits and just only once
            if ((set(range(run_input.num_qubits)) != set(final_layout)) or (len(final_layout) != run_input.num_qubits)):
                if ( True == hasattr(layout, "_output_qubit_list")) :
                    final_layout = []
                    for item in layout._output_qubit_list:
                        final_layout.append(item._index)
                else:
                    final_layout = qubit_layout

        if (len(final_layout) == run_input.num_qubits):
            qubit_lookup_vector = final_layout
        else:
            qubit_lookup_vector = [i for i in range(0, run_input.num_qubits)]

        clbit_lookup_vector = [i for i in range(0, run_input.num_clbits)]

        QrTranslator.emit_quantum_circuit_(run_input,
                              qc,
                              run_input.qregs,
                              qubit_lookup_vector,
                              clbit_lookup_vector,
                              False,
                              0,
                              ignore_meas,
                              True 
                              )
        return

    
    def translate_job_status(
            qr_status : QuantumRingsLib.JobStatus
            ) -> JobStatus:
        """
        Translates a QuantumRingsLib defined JobStatus to a qiskit defined JobStatus.

        Args:
            | qr_status : QuantumRingsLib.JobStatus

        Returns:
            Equivalent qiskit JobStatus
        """
        if (qr_status == QuantumRingsLib.JobStatus.INITIALIZING):
            return JobStatus.INITIALIZING
        elif (qr_status == QuantumRingsLib.JobStatus.QUEUED):
            return JobStatus.QUEUED
        elif (qr_status == QuantumRingsLib.JobStatus.VALIDATING):
            return JobStatus.VALIDATING
        elif (qr_status == QuantumRingsLib.JobStatus.RUNNING):
            return JobStatus.RUNNING
        elif (qr_status == QuantumRingsLib.JobStatus.CANCELLED):
            return JobStatus.CANCELLED
        elif (qr_status == QuantumRingsLib.JobStatus.DONE):
            return JobStatus.DONE
        elif (qr_status == QuantumRingsLib.JobStatus.ERROR):
            return JobStatus.ERROR
        else:
            return qr_status

    def print_instruction(instruction, 
                          lookup_vector=[],
                          remap_vector=[]
                          ) -> None:
        """
        Prints a qiskit instruction
        """
        name = "\t" + instruction.operation.name
        name += '('
        for i in range (len(instruction.params)):
            name +=  str(instruction.params[i]) + ","
        name += ') '
        
        for i in range (len(instruction.qubits)):
            name += instruction.qubits[i]._register.name + '[' + str(instruction.qubits[i]._index) + '],'

        name = name[:-1]
        
        if ( len(instruction.clbits)):
            name += " -> "

            for i in range (len(instruction.clbits)):
                name += instruction.clbits[i]._register.name + '[' + str(instruction.clbits[i]._index) + '],'

            name = name[:-1]

        print(f"Instruction: {name} Lookup Vector: {lookup_vector} Remap Vector: {remap_vector}")
    
    def analyze_instructions(run_input) -> None:
        """
        Prints a given qiskit QuantumCircuit
        """
        for instruction in run_input:
            QrTranslator.print_instruction(instruction) 