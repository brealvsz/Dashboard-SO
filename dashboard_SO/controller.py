import threading
import time
from model import sistema

class Controller:
    def __init__(self, view):
        self.view = view
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
                uso_memoria = sistema.uso_memoria_percentual()

                self.view.exibir(
                    self.processos_atuais,
                    self.memoria,
                    self.uso_cpu_global,
                    uso_memoria,
                    self.tempo_ocioso_global,
                    self.total_processos,
                    self.total_threads,
                    self.uso_cpu_por_nucleo
                )


        thread = threading.Thread(target=atualizar, daemon=True)
        thread.start()