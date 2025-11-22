from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator # Usamos AerSimulator para el backend
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np
from math import floor, pi

# ======================================================================
#  1. PARAMETROS GLOBALES
# ======================================================================

n = 7  # Número de qubits
target_state_decimal = 85 # Contraseña objetivo
target_state_binary = format(target_state_decimal, f'0{n}b')

N = 2**n # Espacio de búsqueda
# Número óptimo de iteraciones de Grover: R ≈ (π/4) * sqrt(N)
R = floor((pi / 4) * np.sqrt(N)) 

print(f"Espacio de búsqueda (N): {N} estados")
print(f"Contraseña objetivo (binario): {target_state_binary}")
print(f"Número de iteraciones de Grover (R): {R}")

# ======================================================================
# 2. FUNCIONES: ORÁCULO Y DIFUSOR
# ======================================================================

def create_oracle(n, target_state_binary):
    """Crea un oráculo que aplica una fase de -1 al estado objetivo."""
    qc_oracle = QuantumCircuit(n)
    
    # Aplicar X a los qubits que son '0' en el estado objetivo.
    for i, bit in enumerate(target_state_binary):
        if bit == '0':
            qc_oracle.x(i)

    # Aplicar la compuerta Z controlada por todos los qubits (MCZ)
    control_qubits = list(range(n))
    
    # Implementación de MCZ usando H y Toffolis (MCX)
    qc_oracle.h(n-1)
    # Controlado por los primeros n-1 qubits, aplicado al último
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
    
    # D = H^n * O_0 * H^n
    qc_diffuser.h(range(n))
    qc_diffuser.x(range(n)) # Prepara |00...0> para ser |11...1>
    
    # Aplicar MCZ para el estado |11...1> (que representa O_0)
    qc_diffuser.h(n-1)
    qc_diffuser.mcx(list(range(n-1)), n-1)
    qc_diffuser.h(n-1)
    
    qc_diffuser.x(range(n)) # Deshace la preparación
    qc_diffuser.h(range(n))
    
    return qc_diffuser

# ======================================================================
# 3. CONSTRUCCION Y EJECUCION DEL CIRCUITO
# ======================================================================

# --- Construcción del Circuito Principal ---
grover_circuit = QuantumCircuit(n, n)

# 1. Inicialización: Superposición uniforme
grover_circuit.h(range(n))

# crear el Oráculo y el Difusor con la contraseña
oracle = create_oracle(n, target_state_binary)
diffuser = create_grover_diffuser(n)

# 2. y 3. Iteraciones de Grover (R veces)
for _ in range(R):
    grover_circuit.append(oracle.to_instruction(), range(n)) # Agregamos el oráculo
    grover_circuit.append(diffuser.to_instruction(), range(n)) # Agregamos el difusor

# 4. medición
grover_circuit.measure(range(n), range(n))

# --- ejecucion del circuito ---
backend = AerSimulator() # Usamos AerSimulator
shots = 1024 

t_grover_circuit = transpile(grover_circuit, backend)

job = backend.run(t_grover_circuit, shots=shots)
result = job.result()
counts = result.get_counts()

# --- visualización del resultado ---
print("\n" + "="*40)
print("Resultados de la Simulación:")
print("="*40)

# El estado binario objetivo es '1010101'
measured_key_binary = max(counts, key=counts.get)
measured_key_decimal = int(measured_key_binary, 2)

print(f"Contraseña objetivo (Decimal): **{target_state_decimal}**")
print(f"Clave más probable medida (Binario): **{measured_key_binary}**")
print(f"Clave más probable medida (Decimal): **{measured_key_decimal}**")
print(f"Probabilidad de éxito (aprox): {counts[measured_key_binary] / shots * 100:.2f}%")

plot_histogram(counts, title=f'Resultados del Algoritmo de Grover (N=128, Objetivo={target_state_decimal})')
plt.show() # mostrar el grafico
