# GAS.py
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np
from math import floor, pi

# ======================================================================
# 1. PARÁMETROS GLOBALES
# ======================================================================

n = 7
target_state_decimal = 73
target_state_binary = format(target_state_decimal, f'0{n}b')

# ======================================================================
#  2. FUNCIONES: ORÁCULO Y DIFUSOR (Incluidas para evitar errores de importación)
# ======================================================================

def create_oracle(n, target_state_binary):
    """Crea un oráculo que aplica una fase de -1 al estado objetivo."""
    qc_oracle = QuantumCircuit(n)
    
    # 1. Aplicar X a los qubits que son '0' en el estado objetivo.
    for i, bit in enumerate(target_state_binary):
        if bit == '0':
            qc_oracle.x(i)

    # 2. Aplicar la compuerta Z controlada por todos los qubits (MCZ)
    control_qubits = list(range(n))
    qc_oracle.h(n-1)
    qc_oracle.mcx(control_qubits[:-1], n-1)
    qc_oracle.h(n-1)

    # 3. Deshacer la aplicación de X.
    for i, bit in enumerate(target_state_binary):
        if bit == '0':
            qc_oracle.x(i)

    return qc_oracle

def create_grover_diffuser(n):
    """Crea el operador de difusión de Grover (inversión alrededor de la media)."""
    qc_diffuser = QuantumCircuit(n)
    
    # D = H^n * O_0 * H^n
    qc_diffuser.h(range(n))
    qc_diffuser.x(range(n))
    
    # Aplicar MCZ para el estado |11...1>
    qc_diffuser.h(n-1)
    qc_diffuser.mcx(list(range(n-1)), n-1)
    qc_diffuser.h(n-1)
    
    qc_diffuser.x(range(n))
    qc_diffuser.h(range(n))
    
    return qc_diffuser

# ======================================================================
# 3. ALGORITMO DE BÚSQUEDA ADAPTATIVA
# ======================================================================

def grover_adaptive_search(n, target_state_binary):
    """
    Implementa el Algoritmo de Búsqueda Adaptativa de Grover (GAS).
    Utiliza una secuencia creciente de iteraciones (2^k) hasta encontrar la solución.
    """
    oracle = create_oracle(n, target_state_binary)
    diffuser = create_grover_diffuser(n)
    
    # Convertimos los circuitos a instrucciones una sola vez
    oracle_inst = oracle.to_instruction()
    diffuser_inst = diffuser.to_instruction()
    
    # Secuencia de iteraciones creciente (Estrategia 1: 1, 2, 4, 8, ...)
    k = 0
    max_k = 12 # Límite de intentos (2^12 > 4*sqrt(128))
    
    print(f"Iniciando Búsqueda Adaptativa para la contraseña: {target_state_binary} (Decimal: {target_state_decimal})")
    
    while k < max_k:
        # R_k: Número de iteraciones en este paso. Usamos 2^k.
        R_k = 2**k 

        # El número óptimo de iteraciones es R ≈ 11.
        # Si R_k es mucho mayor que 11, la probabilidad caerá.

        # Construir el circuito para R_k iteraciones
        qc = QuantumCircuit(n, n)
        qc.h(range(n))

        for _ in range(R_k):
            qc.append(oracle_inst, range(n))
            qc.append(diffuser_inst, range(n))

        qc.measure(range(n), range(n))

        # Ejecutar y verificar
        backend = AerSimulator()
        # Solo necesitamos 1 shot para verificar, pero usamos 100 para estabilidad del simulador
        shots = 100 

        job = backend.run(transpile(qc, backend), shots=shots) 
        result = job.result()
        counts = result.get_counts()

        # La solución se considera "encontrada" si es la más probable
        measured_state = max(counts, key=counts.get)
        probability_of_target = counts.get(target_state_binary, 0) / shots

        print(f"Intento k={k}, R={R_k} iteraciones. Más probable: {measured_state}. Probabilidad de Target: {probability_of_target:.2f}")

        # La condición de éxito en un simulador perfecto es si la probabilidad es alta
        # Usamos la condición original de GAS: si la medición fue la target
        if measured_state == target_state_binary and probability_of_target > 0.5:
             print(f"\n Solución encontrada en la iteración adaptativa k={k} con R={R_k}!")
             return measured_state

        k += 1

    print("\n Límite de intentos alcanzado sin encontrar la solución con alta probabilidad.")
    return None 

# --- Ejecución ---
solution = grover_adaptive_search(n, target_state_binary)
print(f"\nResultado final: Contraseña {target_state_decimal} (Binario: {solution})")
