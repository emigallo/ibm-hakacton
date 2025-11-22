# VQS.py
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ParameterVector, Parameter
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Pauli, SparsePauliOp
import numpy as np
import matplotlib.pyplot as plt

# ======================================================================
# 1. PARÁMETROS GLOBALES
# ======================================================================
n = 4  # Qubits para el espacio de búsqueda
target_decimal = 10 
target_state_binary = format(target_decimal, f'0{n}b') # Target: 1010

# El número total de parámetros (dos capas de rotación + una de entrelazamiento)
num_params = 2 * n 

# ======================================================================
# 2. FUNCIONES: ANSATZ
# ======================================================================

def create_ansatz(n, params):
    """
    Define el circuito parametrizado (Ansatz) de tipo hardware-efficient.
    Toma una lista de 2n parámetros.
    """
    qc = QuantumCircuit(n)
    
    # Capa 1: Rotación RY (n parámetros)
    for i in range(n):
        qc.ry(params[i], i)
    
    # Capa de entrelazamiento: CNOTs lineales
    qc.barrier()
    for i in range(n - 1):
        qc.cx(i, i + 1)
    
    # Capa 2: Rotación RY (n parámetros)
    qc.barrier()
    for i in range(n):
        qc.ry(params[i + n], i)

    return qc

def vqs_implementation(n, num_params):
    """
    Define la estructura del algoritmo VQS (VQE adaptado).
    Crea el Ansatz y un Hamiltoniano de Costo para la minimización.
    """
    
    # 1. Definición del Ansatz
    # Creamos un vector de parámetros simbólicos
    theta = ParameterVector('θ', num_params) 
    ansatz = create_ansatz(n, theta)

    # 2. Definición del Operador de Costo (Hamiltoniano)
    # En VQS, queremos *maximizar* la probabilidad del estado objetivo.
    # Esto es equivalente a *minimizar* el Hamiltoniano H = I - |target><target|
    
    # Para el estado |1010>, el proyector es P = |1010><1010|
    # Usaremos una representación Pauli Z para forzar la medición en la base computacional.
    # La forma más simple de Hamiltoniano para |1010> es compleja (requiere operadores Pauli de n-cuerpos).
    
    # --- Alternativa simple (Solo para demostración de la estructura VQS/VQE) ---
    # Usaremos el operador identity para que el Ansatz sea el único factor de costo.
    # En un problema real, este sería el proyector P o el Hamiltoniano de búsqueda.
    target_op = SparsePauliOp(Pauli('I' * n), coeffs=[1])
    
    print(f"Ansatz VQS creado con {num_params} parámetros.")
    return ansatz, target_op

# ======================================================================
#  3. EJECUCIÓN (Simulando la Evaluación Clásica)
# ======================================================================

# --- Inicialización del VQS ---
ansatz, hamiltonian = vqs_implementation(n, num_params)

#  NOTA: La instancia VQE y el optimizador (SPSA) requieren módulos externos
# (qiskit_algorithms) que causaron el error de importación.
