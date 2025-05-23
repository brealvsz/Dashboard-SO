from pathlib import Path
import time
from .processo import Processo


def memoria_global():
    mem_info = {} # inicializa um dicionário para armezenar as infos de memória
    with open('/proc/meminfo', 'r') as f: # abre e lê o arquivo /proc/meminfo
        for linha in f:
            partes = linha.split(':')               # divide cada linha no caractere ':' para separar chave e valor
            if len(partes) > 1:                     #garante que cada linha tenha pelo menos duas partes (chave e valor)
                chave = partes[0].strip()           #remove espaços em branco
                valor = partes[1].strip().split()[0]#remove espaços em branco e pega a primeira parte (valor)
                try:
                    mem_info[chave] = int(valor) # converte o valor para inteiro e armazena no dicionário.
                except ValueError:
                    continue    #ignora linhas em que o valor nao pode ser convertido 
    return mem_info


def uso_memoria_percentual():
    mem = memoria_global()
    total = mem.get('MemTotal', 1)
    disponivel = mem.get('MemAvailable', mem.get('MemFree', 0))
    if total == 0:
        return 0.0
    return round(100 * (total - disponivel) / total, 2)


def _obter_tempos_cpu():
    tempos_cpu = {}
    with open('/proc/stat', 'r') as f:
        for linha in f:
            if linha.startswith('cpu'):
                partes = linha.split()
                id_cpu = partes[0]
                try:
                    valores = list(map(int, partes[1:]))
                    tempos_cpu[id_cpu] = {
                        'total': sum(valores),
                        'ocioso': valores[3]
                    }
                except ValueError:
                    continue
            else:
                if not linha.strip():
                    continue
                if not linha[0].isalpha():
                    break
    return tempos_cpu


def calcular_uso_cpu_do_intervalo(tempos_cpu1, tempos_cpu2):
    uso_por_nucleo = {}
    uso_global = 0.0
    ocioso_global = 0.0
    diferenca_total_global_cpu_ticks = 0

    if 'cpu' in tempos_cpu1 and 'cpu' in tempos_cpu2:
        diferenca_total_global_cpu_ticks = tempos_cpu2['cpu']['total'] - tempos_cpu1['cpu']['total']
        diferenca_ociosa_global = tempos_cpu2['cpu']['ocioso'] - tempos_cpu1['cpu']['ocioso']
        
        if diferenca_total_global_cpu_ticks > 0:
            uso_global = 100.0 * (diferenca_total_global_cpu_ticks - diferenca_ociosa_global) / diferenca_total_global_cpu_ticks
            ocioso_global = 100.0 * diferenca_ociosa_global / diferenca_total_global_cpu_ticks
        else:
            uso_global = 0.0
            ocioso_global = 100.0

    for id_cpu, tempos1 in tempos_cpu1.items():
        if id_cpu == 'cpu':
            continue
        
        if id_cpu in tempos_cpu2:
            tempos2 = tempos_cpu2[id_cpu]
            diferenca_total = tempos2['total'] - tempos1['total']
            diferenca_ociosa = tempos2['ocioso'] - tempos1['ocioso']

            if diferenca_total > 0:
                uso_cpu_nucleo = 100.0 * (diferenca_total - diferenca_ociosa) / diferenca_total
            else:
                uso_cpu_nucleo = 0.0
            
            uso_por_nucleo[id_cpu] = round(uso_cpu_nucleo, 2)

    return round(uso_global, 2), round(ocioso_global, 2), uso_por_nucleo, diferenca_total_global_cpu_ticks


def obter_numero_nucleos_cpu():
    try:
        contagem_nucleos = 0
        with open('/proc/cpuinfo', 'r') as f:
            for linha in f:
                if linha.strip().startswith('processor'):
                    contagem_nucleos += 1
        return contagem_nucleos if contagem_nucleos > 0 else 1
    except FileNotFoundError:
        print("Aviso: /proc/cpuinfo não encontrado. Assumindo 1 núcleo para cálculos de CPU.")
        return 1
    except Exception as e:
        print(f"Erro ao ler /proc/cpuinfo: {str(e)}. Assumindo 1 núcleo para cálculos de CPU.")
        return 1


def processos_ativos(tempo_total_cpu_sistema_atual):
    lista_processos = []
    for p in Path('/proc').iterdir():
        if p.is_dir() and p.name.isdigit():
            proc = Processo(int(p.name))
            proc.carregar_dados(tempo_total_cpu_sistema_atual)
            lista_processos.append(proc)
    return lista_processos


def total_processos_threads():
    total_threads = 0
    total_processos = 0
    for p in Path('/proc').iterdir():
        if p.is_dir() and p.name.isdigit():
            total_processos += 1
            try:
                with open(p / 'status', 'r') as f:
                    for linha in f:
                        if linha.startswith("Threads:"):
                            total_threads += int(linha.split()[1])
                            break
            except (FileNotFoundError, PermissionError, ValueError):
                continue
    return total_processos, total_threads