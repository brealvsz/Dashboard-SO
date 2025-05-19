from pathlib import Path
from .processo import Processo
import time

def memoria_global():
    meminfo = {}
    with open('/proc/meminfo', 'r') as f:
        for linha in f:
            partes = linha.split(':')
            meminfo[partes[0]] = int(partes[1].strip().split()[0])
    return meminfo

def uso_memoria_percentual():
    mem = memoria_global()
    mem_total = mem.get('MemTotal', 1)
    mem_livre = mem.get('MemLivre', 0)
    uso = 100 - (mem_livre * 100 / mem_total)
    return uso

def processos_ativos():

    processos = []
    for p in Path('/proc').iterdir():
        if p.is_dir() and p.name.isdigit():
            proc = Processo(int(p.name))
            proc.carregar_dados()
            processos.append(proc)
    return processos

def uso_cpu_global(intervalo = 1.0):
    with open('/proc/stat', 'r') as f:
        linha = f.readline()
    valores1 = list(map(int, linha.split()[1:]))
    total1 = sum(valores1)
    idle1 = valores1[3]

    time.sleep(intervalo)

    with open('/proc/stat', 'r') as f:
        linha = f.readline()
    valores2 = list(map(int, linha.split()[1:]))
    total2 = sum(valores2)
    idle2 = valores2[3]

    total_diff = total2 - total1
    idle_diff = idle2 - idle1

    uso = 100.0 * (total_diff - idle_diff) / total_diff
    ocioso = 100.0 * idle_diff / total_diff
    return round(uso, 2), round(ocioso, 2)

def total_processos_threads():
    proc = Path('/proc')
    total_threads = 0
    total_processos = 0
    for p in proc.iterdir():
        if p.is_dir() and p.name.isdigit():
            total_processos += 1
            try:
                with open(p / 'status', 'r') as f:
                    for linha in f:
                        if linha.startswith("Threads:"):
                            total_threads += int(linha.split()[1])
                            break
            except:
                continue
    return total_processos, total_threads
    

