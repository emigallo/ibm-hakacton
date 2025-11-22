from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np
from math import floor, pi


# --- Parámetros del Algoritmo de Grover ---
n = 7  # Número de qubits (representa el espacio de contraseñas 2^7 = 128)
# Elegimos una contraseña "objetivo" de 7 bits para marcar (ej: 0b1010101 -> 85)
# El oráculo marcará este estado.
target_state_decimal = 85
target_state_binary = format(target_state_decimal, f'0{n}b')

# Número óptimo de iteraciones de Grover:
# R = floor((pi / 4) * sqrt(N)) donde N = 2^n
N = 2**n
R = floor((pi / 4) * np.sqrt(N))
print(f"Espacio de búsqueda (N): {N} estados")
print(f"Contraseña objetivo (binario): {target_state_binary}")
print(f"Número de iteraciones de Grover (R): {R}")


# Creamos el circuito
qc = QuantumCircuit(3, 3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure([0, 1, 2], [0, 1, 2])

# Ejecutamos en el simulador
sim = AerSimulator()
result = sim.run(qc, shots=1024).result()
counts = result.get_counts()

# Mostramos resultados
print(counts)
qc.draw('mpl')
plot_histogram(counts)
plt.show()
