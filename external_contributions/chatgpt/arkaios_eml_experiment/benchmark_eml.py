"""ARKAIOS–EML: benchmark reproducible de simplificación simbólica.
Ejecutar: python benchmark_eml.py
No mide velocidad de modelos de IA completos.
"""
import math
import random
import statistics
import time

# E(a,b) = exp(a) - ln(b), b>0
# P(x)=E(x,1)=exp(x)
# L(u)=E(1,E(E(1,u),1))=ln(u), u>0

def E(a,b):
    if b <= 0:
        raise ValueError('EML requiere b>0')
    return math.exp(a)-math.log(b)

def P(x): return E(x,1.0)
def L(u): return E(1.0,E(E(1.0,u),1.0))
def composed(x): return L(P(x))
def optimized(x): return x

def benchmark(fn, data, repetitions=5):
    durations=[]
    checksum=0.0
    for _ in range(repetitions):
        start=time.perf_counter()
        checksum=sum(fn(x) for x in data)
        durations.append(time.perf_counter()-start)
    return statistics.median(durations), checksum

def main():
    random.seed(20261020)
    data=[random.uniform(-3,3) for _ in range(25000)]
    # Warm-up
    for x in data[:100]: composed(x); optimized(x)
    native_t, native_s=benchmark(optimized,data)
    eml_t, eml_s=benchmark(composed,data)
    errors=[abs(composed(x)-x) for x in data]
    print('ARKAIOS–EML | identidad ln(exp(x))=x')
    print('Dominio probado: x en [-3,3], float64')
    print(f'Muestras: {len(data)}')
    print(f'EML compuesto (mediana): {eml_t*1000:.3f} ms')
    print(f'Simplificado (mediana): {native_t*1000:.3f} ms')
    print(f'Aceleración simplificado vs EML: {eml_t/native_t:.2f}x')
    print(f'Error absoluto máximo EML: {max(errors):.3g}')
    print(f'Diferencia checksums: {abs(native_s-eml_s):.3g}')
    print('Operadores EML por evaluación: compuesto=4; simplificado=0')
    print('NOTA: Python microbenchmark; no extrapolar a GPU o inferencia IA.')

if __name__=='__main__': main()
