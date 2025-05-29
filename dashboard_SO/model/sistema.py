from pathlib import Path
#import time
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

    mem = memoria_global()              # obtem todas as infos de memoria global
    total = mem.get('MemTotal', 1)      # pega a memória total do sistema, com fallback para 1 para evitar divisão por zero.
    disponivel = mem.get('MemAvailable', mem.get('MemFree', 0))     # pega a memoria disponivel ou a memoria livre 
    if total == 0:      # para evitar divisao por zero 
        return 0.0
    return round(100 * (total - disponivel) / total, 2)     # calcula o percentual de uso da memória RAM.


def _obter_tempos_cpu():
    tempos_cpu = {} # inicializa um dicionário para armazenar os tempos de CPU 

    # abre o /proc/stat para leitura
    with open('/proc/stat', 'r') as f:
        for linha in f:
            #verifica se a linha começa com "cpu"
            if linha.startswith('cpu'):
                partes = linha.split()  #divide a linha em uma lista de strings 
                id_cpu = partes[0]
                try:
                    # converte os valores restantes da linha
                    valores = list(map(int, partes[1:]))
                    # armazena os tempos para a CPU atual no dicionário tempos_cpu
                    tempos_cpu[id_cpu] = {
                        'total': sum(valores), # soma dos ticks de CPU, representando o tempo total de trabalho
                        'ocioso': valores[3] # tempo ocioso, que é o quarto valor na linha 'cpu'
                    }
                except ValueError:
                    # ignora linhas onde os valores de tempo da CPU não podem ser convertidos para nums inteiros
                    continue
            else:
                # se a linha não começar com 'cpu', verifica se é uma linha vazia ou não alfabética
                # para parar a leitura assim que as linhas de 'cpu' terminam
                if not linha.strip(): # ignora linhas vazias
                    continue
                if not linha[0].isalpha():
                    break
    return tempos_cpu


def calcular_uso_cpu_do_intervalo(tempos_cpu1, tempos_cpu2):
    uso_por_nucleo = {}         # dicionario para armazenar o uso de CPU por nucleo 
    uso_global = 0.0
    ocioso_global = 0.0
    diferenca_total_global_cpu_ticks = 0

    #calcula o uso de CPU
    if 'cpu' in tempos_cpu1 and 'cpu' in tempos_cpu2:
        # diferença total de ticks da CPU do sistema entre as duas leituras
        diferenca_total_global_cpu_ticks = tempos_cpu2['cpu']['total'] - tempos_cpu1['cpu']['total']
        # diferença de ticks ociosos da CPU do sistema
        diferenca_ociosa_global = tempos_cpu2['cpu']['ocioso'] - tempos_cpu1['cpu']['ocioso']
        
        # calcula o percentual de uso e ocioso global. Evita divisão por zero
        if diferenca_total_global_cpu_ticks > 0:
            uso_global = 100.0 * (diferenca_total_global_cpu_ticks - diferenca_ociosa_global) / diferenca_total_global_cpu_ticks
            ocioso_global = 100.0 * diferenca_ociosa_global / diferenca_total_global_cpu_ticks
        else:
            uso_global = 0.0
            ocioso_global = 100.0

    #calcula o uso de CPU para cada núcleo indivualmente 
    for id_cpu, tempos1 in tempos_cpu1.items():
        #ignora cpu global
        if id_cpu == 'cpu':
            continue

        #verifica se o núcleo existia na segunda leitura.
        if id_cpu in tempos_cpu2:
            tempos2 = tempos_cpu2[id_cpu]
            # calcula as diferenças de ticks total e ocioso para o núcleo.
            diferenca_total = tempos2['total'] - tempos1['total']
            diferenca_ociosa = tempos2['ocioso'] - tempos1['ocioso']

            # calcula o percentual de uso do núcleo. Evita divisão por zero.
            if diferenca_total > 0:
                uso_cpu_nucleo = 100.0 * (diferenca_total - diferenca_ociosa) / diferenca_total
            else:
                uso_cpu_nucleo = 0.0
            
            # arredonda e armazena o percentual de uso do núcleo
            uso_por_nucleo[id_cpu] = round(uso_cpu_nucleo, 2)

        # Retorna o uso global, ocioso global, dicionário de uso por núcleo e a diferença total de ticks da CPU global.
    return round(uso_global, 2), round(ocioso_global, 2), uso_por_nucleo, diferenca_total_global_cpu_ticks


def obter_numero_nucleos_cpu():

    # tenta ler o número de núcleos lógicos da CPU a partir de /proc/cpuinfo.
    try:
        contagem_nucleos = 0
        with open('/proc/cpuinfo', 'r') as f:
            for linha in f:
                # cada linha começando com "processor" representa um núcleo lógico
                if linha.strip().startswith('processor'):
                    contagem_nucleos += 1

        # retorna a contagem evitando que seja zero
        return contagem_nucleos if contagem_nucleos > 0 else 1
    
    #tratamento de erro caso arquivo nao seja encontrado -> tratamento para erros diversos
    except FileNotFoundError:
        print("Aviso: /proc/cpuinfo não encontrado. Assumindo 1 núcleo para cálculos de CPU.")
        return 1
    except Exception as e:
        print(f"Erro ao ler /proc/cpuinfo: {str(e)}. Assumindo 1 núcleo para cálculos de CPU.")
        return 1


def processos_ativos(tempo_total_cpu_sistema_atual):
    #inicializa uma lista para 
    lista_processos = [] 
    # itera sobre os diretórios dentro de /proc
    for p in Path('/proc').iterdir():
        # verifica se é um diretório e se o nome é um número (PID)
        if p.is_dir() and p.name.isdigit():
            # cria um objeto de Processp
            proc = Processo(int(p.name))
            # carrega os dados do processo, passando o tempo total da CPU do sistema
            proc.carregar_dados(tempo_total_cpu_sistema_atual)
            # add na lista
            lista_processos.append(proc)
    return lista_processos


def total_processos_threads():
    #contadores para o total de threads e processos
    total_threads = 0
    total_processos = 0
    # itera sobre os diretórios dentro de /proc
    for p in Path('/proc').iterdir():
        # verifica se é um diretório e se o nome é um número (PID)
        if p.is_dir() and p.name.isdigit():
            total_processos += 1
            try:
                # tenta abrir e ler o arquivo /proc/{pid}/status
                with open(p / 'status', 'r') as f:
                    for linha in f:
                        # se a linha começa com com "Threads: "
                        if linha.startswith("Threads:"):
                            # add ao total
                            total_threads += int(linha.split()[1])
                            break
            # ignora erros
            except (FileNotFoundError, PermissionError, ValueError):
                continue
    return total_processos, total_threads