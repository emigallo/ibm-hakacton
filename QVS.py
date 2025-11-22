from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ParameterVector, Parameter
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Pauli, SparsePauliOp
import numpy as np
import matplotlib.pyplot as plt

# PARÁMETROS GLOBALES

n = 4  # Qubits para el espacio de búsqueda
target_decimal = 10
target_state_binary = format(target_decimal, f'0{n}b')

# El número total de parámetros (dos capas de rotación + una de entrelazamiento)
num_params = 2 * n

# FUNCIONES
def create_ansatz(n, params):

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

    # 1. Definición del Ansatz
    theta = ParameterVector('θ', num_params)
    ansatz = create_ansatz(n, theta)

    target_op = SparsePauliOp(Pauli('I' * n), coeffs=[1])

    print(f"Ansatz VQS creado con {num_params} parámetros.")
    return ansatz, target_op

# --- Inicialización del VQS ---
ansatz, hamiltonian = vqs_implementation(n, num_params)
