from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np
import os
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import depolarizing_error
from qiskit_aer.noise import NoiseModel
import sympy

N_QUBITS = 0

def create_oracle():
    global N_QUBITS
    N_QUBITS = 8
    TARGET_DECIMAL = 255
    TARGET_PASSWORD = format(TARGET_DECIMAL, f'0{N_QUBITS}b')    
    num_qubits = len(TARGET_PASSWORD)
    qc = QuantumCircuit(num_qubits)
    
    # 1. Preparamos el estado (X donde hay ceros)
    for i, bit in enumerate(reversed(TARGET_PASSWORD)): 
        if bit == '0':
            qc.x(i)
    
    # 2. Phase Flip (MCZ)
    qc.h(num_qubits-1)
    qc.mcx(list(range(num_qubits-1)), num_qubits-1)
    qc.h(num_qubits-1)
    
    # 3. Uncomputation (Deshacer X)
    for i, bit in enumerate(reversed(TARGET_PASSWORD)):
        if bit == '0':
            qc.x(i)
            
    oracle_gate = qc.to_gate()
    oracle_gate.name = "Oráculo"

    print(f"Contraseña a buscar: {TARGET_DECIMAL}")
    print(f"Qbits a utilizar: {N_QUBITS}")

    return oracle_gate

def create_oracle_atenea():
    global N_QUBITS
    N_QUBITS = 10
    qc = QuantumCircuit(N_QUBITS, name="Oráculo")

    # Encontramos los números válidos (100–999)
    valid_numbers = [
        n for n in range(100, 1000)
        if sympy.isprime(n) and sum(map(int, str(n))) == 10 and str(n).endswith("7")
    ]

    print(f"Números válidos: {valid_numbers}")

    # Por cada número válido, marcamos ese estado
    for num in valid_numbers:
        bits = format(num, f'0{N_QUBITS}b')
        
        # Aplicamos X a los bits que sean '0' (para convertirlo temporalmente en |11...1>)
        for i, bit in enumerate(reversed(bits)):
            if bit == '0':
                qc.x(i)
        
        # Aplicamos una Z multi-controlada
        qc.h(N_QUBITS-1)
        qc.mcx(list(range(N_QUBITS-1)), N_QUBITS-1)
        qc.h(N_QUBITS-1)
        
        # Deshacemos las X
        for i, bit in enumerate(reversed(bits)):
            if bit == '0':
                qc.x(i)

    return qc.to_gate(label="Oráculo")

def create_diffuser():
    qc = QuantumCircuit(N_QUBITS)
    
    qc.h(range(N_QUBITS))
    qc.x(range(N_QUBITS))
    
    qc.h(N_QUBITS-1)
    qc.mcx(list(range(N_QUBITS-1)), N_QUBITS-1)
    qc.h(N_QUBITS-1)
    
    qc.x(range(N_QUBITS))
    qc.h(range(N_QUBITS))
    
    diffuser_gate = qc.to_gate()
    diffuser_gate.name = "Difusor"
    return diffuser_gate

def run_grover(addNoise, oracle, diffuser):
    grover_circuit = QuantumCircuit(N_QUBITS, N_QUBITS)
    grover_circuit.h(range(N_QUBITS))

    num_iterations = int(np.floor(np.pi/4 * np.sqrt(2**N_QUBITS)))
    print(f"Se realizarán {num_iterations} iteraciones.")

    for _ in range(num_iterations):
        grover_circuit.append(oracle, range(N_QUBITS))
        grover_circuit.append(diffuser, range(N_QUBITS))

    # 3. Medición
    grover_circuit.measure(range(N_QUBITS), range(N_QUBITS))

    simulator = AerSimulator()

    if addNoise == True:
        noise_model = NoiseModel()
        noise_model.add_all_qubit_quantum_error(depolarizing_error(0.02, 1), ['x','h'])
        noise_model.add_all_qubit_quantum_error(depolarizing_error(0.03, 2), ['cx'])
        simulator = AerSimulator(noise_model=noise_model)
  
    compiled_circuit = transpile(grover_circuit, simulator)
    result = simulator.run(compiled_circuit, shots=1024).result()
    counts = result.get_counts()

    # --- RESULTADOS ---
    most_frequent_binary = max(counts, key=counts.get)
    recovered_decimal = int(most_frequent_binary, 2)

    print(f"Cadena binaria más frecuente: {most_frequent_binary} ({recovered_decimal})")

    grover_circuit.draw('mpl')
    plt.show()

    plot_histogram(counts)
    plt.show()

run_grover(False, create_oracle_atenea(), create_diffuser())