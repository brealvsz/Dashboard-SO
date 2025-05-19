import threading
import time
from model import sistema

class Controller:
    def __init__(self, view):
        self.view = view
        self.processos = []
        self.memoria = {}
        self.uso_cpu = 0 
        self.tempo_ocioso = 0
        self.total_processos = 0
        self.total_threads = 0

    def iniciar_monitoramento(self):
        def atualizar():
            while True:
                self.processos = sistema.processos_ativos()
                self.memoria = sistema.memoria_global()
                self.uso_cpu, self.tempo_ocioso = sistema.uso_cpu_global(0.5)
                self.total_processos, self.total_threads = sistema.total_processos_threads()
                uso_memoria = sistema.uso_memoria_percentual()

                self.view.exibir(
                self.processos,
                self.memoria,
                self.uso_cpu,
                uso_memoria,
                self.tempo_ocioso,
                self.total_processos,
                self.total_threads
            )
                time.sleep(5)

        thread = threading.Thread(target=atualizar, daemon=True)
        thread.start()
