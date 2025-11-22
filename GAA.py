 GAA.py
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import numpy as np
import matplotlib.pyplot as plt
from math import pi, floor, asin

# ======================================================================
# 1. PARÁMETROS GLOBALES
# ======================================================================
n = 4 # 4 qubits (N = 16 estados)
target_decimal = 10 
target_state_binary = format(target_decimal, f'0{n}b') # Target: 1010
target_subspace = [target_state_binary]

N = 2**n
# Calculamos las iteraciones óptimas para Grover/GAA con superposición uniforme
R = floor((pi / 4) * np.sqrt(N)) 

print(f"Espacio de búsqueda (N): {N} estados")
print(f"Contraseña objetivo (binario): {target_state_binary}")
print(f"Iteraciones óptimas (R): {R}")

# ======================================================================
# 2. FUNCIONES: ORÁCULO DE OBJETIVO (O_G) y REFLEXIÓN INICIAL (O_chi)
# ======================================================================

def get_target_oracle(n, target_subspace):
    """Oráculo de Fase (O_G): Marca el estado objetivo |target> con una fase de -1."""
    qc = QuantumCircuit(n)
    
    # Target: 1010. Qubits 1 y 3 son '0', necesitan X. (Asumiendo orden q0q1q2q3)
    qc.x([1, 3]) 
    
    # Apply MCZ (implementado como H + MCX + H)
    control_qubits = list(range(n))
    qc.h(n-1)
    qc.mcx(control_qubits[:-1], n-1)
    qc.h(n-1)
    
    # Deshacer las X
    qc.x([1, 3])
    return qc

def get_initial_reflection_oracle(n):
    """
    Oráculo de Reflexión (O_chi): Refleja sobre el estado inicial |chi>.
    Para la inicialización con Hadamard, |chi> = |s>, y O_chi es el Difusor de Grover.
    """
    qc_diffuser = QuantumCircuit(n)
    
    qc_diffuser.h(range(n))
    qc_diffuser.x(range(n))
    
    # Apply MCZ for the state |11...1>
    qc_diffuser.h(n-1)
    qc_diffuser.mcx(list(range(n-1)), n-1)
    qc_diffuser.h(n-1)
    
    qc_diffuser.x(range(n))
    qc_diffuser.h(range(n))
    
    return qc_diffuser

# ======================================================================
#  3. CONSTRUCCIÓN Y EJECUCIÓN DEL ALGORITMO
# ======================================================================

def gaa_circuit(n, target_subspace, iterations):
    """Construye el circuito GAA (Q = - O_chi * O_G)"""
    qc = QuantumCircuit(n, n)
    
    # Inicialización: Estado inicial |chi> = |s>
    qc.h(range(n))
    
    # Obtener los operadores como instrucciones (CORRECCIÓN CLAVE)
    oracle_G_inst = get_target_oracle(n, target_subspace).to_instruction()
    oracle_chi_inst = get_initial_reflection_oracle(n).to_instruction()
    
    # Iteraciones GAA
    for _ in range(iterations):
        # Aplicar el Oráculo Objetivo (O_G)
        qc.append(oracle_G_inst, range(n))
        # Aplicar el Operador de Reflexión Inicial (O_chi)
        qc.append(oracle_chi_inst, range(n))

    qc.measure(range(n), range(n))
    return qc

# --- Ejecución ---
circuit = gaa_circuit(n, target_subspace, R)
backend = AerSimulator()
shots = 1024 

t_circuit = transpile(circuit, backend)
job = backend.run(t_circuit, shots=shots)
result = job.result()
counts = result.get_counts()

# --- Análisis de Resultados ---
measured_key_binary = max(counts, key=counts.get)
measured_key_decimal = int(measured_key_binary, 2)
probability_of_target = counts.get(target_state_binary, 0) / shots

print("\n" + "="*40)
print("Resultados de la Amplificación de Amplitud Generalizada (GAA):")
print("="*40)
print(f"Contraseña objetivo (Decimal): **{target_decimal}**")
print(f"Clave más probable medida (Binario): **{measured_key_binary}**")
print(f"Clave más probable medida (Decimal): **{measured_key_decimal}**")
print(f"Probabilidad de éxito: {probability_of_target*100:.2f}%")

plot_histogram(counts, title='Resultados de GAA (Target: 1010)')
plt.show()

