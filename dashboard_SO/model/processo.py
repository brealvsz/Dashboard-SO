class Processo:
    def __init__(self, pid):
        #atributos que cada processo individual do sistema vai ter
        self.pid = pid
        self.nome = ''
        self.estado = ''
        self.memoria_kb = 0
        self.threads = 0
        self.uid = -1
        self.prioridade = 0

        #atributos necessários para calcular o percentual de CPU que cada processo utiliza
        self.cpu_tempo_usuario = 0
        self.cpu_tempo_sistema = 0
        self.cpu_tempo_total_processo = 0 #soma dos anteriores, representa o total de ticks de CPU
        self.cpu_tempo_total_sistema_na_leitura = 0 #Tempo total de ticks da CPU do sistema no momento em que os dados foram lidos
        self.cpu_percentual = 0.0

    def carregar_dados(self, tempo_total_cpu_sistema_atual):

        # Armazena o tempo total da CPU do sistema no momento da leitura. Sera usado posteriormente no calculo de uso percentual de CPU por processo
        self.cpu_tempo_total_sistema_na_leitura = tempo_total_cpu_sistema_atual

        # Bloco try-except para lidar com erros de leitura de arquivo 
        #talvez tirar
        try:

             # Abre e lê o arquivo /proc/{pid}/status.
            with open(f'/proc/{self.pid}/status', 'r') as f:
                for linha in f:
                    if ':' not in linha: # ignorar as linhas que não contêm o separador ':'
                        continue

                    # Divide a linha em chave e valor, considerando apenas o primeiro ':'
                    chave, valor = linha.split(':', 1)
                    valor = valor.strip() # Remove espaços em branco
                    
                    if chave == 'Name': # nome do processo 
                        self.nome = valor.split()[0]
                    elif chave == 'State': # estado do processo
                        self.estado = valor.split()[0]
                    elif chave == 'VmRSS': #memoria utilizada pelo processo (prefere a VmRSS (resident set size))
                        try:
                            self.memoria_kb = int(valor.split()[0])
                        except ValueError:
                            self.memoria_kb = 0
                    elif chave == 'VmSize' and self.memoria_kb == 0: #se VmRSS nao foi encontrada (ou é 0) tenta VmSize (memoria virtual total)
                        try:
                            self.memoria_kb = int(valor.split()[0])
                        except ValueError:
                            self.memoria_kb = 0
                    elif chave == 'Threads': # qntd de threads
                        try:
                            self.threads = int(valor)
                        except ValueError:
                            self.threads = 0
                    elif chave == 'Uid': # ID do usuario do processo
                        uids = [x for x in valor.split() if x.isdigit()]
                        if uids:
                            try:
                                self.uid = int(uids[0])
                            except ValueError:
                                self.uid = -1
        except FileNotFoundError: # tratamento caso o arquivo não seja encontrado
            self.nome = "[Encerrado]"
            self.estado = ""
            self.memoria_kb = 0
            self.threads = 0
            self.uid = -1
            self.prioridade = 0
            return
        except PermissionError: # tratamento caso não haja permissão para ler o arquivo.
            self.nome = "[Sem Permissão]"
            self.estado = ""
            self.memoria_kb = 0
            self.threads = 0
            self.uid = -1
            self.prioridade = 0
            return
        except Exception as e: # tratamento outros erros inesperados durante a leitura do status.
            print(f"Erro inesperado ao ler /proc/{self.pid}/status: {str(e)}")
            self.nome = "[Erro Status]"
            self.estado = ""
            self.memoria_kb = 0
            self.threads = 0
            self.uid = -1
            self.prioridade = 0
            return

        #uso de cpu e pioridade
        try: 
            with open(f'/proc/{self.pid}/stat', 'r') as f:
                # le a única linha do arquivo e divide em uma lista de strings.
                linha_stat = f.readline().split()
                # a prioridade (nice) se encontra no campo 19, por isso índice 18
                # utime é o 14° campo (índice 13), stime é o 15º campo (índice 14).
                if len(linha_stat) > 18:
                    self.cpu_tempo_usuario = int(linha_stat[13]) # converte para inteiro os ticks de CPU de usuário.
                    self.cpu_tempo_sistema = int(linha_stat[14]) # converte para inteiro os ticks de CPU de sistema.
                    self.cpu_tempo_total_processo = self.cpu_tempo_usuario + self.cpu_tempo_sistema # calcula o tempo total de CPU do processo.
                    self.prioridade = int(linha_stat[18]) # converte para inteiro o valor de prioridade (nice value).
                else:
                    #valores padrao se os campos nao existirem
                    self.cpu_tempo_usuario = 0
                    self.cpu_tempo_sistema = 0
                    self.cpu_tempo_total_processo = 0
                    self.prioridade = 0
        # tratamento de erros como arquivo não encontrado
        # valor não numérico ou índice fora dos limites.
        except (FileNotFoundError, ValueError, IndexError) as e: 
            self.cpu_tempo_usuario = 0
            self.cpu_tempo_sistema = 0
            self.cpu_tempo_total_processo = 0
            self.prioridade = 0
        # tratamento de erros inesperados
        except Exception as e:
            print(f"Erro inesperado ao ler /proc/{self.pid}/stat: {str(e)}")
            self.cpu_tempo_usuario = 0
            self.cpu_tempo_sistema = 0
            self.cpu_tempo_total_processo = 0
            self.prioridade = 0


    def calcular_uso_cpu(self, processo_anterior, diferenca_tempo_total_sistema_cpu, numero_nucleos):

        # se não há dados do processo anterior, ou se o tempo total do sistema não mudou,
        # ou se não há núcleos (evita divisão por zero), o percentual é 0.
        if processo_anterior is None or diferenca_tempo_total_sistema_cpu == 0 or numero_nucleos == 0:
            self.cpu_percentual = 0.0
            return

        # calcula a diferença de ticks de CPU usados pelo processo entre a leitura atual e a anterior.
        diferenca_tempo_cpu_processo = self.cpu_tempo_total_processo - processo_anterior.cpu_tempo_total_processo
        
        # garante que a diferença total de ticks do sistema não seja zero para evitar divisão por zero.
        if diferenca_tempo_total_sistema_cpu > 0:
            self.cpu_percentual = round((diferenca_tempo_cpu_processo * numero_nucleos / diferenca_tempo_total_sistema_cpu) * 100, 2)
            
            if self.cpu_percentual > 1000.0 * numero_nucleos:
                 self.cpu_percentual = 100.0 * numero_nucleos
        else:
            self.cpu_percentual = 0.0