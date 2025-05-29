import threading # p/ executar tarefas em segundo plano (monitoramento)
import time # p/ adicionar pausas (sleep)
from model import sistema # módulo que contém a lógica de coleta de dados

class Controller: # classe que gerencia a lógica de coleta de dados do sistema e a comunicação entre o model e a view
    
    def __init__(self, view_instance): # construtor recebe a instância da view
        self.view = view_instance # armazena para poder atualizar
        self.processos_atuais = [] # lista para armazenar os processos ativos na leitura atual
        self.processos_anteriores = {} # dicionário para armazenar processos da leitura anterior (para cálculo de CPU)
        self.memoria = {} # dicionário para armazenar informações de memória
        self.uso_cpu_global = 0.0 # uso percentual global da CPU
        self.tempo_ocioso_global = 0.0 # tempo percentual ocioso global da CPU
        self.uso_cpu_por_nucleo = {} # dicionário para armazenar o uso percentual de cada núcleo da CPU
        self.total_processos = 0 # número total de processos
        self.total_threads = 0 # número total de threads
        self.numero_nucleos = sistema.obter_numero_nucleos_cpu() # para obter o número de núcleos da CPU do model
        self.intervalo_monitoramento = 1.0 # intervalo entre as atualizações de dados(em segundos)

    def iniciar_monitoramento(self): # inicia o loop de monitoramento em uma nova thread para não bloquear a interface gráfica
        
        def atualizar(): # função executada em loop pela thread de monitoramento(coleta dados do sistema, formata e envia para a view)
        
            # primeira Leitura (antes do loop) - tempos de CPU do sistema 
            tempos_cpu_sistema_leitura1 = sistema._obter_tempos_cpu()
            # agrega o tempo total da CPU da primeira leitura (usado para cálculo de CPU de processos)
            tempo_total_cpu_sistema_leitura1_agregado = tempos_cpu_sistema_leitura1.get('cpu', {}).get('total', 0)
            
            # lista de processos ativos na primeira leitura
            processos_leitura1 = sistema.processos_ativos(tempo_total_cpu_sistema_leitura1_agregado)
            # converte a lista de processos em um dicionário (PID como chave) para acesso rápido
            processos_dict_leitura1 = {p.pid: p for p in processos_leitura1}

            # armazena os processos da primeira leitura como "anteriores" para o primeiro cálculo no loop
            self.processos_anteriores = processos_dict_leitura1 

            # loop de monitoramento
            while True:
                # pausa pelo intervalo de monitoramento
                time.sleep(self.intervalo_monitoramento)

                # segunda leitura (dentro do loop, para comparação) - tempos de CPU do sistema (leitura atual)
                tempos_cpu_sistema_leitura2 = sistema._obter_tempos_cpu()
                # agrega o tempo total da CPU da segunda leitura
                tempo_total_cpu_sistema_leitura2_agregado = tempos_cpu_sistema_leitura2.get('cpu', {}).get('total', 0)

                # calcula o uso global da CPU, tempo ocioso e uso por núcleo comparando as duas leituras
                self.uso_cpu_global, self.tempo_ocioso_global, self.uso_cpu_por_nucleo, diferenca_tempo_total_sistema_cpu = \
                    sistema.calcular_uso_cpu_do_intervalo(tempos_cpu_sistema_leitura1, tempos_cpu_sistema_leitura2)

                # lista de processos ativos na leitura atual
                self.processos_atuais = sistema.processos_ativos(tempo_total_cpu_sistema_leitura2_agregado)
                # converte a lista de processos atuais em um dicionário
                processos_dict_leitura2 = {p.pid: p for p in self.processos_atuais}

                # calcula o uso de CPU para cada processo
                for pid, proc_atual in processos_dict_leitura2.items():
                    proc_anterior = self.processos_anteriores.get(pid) # pega o processo correspondente da leitura anterior
                    # chama o método do objeto processo para calcular seu uso de CPU
                    proc_atual.calcular_uso_cpu(proc_anterior, diferenca_tempo_total_sistema_cpu, self.numero_nucleos)

                # atualiza os "processos anteriores" e "tempos de CPU anteriores" para a próxima iteração
                self.processos_anteriores = processos_dict_leitura2 
                tempos_cpu_sistema_leitura1 = tempos_cpu_sistema_leitura2

                # coleta dados globais de memória
                self.memoria = sistema.memoria_global() 
                # coleta o total de processos e threads
                self.total_processos, self.total_threads = sistema.total_processos_threads()
                # pega o percentual de uso da memória
                uso_memoria_percentual = sistema.uso_memoria_percentual()

                # chama o método interno para formatar
                dados_formatados = self._formatar_dados_para_view(uso_memoria_percentual)
                
                # chama o método 'atualizar_exibicao' da instância da view, passando os dados formatados
                self.view.atualizar_exibicao(dados_formatados)

        # cria uma nova thread que executa a função 'atualizar'
        # 'daemon=True' significa que a thread termina quando o programa principal terminar
        thread_monitoramento = threading.Thread(target=atualizar, daemon=True)
        thread_monitoramento.start() 

    def _formatar_dados_para_view(self, uso_memoria_percentual): # formata todos os dados coletados em um dicionário esperado pela view

        # dados da CPU
        lista_percentuais_por_cpu = []
        # a view espera 'per_cpu_percent' como uma lista ordenada de floats [cpu0_%, cpu1_%, ...]
        # self.uso_cpu_por_nucleo é um dicionário ordenado pelos IDs para a view
        ids_cpu_ordenados = sorted([k for k in self.uso_cpu_por_nucleo.keys() if k.startswith('cpu') and k != 'cpu'])
        for id_cpu in ids_cpu_ordenados:
            lista_percentuais_por_cpu.append(self.uso_cpu_por_nucleo.get(id_cpu, 0.0))

        dados_cpu = {
            'cpu_total_percent': self.uso_cpu_global,
            'cpu_idle_percent': self.tempo_ocioso_global,
            'per_cpu_percent': lista_percentuais_por_cpu, # lista ordenada do uso de cada núcleo
            'cpu_count': self.numero_nucleos, # número de núcleos
            'process_count': self.total_processos,
            'thread_count': self.total_threads
        }

        # dados de memória (convertidos de KB para MB)
        total_mem_kb = self.memoria.get('MemTotal', 0)
        livre_mem_kb = self.memoria.get('MemFree', 0)
        cache_mem_kb = self.memoria.get('Cached', 0) # memória usada para cache de disco
        swap_total_kb = self.memoria.get('SwapTotal', 0)
        swap_livre_kb = self.memoria.get('SwapFree', 0)
        swap_cache_kb = self.memoria.get('SwapCached', 0) # memória de swap que também está em cache RAM

        # calcula a memória usada
        usada_mem_kb = total_mem_kb - livre_mem_kb
        
        dados_memoria = {
            'total_memory_mb': total_mem_kb / 1024,
            'used_memory_mb': usada_mem_kb / 1024, # memória usada 
            'free_memory_mb': livre_mem_kb / 1024, # memória livre 
            'memory_used_percent': uso_memoria_percentual, # mercentual de uso da memória
            'cache_memory_mb': cache_mem_kb / 1024, # memória em cache 
            'swap_total_mb': swap_total_kb / 1024,
            'swap_used_mb': (swap_total_kb - swap_livre_kb) / 1024, # swap usado
            'swap_free_mb': swap_livre_kb / 1024, # swap livre
            'swap_cached_mb': swap_cache_kb / 1024 # swap em cache 
            # tudo convertido para MB, com excessão do percentual já calculado pelo model
        }

        # dados de processos
        dados_processos_lista = []
        for p in self.processos_atuais: # itera sobre a lista de objetos processo
            dados_processos_lista.append({
                'pid': p.pid,
                'name': p.nome,
                'uid': p.uid,
                'cpu_percent': p.cpu_percentual, # percentual de CPU já calculado para o processo
                'memory_usage_mb': p.memoria_kb / 1024, # converte memória do processo de KB para MB
                'priority': p.prioridade,
                'state': p.estado,
                'threads': p.threads
            })
        
        # ordena a lista de processos pelo uso de CPU, do maior para o menor
        dados_processos_lista.sort(key=lambda x: x.get('cpu_percent', 0.0), reverse=True)

        # monta o dicionário final com todos os dados
        snapshot_completo = {
            'cpu': dados_cpu,
            'memory': dados_memoria,
            'processes': dados_processos_lista
        }
        return snapshot_completo