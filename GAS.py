# grover_adaptive.py
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np

# Parámetros
n = 7
target_state_decimal = 73
target_state_binary = format(target_state_decimal, f'0{n}b')

# Reutilizar funciones de oráculo y difusor
from grover_standard_functions import create_oracle, create_grover_diffuser 
# Asumiendo que las funciones están en un módulo separado o en este archivo

def grover_adaptive_search(n, target_state_binary):
    oracle = create_oracle(n, target_state_binary)
    diffuser = create_grover_diffuser(n)
    
    # Secuencia de iteraciones creciente (Estrategia 1: 1, 2, 4, 8, ...)
    k = 0
    max_k = 15 # Límite de intentos
    
    while k < max_k:
        # R_k: Iteraciones en este paso
        R_k = 2**k 
        
        # Construir el circuito para R_k iteraciones
        qc = QuantumCircuit(n, n)
        qc.h(range(n))
        
        for _ in range(R_k):
            qc.append(oracle.to_instruction(), range(n))
            qc.append(diffuser.to_instruction(), range(n))

        qc.measure(range(n), range(n))
        
        # Ejecutar y verificar
        backend = AerSimulator()
        job = backend.run(transpile(qc, backend), shots=1) # Solo 1 shot para verificar
        result = job.result()
        counts = result.get_counts()
        
        measured_state = list(counts.keys())[0]
        
        # Si la solución (target) se encuentra, ¡éxito!
        if measured_state == target_state_binary:
            print(f"🎉 Solución encontrada en la iteración adaptativa k={k} con R={R_k}!")
            return measured_state
            
        k += 1
        
    return None # Si no se encuentra después del límite

# Ejecución
# solution = grover_adaptive_search(n, target_state_binary)
# print(f"Resultado final: {solution}")
