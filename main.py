from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np
from math import floor, pi

# --- Funciones (Reutilizadas del ejemplo anterior) ---
def create_oracle():
    n = 7
    target_state_decimal = 85
    target_state_binary = format(target_state_decimal, f'0{n}b')

    """Crea un oráculo que aplica una fase de -1 al estado objetivo."""
    qc_oracle = QuantumCircuit(n)
   
    # Aplicar X a los qubits que son '0' en el estado objetivo.
    # El estado 73 es '1001001'. Qubits 1, 2, 4, 5 son '0'.
    for i, bit in enumerate(target_state_binary):
        if bit == '0':
            qc_oracle.x(i)

    # Aplicar la compuerta Z controlada por todos los qubits (MCZ)
    control_qubits = list(range(n))
    qc_oracle.h(n-1)
    qc_oracle.mcx(control_qubits[:-1], n-1)
    qc_oracle.h(n-1)

    # Deshacer la aplicación de X.
    for i, bit in enumerate(target_state_binary):
        if bit == '0':
            qc_oracle.x(i)

    return qc_oracle

def create_grover_diffuser(n):
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


print(create_oracle())
