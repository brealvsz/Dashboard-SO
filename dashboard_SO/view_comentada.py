import customtkinter as ctk 
import threading
import time 
from tkinter import ttk # extensão p/ widgets(Treeview)

# aparência global
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CORES_LINHA = ['#00FFFF', '#FF00FF', '#FFFF00', '#00FF00', '#FF4500', '#BA55D3', '#00BFFF', '#ADFF2F']
FONTE_PRINCIPAL = "Montserrat"

class DashboardApp(ctk.CTk): # herança
    def __init__(self, num_nucleos_cpu_param): # construtor classe filha, num de nucleos passado do controller
        super().__init__() # chama construtor classe pai

        # título e tamanho da janela
        self.title("Dashboard Brebs e Jutepie") 
        self.geometry("1300x1024")

        self.num_nucleos_cpu = num_nucleos_cpu_param
        # caso de erro:
        if self.num_nucleos_cpu is None or self.num_nucleos_cpu <= 0:
            print("AVISO: Número de núcleos da CPU não fornecido ou inválido para a View. Usando 4 como padrão.")
            self.num_nucleos_cpu = 4

        # configuração das fontes dos textos da interface
        self.fonte_titulo = ctk.CTkFont(family=FONTE_PRINCIPAL, size=20, weight="bold")
        self.fonte_cabecalho = ctk.CTkFont(family=FONTE_PRINCIPAL, size=16, weight="bold")
        self.fonte_rotulo = ctk.CTkFont(family=FONTE_PRINCIPAL, size=12)
        self.fonte_rotulo_detalhe = ctk.CTkFont(family=FONTE_PRINCIPAL, size=10)
        self.fonte_rotulo_pequeno = ctk.CTkFont(family=FONTE_PRINCIPAL, size=10)

        # cria frame principal
        self.frame_principal = ctk.CTkFrame(self, fg_color="transparent") 
        self.frame_principal.pack(fill="both", expand=True, padx=15, pady=15) # empacota p/ preencher a janela

        # redimensionamento das linhas e colunas do grid do frame principal
        self.frame_principal.grid_rowconfigure(0, weight=0) # não expande verticalmente
        self.frame_principal.grid_rowconfigure(1, weight=0) # não expande verticalmente
        self.frame_principal.grid_rowconfigure(2, weight=0) # não expande verticalmente
        self.frame_principal.grid_rowconfigure(3, weight=1) # expande verticalmente - treeview 
        self.frame_principal.grid_columnconfigure(0, weight=1) # expande horizontalmente

        # frame p/ barras do uso da CPU
        self.frame_secao_barras_cpu = ctk.CTkFrame(self.frame_principal, fg_color="#2A2D2E")
        self.frame_secao_barras_cpu.grid(row=0, column=0, sticky="nsew", padx=5, pady=10) # posição
        self.frame_secao_barras_cpu.grid_columnconfigure(0, weight=1) # barra que expande horizontalmente

        # título seção CPU
        ctk.CTkLabel(self.frame_secao_barras_cpu, text="Uso da CPU", font=self.fonte_titulo).pack(pady=(10, 5))

        # frame p/ barra de progresso geral da CPU
        self.frame_barra_cpu_geral = ctk.CTkFrame(self.frame_secao_barras_cpu, fg_color="transparent")
        self.frame_barra_cpu_geral.pack(fill="x", padx=20, pady=(5,10)) # empacota p/ preencher horizontalmente
        self.frame_barra_cpu_geral.grid_columnconfigure(0, weight=1) # barra de progresso expande
        self.frame_barra_cpu_geral.grid_columnconfigure(1, weight=0) # rótulo de uso não expande
        self.frame_barra_cpu_geral.grid_columnconfigure(2, weight=0) # rótulo de ocioso não expande

        # barra de progresso p/ o uso total da CPU
        self.progresso_cpu_geral = ctk.CTkProgressBar(self.frame_barra_cpu_geral, height=20, fg_color="#3a3a3a", progress_color=CORES_LINHA[0])
        self.progresso_cpu_geral.grid(row=0, column=0, sticky="ew", padx=(0,10)) # posiciona

        # rótulo p/ o percentual de uso total da CPU
        self.rotulo_uso_cpu_geral = ctk.CTkLabel(self.frame_barra_cpu_geral, text="Total: 0.0%", font=self.fonte_rotulo)
        self.rotulo_uso_cpu_geral.grid(row=0, column=1, sticky="w", padx=(0,10))

        # rótulo p/ o percentual de tempo ocioso da CPU
        self.rotulo_cpu_ociosa_geral = ctk.CTkLabel(self.frame_barra_cpu_geral, text="Ocioso: 0.0%", font=self.fonte_rotulo)
        self.rotulo_cpu_ociosa_geral.grid(row=0, column=2, sticky="w")

        # frame p/ as barras de progresso de cada núcleo da CPU
        self.frame_barras_nucleos = ctk.CTkFrame(self.frame_secao_barras_cpu, fg_color="transparent")
        self.frame_barras_nucleos.pack(fill="x", expand=True, padx=20, pady=(0,15))

        # listas p/ armazenar as barras de progresso e os rótulos de cada núcleo
        self.barras_nucleo_cpu = []
        self.rotulos_barras_nucleo_cpu = []
        for i in range(int(self.num_nucleos_cpu)): # itera sobre o número de núcleos da CPU
            # frame individual p/ cada núcleo
            frame_nucleo = ctk.CTkFrame(self.frame_barras_nucleos, fg_color="transparent")
            frame_nucleo.pack(side="left", fill="x", expand=True, padx=5) # empacota lado a lado

            # rótulo p/ o núcleo específico
            rotulo = ctk.CTkLabel(frame_nucleo, text=f"CPU {i+1}: 0.0%", font=self.fonte_rotulo_pequeno)
            rotulo.pack(pady=(0,2), anchor="center") # empacota acima da barra
            self.rotulos_barras_nucleo_cpu.append(rotulo) # adiciona na lista de rótulos

            # barra de progresso p/ o núcleo específico
            barra = ctk.CTkProgressBar(frame_nucleo, orientation="horizontal", height=12, fg_color="#3a3a3a")
            barra.configure(progress_color=CORES_LINHA[i % len(CORES_LINHA)]) # cor da barra (ciclicamente)
            barra.set(0) # define o valor inicial da barra como 0
            barra.pack(fill="x", expand=True) # empacota p/ preencher horizontalmente
            self.barras_nucleo_cpu.append(barra) # adiciona à lista de barras

        # frame p/ agrupar os elementos do uso de memória
        self.frame_secao_memoria = ctk.CTkFrame(self.frame_principal, fg_color="#2A2D2E")
        self.frame_secao_memoria.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.frame_secao_memoria.grid_columnconfigure(0, weight=1) # coluna interna expande

        # rótulo do título da seção de memória
        ctk.CTkLabel(self.frame_secao_memoria, text="Uso de Memória", font=self.fonte_titulo).pack(pady=(5,3))

        # container p/ a barra de progresso da memória
        self.container_barra_memoria = ctk.CTkFrame(self.frame_secao_memoria, fg_color="transparent")
        self.container_barra_memoria.pack(fill="x", padx=20, pady=(3,5))
        self.container_barra_memoria.grid_columnconfigure(0, weight=1) # barra de progresso expande
        self.container_barra_memoria.grid_columnconfigure(1, weight=0) # rótulo de uso não expande

        # barra de progresso p/ o uso de memória
        self.progresso_memoria = ctk.CTkProgressBar(self.container_barra_memoria, height=15, fg_color="#3a3a3a", progress_color=CORES_LINHA[1])
        self.progresso_memoria.grid(row=0, column=0, sticky="ew", padx=(0,10))

        # rótulo p/ exibir o percentual e valores de uso da memória
        self.rotulo_percentual_uso_memoria = ctk.CTkLabel(self.container_barra_memoria, text="0.0% (0.0/0.0 GB)", font=self.fonte_rotulo)
        self.rotulo_percentual_uso_memoria.grid(row=0, column=1, sticky="w")

        # frame p/ os detalhes da memória (total, usada, livre, cache, swap)
        self.frame_detalhes_memoria = ctk.CTkFrame(self.frame_secao_memoria, fg_color="transparent")
        self.frame_detalhes_memoria.pack(fill="x", padx=20, pady=(0, 8))
        self.frame_detalhes_memoria.grid_columnconfigure((0, 1, 2), weight=1) # colunas internas expandem igualmente

        # linha 0: Total, Usada, Livre (RAM)
        self.rotulo_detalhe_mem_total = ctk.CTkLabel(self.frame_detalhes_memoria, text="Total: -- MB", font=self.fonte_rotulo_detalhe)
        self.rotulo_detalhe_mem_total.grid(row=0, column=0, sticky="w", pady=0, padx=3)
        self.rotulo_detalhe_mem_usada = ctk.CTkLabel(self.frame_detalhes_memoria, text="Usada: -- MB", font=self.fonte_rotulo_detalhe)
        self.rotulo_detalhe_mem_usada.grid(row=0, column=1, sticky="w", pady=0, padx=3)
        self.rotulo_detalhe_mem_livre = ctk.CTkLabel(self.frame_detalhes_memoria, text="Livre: -- MB", font=self.fonte_rotulo_detalhe)
        self.rotulo_detalhe_mem_livre.grid(row=0, column=2, sticky="w", pady=0, padx=3)

        # linha 1: Cache (RAM), Swap Usado, Swap Livre
        self.rotulo_detalhe_mem_cache = ctk.CTkLabel(self.frame_detalhes_memoria, text="Cache(RAM): -- MB", font=self.fonte_rotulo_detalhe)
        self.rotulo_detalhe_mem_cache.grid(row=1, column=0, sticky="w", pady=0, padx=3)
        self.rotulo_detalhe_swap_usado = ctk.CTkLabel(self.frame_detalhes_memoria, text="Swap Usado: -- MB (--%)", font=self.fonte_rotulo_detalhe)
        self.rotulo_detalhe_swap_usado.grid(row=1, column=1, sticky="w", pady=0, padx=3)
        self.rotulo_detalhe_swap_livre = ctk.CTkLabel(self.frame_detalhes_memoria, text="Swap Livre: -- MB", font=self.fonte_rotulo_detalhe)
        self.rotulo_detalhe_swap_livre.grid(row=1, column=2, sticky="w", pady=0, padx=3)

        # linha 2: Swap Cache
        self.rotulo_detalhe_swap_cache = ctk.CTkLabel(self.frame_detalhes_memoria, text="Swap Cache: -- MB", font=self.fonte_rotulo_detalhe)
        self.rotulo_detalhe_swap_cache.grid(row=2, column=0, sticky="w", pady=(0,2), padx=3)

        # frame p/ o cabeçalho da seção de processos
        self.frame_cabecalho_processos = ctk.CTkFrame(self.frame_principal, fg_color="#2A2D2E")
        self.frame_cabecalho_processos.grid(row=2, column=0, sticky="nsew", padx=5, pady=(5, 0))
        self.frame_cabecalho_processos.grid_columnconfigure(0, weight=1)

        # rótulo do título da seção de processos
        ctk.CTkLabel(self.frame_cabecalho_processos, text="Processos", font=self.fonte_titulo).pack(pady=(5, 3))

        # frame p/ as contagens de processos e threads
        self.frame_contagens_processos = ctk.CTkFrame(self.frame_cabecalho_processos, fg_color="transparent")
        self.frame_contagens_processos.pack(fill="x", padx=20, pady=(0, 5))
        self.frame_contagens_processos.grid_columnconfigure((0, 1), weight=1) # colunas p/ contagens expandem

        # rótulo p/ o total de processos
        self.rotulo_total_processos = ctk.CTkLabel(self.frame_contagens_processos, text="Total de Processos: --", font=self.fonte_rotulo)
        self.rotulo_total_processos.grid(row=0, column=0, pady=(0,5), padx=10, sticky="e") # alinha à direita (east)

        # rótulo p/ o total de threads
        self.rotulo_total_threads = ctk.CTkLabel(self.frame_contagens_processos, text="Total de Threads: --", font=self.fonte_rotulo)
        self.rotulo_total_threads.grid(row=0, column=1, pady=(0,5), padx=10, sticky="w") # alinha à esquerda (west)

        # cria o treeview (tabela) p/ listar os processos
        self.criar_treeview_processos()

        # posiciona o treeview de processos na grade do frame principal
        self.treeview_processos.grid(row=3, column=0, sticky="nsew", padx=5, pady=(0,10))

        # define a ação a ser tomada quando a janela é fechada (botão 'X')
        self.protocol("WM_DELETE_WINDOW", self.ao_fechar)

    def ao_fechar(self): # método chamado quando o usuário tenta fechar a janela
    
        print("Fechando aplicação...")
        self.destroy() 

    def criar_treeview_processos(self): # cria e configura o treeview(p/ exibir a lista de processos)
        
        estilo = ttk.Style() # objeto de estilo p/ personalizar o treeview
        estilo.theme_use("clam") # tema

        # aparência geral do treeview
        estilo.configure("Treeview",
                        background="#2b2b2b", foreground="white",
                        fieldbackground="#2b2b2b", rowheight=28, # altura da linha
                        font=(FONTE_PRINCIPAL, 10))
        # cor de fundo de um item selecionado
        estilo.map('Treeview', background=[('selected', '#0078D7')])

        # aparência do cabeçalho do treeview
        estilo.configure("Treeview.Heading",
                        background="#3a3a3a", foreground="cyan",
                        font=(FONTE_PRINCIPAL, 11, 'bold'), relief="flat")
        # cor de fundo do cabeçalho quando o mouse está sobre ele
        estilo.map("Treeview.Heading", background=[('active', '#555555')])

        # colunas do treeview
        self.colunas_treeview_processos = ("PID", "Nome", "UID", "% CPU", "Memória (MB)", "Prioridade", "Estado")
        # cria o widget treeview
        self.treeview_processos = ttk.Treeview(
            self.frame_principal, # widget pai
            columns=self.colunas_treeview_processos, # define as colunas
            show='headings', # mostra apenas os cabeçalhos (sem a primeira coluna de ícones)
            style="Treeview" # aplica o estilo configurado
        )

        # largura padrão e mínima das colunas
        larguras_cols = {"PID": 70, "Nome": 200, "UID": 70, "% CPU": 80,
                      "Memória (MB)": 120, "Prioridade": 100, "Estado": 110}
        for nome_col in self.colunas_treeview_processos:
            self.treeview_processos.heading(nome_col, text=nome_col, anchor="w") # texto e alinhamento do cabeçalho
            self.treeview_processos.column(nome_col, anchor="w", width=larguras_cols.get(nome_col, 80), minwidth=larguras_cols.get(nome_col, 50)) # alinhamento, largura e largura mínima da coluna

    def atualizar_exibicao(self, dados): # atualiza os widgets da interface com os novos dados recebidos do controller
    
        if not dados: # se não tem dados, não faz nada
            return

        # atualização dos dados da CPU 
        dados_cpu = dados.get('cpu', {}) # pega o dicionário 'cpu' ou um dicionário vazio se não existir
        percentual_total_cpu = dados_cpu.get('cpu_total_percent', 0)
        percentual_cpu_ociosa = dados_cpu.get('cpu_idle_percent', 0) 

        # atualiza a barra de progresso e os rótulos da CPU geral
        self.progresso_cpu_geral.set(percentual_total_cpu / 100) # valor da barra é entre 0 e 1
        self.rotulo_uso_cpu_geral.configure(text=f"Total: {percentual_total_cpu:.1f}%")
        self.rotulo_cpu_ociosa_geral.configure(text=f"Ocioso: {percentual_cpu_ociosa:.1f}%")

        # atualiza as barras de progresso e rótulos de cada núcleo da CPU
        percentuais_por_cpu = dados_cpu.get('per_cpu_percent', []) # lista com o uso de cada CPU
        num_nucleos_exibicao = int(self.num_nucleos_cpu) # usa o número de núcleos definido no construtor

        for i in range(num_nucleos_exibicao):
            if i < len(self.barras_nucleo_cpu): # verifica se o índice está dentro dos limites da lista de barras
                if i < len(percentuais_por_cpu): # verifica se tem dados para este núcleo
                    percentual = percentuais_por_cpu[i]
                    self.barras_nucleo_cpu[i].set(percentual / 100)
                    self.rotulos_barras_nucleo_cpu[i].configure(text=f"CPU {i+1}: {percentual:.1f}%")
                else: # caso não tenha dados para o núcleo
                    self.barras_nucleo_cpu[i].set(0)
                    self.rotulos_barras_nucleo_cpu[i].configure(text=f"CPU {i+1}: N/A")

        # atualização dos dados de memória
        dados_mem = dados.get('memory', {}) # pega o dicionário 'memory'
        mem_total_mb = dados_mem.get('total_memory_mb', 0)
        mem_usada_mb = dados_mem.get('used_memory_mb', 0)
        mem_total_gb = mem_total_mb / 1024 if mem_total_mb else 0 # converte MB para GB
        mem_usada_gb = mem_usada_mb / 1024 if mem_usada_mb else 0

        # percentual de uso da memória para a barra de progresso
        percentual_uso_mem_para_barra = dados_mem.get('memory_used_percent', 0)
        self.progresso_memoria.set(percentual_uso_mem_para_barra / 100)
        self.rotulo_percentual_uso_memoria.configure(text=f"{percentual_uso_mem_para_barra:.1f}% ({mem_usada_gb:.1f}/{mem_total_gb:.1f} GB)")

        # outras infos da memória
        mem_livre_mb = dados_mem.get('free_memory_mb', 0)
        mem_cache_mb = dados_mem.get('cache_memory_mb', 0)
        swap_usado_mb = dados_mem.get('swap_used_mb', 0)
        swap_total_mb = dados_mem.get('swap_total_mb', 1) # evita divisão por zero
        swap_livre_mb = dados_mem.get('swap_free_mb', 0)
        swap_cache_mb = dados_mem.get('swap_cached_mb', 0)

        # atualiza os rótulos de detalhes da memória
        self.rotulo_detalhe_mem_total.configure(text=f"Total: {mem_total_mb:.0f} MB ({mem_total_gb:.1f} GB)")
        self.rotulo_detalhe_mem_usada.configure(text=f"Usada: {mem_usada_mb:.0f} MB ({mem_usada_gb:.1f} GB)")
        self.rotulo_detalhe_mem_livre.configure(text=f"Livre: {mem_livre_mb:.0f} MB ({(mem_livre_mb/1024 if mem_livre_mb else 0):.1f} GB)")
        self.rotulo_detalhe_mem_cache.configure(text=f"Cache(RAM): {mem_cache_mb:.0f} MB")

        percentual_swap_usado = (swap_usado_mb / swap_total_mb) * 100 if swap_total_mb > 0 else 0
        self.rotulo_detalhe_swap_usado.configure(text=f"Swap Usado: {swap_usado_mb:.0f}/{swap_total_mb:.0f}MB ({percentual_swap_usado:.1f}%)")
        self.rotulo_detalhe_swap_livre.configure(text=f"Swap Livre: {swap_livre_mb:.0f} MB")
        self.rotulo_detalhe_swap_cache.configure(text=f"Swap Cache: {swap_cache_mb:.0f} MB")

        # atualização da contagem de processos 
        self.rotulo_total_processos.configure(text=f"Total de Processos: {dados_cpu.get('process_count', 0)}")
        self.rotulo_total_threads.configure(text=f"Total de Threads: {dados_cpu.get('thread_count', 0)}")

        # atualização do treeview de processos
        item_selecionado = self.treeview_processos.focus() # salva o item selecionado
        posicao_scroll_y_tupla = self.treeview_processos.yview() # salva a posição da barra de rolagem vertical
        posicao_scroll_y = posicao_scroll_y_tupla[0] if posicao_scroll_y_tupla else 0.0

        # limpa todos os itens existentes no treeview antes de adicionar os novos
        filhos = self.treeview_processos.get_children() # pega todos as linhas
        if filhos:
            self.treeview_processos.delete(*filhos) # remove as linhas

        dados_processos = dados.get('processes', []) # pega a lista de processos
        for proc in dados_processos:
            # garante que os valores estejam no formato correto esperado
            valores_proc = (
                proc.get('pid', 'N/A'),
                proc.get('name', 'N/A')[:25], # limita o nome a 25 caracteres para não quebrar o layout
                proc.get('uid', 'N/A'),
                f"{proc.get('cpu_percent', 0.0):.1f}", # formata o percentual de CPU
                f"{proc.get('memory_usage_mb', 0.0):.1f}", # formata o uso de memória
                proc.get('priority', 'N/A'),
                proc.get('state', 'N/A')
            )
            # usa o PID como iid (identificador do item).
            iid_str = str(proc.get('pid', 'N/A'))
            try:
                # insere o novo item no final do treeview
                self.treeview_processos.insert('', 'end', values=valores_proc, iid=iid_str)
            except Exception as e:
                # trata erros sa inserção(embora limpar a treeview deva evitar iid duplicado)
                print(f"Erro ao inserir processo {iid_str} no Treeview: {e}")
                pass

        # tenta restaurar a seleção e a posição de rolagem
        if item_selecionado and self.treeview_processos.exists(item_selecionado): # verifica se o item ainda existe
            try:
                self.treeview_processos.focus(item_selecionado) # restaura o foco
                self.treeview_processos.selection_set(item_selecionado) # restaura a seleção
            except Exception: pass # ignora erros se não for possível restaurar
        if self.treeview_processos.get_children(): # se houver itens no treeview
            try: self.treeview_processos.yview_moveto(posicao_scroll_y) # restaura a posição da rolagem
            except Exception: pass # ignora erros