from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np
from math import floor, pi
import math

def get_bits(number):
    return 7
    # return math.ceil( math.log2(number) + 1)

target_state_decimal = 80
target_statte_digits = get_bits(target_state_decimal)
target_state_binary = format(target_state_decimal, f'0{target_statte_digits}b')
print(f"numero en binario: {target_state_binary}")

def create_oracle():
    """Crea un oráculo que aplica una fase de -1 al estado objetivo."""
    qc_oracle = QuantumCircuit(target_statte_digits)
   
    # Aplicar X a los qubits que son '0' en el estado objetivo.
    # El estado 73 es '1001001'. Qubits 1, 2, 4, 5 son '0'.
    for i, bit in enumerate(target_state_binary):
        if bit == '0':
            qc_oracle.x(i)

    # Aplicar la compuerta Z controlada por todos los qubits (MCZ)
    control_qubits = list(range(target_statte_digits))
    qc_oracle.h(target_statte_digits-1)
    qc_oracle.mcx(control_qubits[:-1], target_statte_digits-1)
    qc_oracle.h(target_statte_digits-1)

    # Deshacer la aplicación de X.
    for i, bit in enumerate(target_state_binary):
        if bit == '0':
            qc_oracle.x(i)

    return qc_oracle

def create_diffuser(n):
    """Crea el operador de difusión de Grover (inversión alrededor de la media)."""
    qc_diffuser = QuantumCircuit(n)
   
    qc_diffuser.h(range(n))
    qc_diffuser.x(range(n))
   
    # Aplicar MCZ para el estado |11...1>
    qc_diffuser.h(n-1)
    qc_diffuser.mcx(list(range(n-1)), n-1)
    qc_diffuser.h(n-1)
   
    qc_diffuser.x(range(n))
    qc_diffuser.h(range(n))
   
    return qc_diffuser

def get_iterations(target_statte_digits, target_decimal, oracle_gate, diff_gate):
    sim = AerSimulator()
    best_iter = 1
    best_prob = 0.0
    best_state = None
    
    for k in range(1, 12):
        qc = QuantumCircuit(target_statte_digits, target_statte_digits)
        qc.h(range(target_statte_digits))
        
        for _ in range(k):
            qc.append(oracle_gate, range(target_statte_digits))
            qc.append(diff_gate, range(target_statte_digits))
        
        qc.measure(range(target_statte_digits), range(target_statte_digits))

        tqc = transpile(qc, sim)
        result = sim.run(tqc, shots=1024).result()
        counts = result.get_counts()
        
        most = max(counts, key=counts.get)
        prob = counts[most] / 1024

        # si este resultado tiene mayor probabilidad del target
        if int(most, 2) == target_decimal and prob > best_prob:
            best_iter = k
            best_prob = prob
            best_state = most

    return best_iter

def run_grover():
    oracle_gate = create_oracle().to_gate(label="Oracle")
    diff_gate   = create_diffuser(target_statte_digits).to_gate(label="Diffuser")

    grover_circuit = QuantumCircuit(target_statte_digits, target_statte_digits)

    # Paso 1: superposición inicial
    grover_circuit.h(range(target_statte_digits))

    # Paso 2: cantidad óptima de iteraciones
    # N = 2**target_statte_digits
    # iterations = int(np.floor(np.pi/4 * np.sqrt(N)))
    iterations = get_iterations(target_statte_digits, target_state_decimal, oracle_gate, diff_gate)
    print(f"Iteraciones de Grover: {iterations}")

    # Paso 3: aplicar Grover varias veces
    for _ in range(iterations):
        grover_circuit.append(oracle_gate, range(target_statte_digits))
        grover_circuit.append(diff_gate, range(target_statte_digits))

    # Paso 4: medir
    grover_circuit.measure(range(target_statte_digits), range(target_statte_digits))

    # --- Simulación ---
    sim = AerSimulator()
    tqc = transpile(grover_circuit, sim)
    result = sim.run(tqc, shots=2048).result()
    counts = result.get_counts()

    most_probable = max(counts, key=counts.get)
    print(f"\n🔐 El código encontrado por Grover es: {most_probable} (binario)")
    print(f"   Valor decimal: {int(most_probable, 2)}")

run_grover()