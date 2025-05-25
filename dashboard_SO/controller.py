import threading
import time
from model import sistema
# from view import DashboardApp # Se sua classe View estiver em um arquivo diferente, importe-a aqui

class Controller:
    def __init__(self, view_instance): # Recebe a instância da View
        self.view = view_instance
        self.processos_atuais = []
        self.processos_anteriores = {}
        self.memoria = {}
        self.uso_cpu_global = 0
        self.tempo_ocioso_global = 0
        self.uso_cpu_por_nucleo = {}
        self.total_processos = 0
        self.total_threads = 0
        self.numero_nucleos = sistema.obter_numero_nucleos_cpu()
        self.intervalo_monitoramento = 1.0

    def iniciar_monitoramento(self):
        def atualizar():
            tempos_cpu_sistema_leitura1 = sistema._obter_tempos_cpu()
            tempo_total_cpu_sistema_leitura1_agregado = tempos_cpu_sistema_leitura1.get('cpu', {}).get('total', 0)
            
            processos_leitura1 = sistema.processos_ativos(tempo_total_cpu_sistema_leitura1_agregado)
            processos_dict_leitura1 = {p.pid: p for p in processos_leitura1}

            self.processos_anteriores = processos_dict_leitura1 

            while True:
                time.sleep(self.intervalo_monitoramento)

                tempos_cpu_sistema_leitura2 = sistema._obter_tempos_cpu()
                tempo_total_cpu_sistema_leitura2_agregado = tempos_cpu_sistema_leitura2.get('cpu', {}).get('total', 0)

                self.uso_cpu_global, self.tempo_ocioso_global, self.uso_cpu_por_nucleo, diferenca_tempo_total_sistema_cpu = \
                    sistema.calcular_uso_cpu_do_intervalo(tempos_cpu_sistema_leitura1, tempos_cpu_sistema_leitura2)

                self.processos_atuais = sistema.processos_ativos(tempo_total_cpu_sistema_leitura2_agregado)
                processos_dict_leitura2 = {p.pid: p for p in self.processos_atuais}

                for pid, proc_atual in processos_dict_leitura2.items():
                    proc_anterior = self.processos_anteriores.get(pid)
                    proc_atual.calcular_uso_cpu(proc_anterior, diferenca_tempo_total_sistema_cpu, self.numero_nucleos)

                self.processos_anteriores = processos_dict_leitura2
                tempos_cpu_sistema_leitura1 = tempos_cpu_sistema_leitura2

                self.memoria = sistema.memoria_global() 
                self.total_processos, self.total_threads = sistema.total_processos_threads()
                uso_memoria_percentual = sistema.uso_memoria_percentual() # Obtém o percentual de uso da memória

                # --- FORMATAR DADOS PARA A NOVA VIEW ---
                formatted_data = self._formatar_dados_para_view(uso_memoria_percentual)
                
                # CHAMA O MÉTODO update_display DA NOVA VIEW
                # Como update_display usa self.after(), precisamos chamá-lo diretamente
                # no contexto da thread principal do Tkinter, o que o after() já faz.
                # Então, o Controller deve garantir que a chamada seja feita de forma segura.
                # A View já tem o `self.after(0, self.update_display, data)`
                # Então, a View não precisa mais do `self.after` aqui.
                # A View agora é um CTk. O Controller vai chamar um método dela diretamente.
                self.view.update_display(formatted_data)


        thread = threading.Thread(target=atualizar, daemon=True)
        thread.start()

    def _formatar_dados_para_view(self, uso_memoria_percentual):
        """
        Formata os dados coletados do sistema em um dicionário
        que a nova View espera.
        """
        # Dados da CPU
        per_cpu_percents = []
        # A View espera 'per_cpu_percent' como uma lista ordenada de floats [cpu0_%, cpu1_%, ...]
        # O self.uso_cpu_por_nucleo é um dicionário {'cpu0': val, 'cpu1': val}
        # Precisamos ordenar pelos IDs para a View.
        cpu_ids_ordenados = sorted([k for k in self.uso_cpu_por_nucleo.keys() if k.startswith('cpu') and k != 'cpu'])
        for cpu_id in cpu_ids_ordenados:
            per_cpu_percents.append(self.uso_cpu_por_nucleo.get(cpu_id, 0.0))

        cpu_data = {
            'cpu_total_percent': self.uso_cpu_global,
            'cpu_idle_percent': self.tempo_ocioso_global,
            'per_cpu_percent': per_cpu_percents,
            'cpu_count': self.numero_nucleos, # Passa o número de núcleos para a View
            'process_count': self.total_processos,
            'thread_count': self.total_threads
        }

        # Dados de Memória
        # A View espera MB, então convertemos de KB para MB
        total_mem_kb = self.memoria.get('MemTotal', 0)
        free_mem_kb = self.memoria.get('MemFree', 0)
        cached_mem_kb = self.memoria.get('Cached', 0)
        swap_total_kb = self.memoria.get('SwapTotal', 0)
        swap_free_kb = self.memoria.get('SwapFree', 0)
        swap_cached_kb = self.memoria.get('SwapCached', 0)

        used_mem_kb = total_mem_kb - free_mem_kb # Isso não é exatamente o usado por psutil, mas é uma aproximação
                                                  # psutil.virtual_memory().used geralmente inclui cache e buffers
                                                  # Se a View usa 'used_memory_mb', é melhor calcular do seu lado
                                                  # ou usar `total_mem_kb - free_mem_kb - cached_mem_kb - buffers_mem_kb` para um 'realmente usado'
                                                  # Por simplicidade, vou usar total - free para 'usado' aqui.
                                                  # Você pode ajustar se a View espera algo diferente.
        
        mem_data = {
            'total_memory_mb': total_mem_kb / 1024,
            'used_memory_mb': used_mem_kb / 1024, # (total - free) em MB
            'free_memory_mb': free_mem_kb / 1024,
            'memory_used_percent': uso_memoria_percentual, # Já vem do sistema.uso_memoria_percentual
            'cache_memory_mb': cached_mem_kb / 1024,
            'swap_total_mb': swap_total_kb / 1024,
            'swap_used_mb': (swap_total_kb - swap_free_kb) / 1024,
            'swap_free_mb': swap_free_kb / 1024,
            'swap_cached_mb': swap_cached_kb / 1024
        }

        # Dados de Processos
        processes_data = []
        for p in self.processos_atuais:
            processes_data.append({
                'pid': p.pid,
                'name': p.nome,
                'uid': p.uid,
                'cpu_percent': p.cpu_percentual,
                'memory_usage_mb': p.memoria_kb / 1024, # Convertendo de KB para MB
                'priority': p.prioridade,
                'state': p.estado
            })
        
        # Sort processes by CPU usage descending
        processes_data.sort(key=lambda x: x.get('cpu_percent', 0.0), reverse=True)


        full_snapshot = {
            'cpu': cpu_data,
            'memory': mem_data,
            'processes': processes_data
        }
        return full_snapshot