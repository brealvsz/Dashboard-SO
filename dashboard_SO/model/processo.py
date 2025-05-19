
import os

class Processo:
    def __init__(self, pid ):
        self.pid = pid
        self.name = ''
        self.estado = ''
        #self.uid = 0
        self.memoriaKB = 0
        self.threads = 0

    def carregar_dados(self):
        try:
            with open(f'/proc/{self.pid}/status', 'r') as f:
                for linha in f:
                    if linha.startswith('Name:'):
                        self.name = linha.split()[1]
                    elif linha.startswith('State:'):
                        self.estado = linha.split()[1]
                    #elif linha.startswith('Uid:'):
                        #self.uid = int(linha.split()[1])
                    elif linha.startswith('VmRSS:'):
                        self.memoriaKB = int(linha.split()[1])
                    elif linha.startswith('Threads:'):
                        self.threads = int(linha.split()[1])
        except:
            pass
