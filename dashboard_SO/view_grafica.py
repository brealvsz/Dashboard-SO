import customtkinter as ctk
import threading # Mantido para 'self.after', embora o loop principal venha do Controller
import time      # Mantido para 'self.after' e potenciais utilitários internos
from tkinter import ttk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

LINE_COLORS = ['#00FFFF', '#FF00FF', '#FFFF00', '#00FF00', '#FF4500', '#BA55D3', '#00BFFF', '#ADFF2F']
MAIN_FONT_FAMILY = "Montserrat"

class DashboardApp(ctk.CTk):
    def __init__(self, num_cpu_cores_param): # NOVO: Recebe num_cpu_cores como parâmetro
        super().__init__()

        self.title("Dashboard Brebs e Jutepie")
        self.geometry("1300x1024")
        
        # REMOVIDO: self.simulator = SystemSimulator(...)
        # self.simulator = SystemSimulator(update_interval_seconds=5)

        # NOVO: O número de núcleos é passado do Controller, que o obteve do Sistema.
        self.num_cpu_cores = num_cpu_cores_param
        # Garante um valor padrão razoável caso a detecção falhe.
        if self.num_cpu_cores is None or self.num_cpu_cores <= 0:
            print("AVISO: Número de núcleos da CPU não fornecido ou inválido para a View. Usando 4 como padrão.")
            self.num_cpu_cores = 4


        # Fonte
        self.title_font = ctk.CTkFont(family=MAIN_FONT_FAMILY, size=20, weight="bold")
        self.header_font = ctk.CTkFont(family=MAIN_FONT_FAMILY, size=16, weight="bold")
        self.label_font = ctk.CTkFont(family=MAIN_FONT_FAMILY, size=12)
        self.detail_label_font = ctk.CTkFont(family=MAIN_FONT_FAMILY, size=10)
        self.small_label_font = ctk.CTkFont(family=MAIN_FONT_FAMILY, size=10)

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_rowconfigure(2, weight=0)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # CPU
        self.cpu_bars_section_frame = ctk.CTkFrame(self.main_frame, fg_color="#2A2D2E")
        self.cpu_bars_section_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=10)
        self.cpu_bars_section_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.cpu_bars_section_frame, text="Uso da CPU", font=self.title_font).pack(pady=(10, 5))
        self.overall_cpu_bar_frame = ctk.CTkFrame(self.cpu_bars_section_frame, fg_color="transparent")
        self.overall_cpu_bar_frame.pack(fill="x", padx=20, pady=(5,10))
        self.overall_cpu_bar_frame.grid_columnconfigure(0, weight=1)
        self.overall_cpu_bar_frame.grid_columnconfigure(1, weight=0)
        self.overall_cpu_bar_frame.grid_columnconfigure(2, weight=0)
        self.overall_cpu_progress = ctk.CTkProgressBar(self.overall_cpu_bar_frame, height=20, fg_color="#3a3a3a", progress_color=LINE_COLORS[0])
        self.overall_cpu_progress.grid(row=0, column=0, sticky="ew", padx=(0,10))
        self.overall_cpu_usage_label = ctk.CTkLabel(self.overall_cpu_bar_frame, text="Total: 0.0%", font=self.label_font)
        self.overall_cpu_usage_label.grid(row=0, column=1, sticky="w", padx=(0,10))
        self.overall_cpu_idle_label = ctk.CTkLabel(self.overall_cpu_bar_frame, text="Ocioso: 0.0%", font=self.label_font)
        self.overall_cpu_idle_label.grid(row=0, column=2, sticky="w")
        self.core_bars_frame = ctk.CTkFrame(self.cpu_bars_section_frame, fg_color="transparent")
        self.core_bars_frame.pack(fill="x", expand=True, padx=20, pady=(0,15))
        self.cpu_core_bars = []
        self.cpu_core_labels_bars = []
        for i in range(int(self.num_cpu_cores)): # Usar self.num_cpu_cores diretamente aqui
            core_frame = ctk.CTkFrame(self.core_bars_frame, fg_color="transparent")
            core_frame.pack(side="left", fill="x", expand=True, padx=5)
            label = ctk.CTkLabel(core_frame, text=f"CPU {i+1}: 0.0%", font=self.small_label_font)
            label.pack(pady=(0,2), anchor="center")
            self.cpu_core_labels_bars.append(label)
            bar = ctk.CTkProgressBar(core_frame, orientation="horizontal", height=12, fg_color="#3a3a3a")
            bar.configure(progress_color=LINE_COLORS[i % len(LINE_COLORS)])
            bar.set(0)
            bar.pack(fill="x", expand=True)
            self.cpu_core_bars.append(bar)

        # Memória
        self.memory_section_frame = ctk.CTkFrame(self.main_frame, fg_color="#2A2D2E")
        self.memory_section_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.memory_section_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.memory_section_frame, text="Uso de Memória", font=self.title_font).pack(pady=(5,3))

        self.memory_bar_container = ctk.CTkFrame(self.memory_section_frame, fg_color="transparent")
        self.memory_bar_container.pack(fill="x", padx=20, pady=(3,5))
        self.memory_bar_container.grid_columnconfigure(0, weight=1)
        self.memory_bar_container.grid_columnconfigure(1, weight=0)
        self.memory_progress = ctk.CTkProgressBar(self.memory_bar_container, height=15, fg_color="#3a3a3a", progress_color=LINE_COLORS[1]) 
        self.memory_progress.grid(row=0, column=0, sticky="ew", padx=(0,10))
        self.memory_usage_percent_label = ctk.CTkLabel(self.memory_bar_container, text="0.0% (0.0/0.0 GB)", font=self.label_font)
        self.memory_usage_percent_label.grid(row=0, column=1, sticky="w")

        self.memory_details_frame = ctk.CTkFrame(self.memory_section_frame, fg_color="transparent")
        self.memory_details_frame.pack(fill="x", padx=20, pady=(0, 8)) 
        self.memory_details_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Linha 0: Total, Usada, Livre (RAM)
        self.mem_detail_total_label = ctk.CTkLabel(self.memory_details_frame, text="Total: -- MB", font=self.detail_label_font)
        self.mem_detail_total_label.grid(row=0, column=0, sticky="w", pady=0, padx=3)
        self.mem_detail_used_label = ctk.CTkLabel(self.memory_details_frame, text="Usada: -- MB", font=self.detail_label_font)
        self.mem_detail_used_label.grid(row=0, column=1, sticky="w", pady=0, padx=3)
        self.mem_detail_free_label = ctk.CTkLabel(self.memory_details_frame, text="Livre: -- MB", font=self.detail_label_font)
        self.mem_detail_free_label.grid(row=0, column=2, sticky="w", pady=0, padx=3)

        # Linha 1: Cache (RAM), Swap Usado, Swap Livre
        self.mem_detail_cache_label = ctk.CTkLabel(self.memory_details_frame, text="Cache(RAM): -- MB", font=self.detail_label_font)
        self.mem_detail_cache_label.grid(row=1, column=0, sticky="w", pady=0, padx=3)
        self.mem_detail_swap_label = ctk.CTkLabel(self.memory_details_frame, text="Swap Usado: -- MB (--%)", font=self.detail_label_font)
        self.mem_detail_swap_label.grid(row=1, column=1, sticky="w", pady=0, padx=3)
        self.mem_detail_swap_free_label = ctk.CTkLabel(self.memory_details_frame, text="Swap Livre: -- MB", font=self.detail_label_font)
        self.mem_detail_swap_free_label.grid(row=1, column=2, sticky="w", pady=0, padx=3)

        # Linha 2: Swap Cache
        self.mem_detail_swap_cache_label = ctk.CTkLabel(self.memory_details_frame, text="Swap Cache: -- MB", font=self.detail_label_font)
        self.mem_detail_swap_cache_label.grid(row=2, column=0, sticky="w", pady=(0,2), padx=3)

        # Processos
        self.process_header_frame = ctk.CTkFrame(self.main_frame, fg_color="#2A2D2E")
        self.process_header_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(5, 0))
        self.process_header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.process_header_frame, text="Processos", font=self.title_font).pack(pady=(5, 3))
        self.process_counts_frame = ctk.CTkFrame(self.process_header_frame, fg_color="transparent")
        self.process_counts_frame.pack(fill="x", padx=20, pady=(0, 5))
        self.process_counts_frame.grid_columnconfigure((0, 1), weight=1)
        self.total_processes_label = ctk.CTkLabel(self.process_counts_frame, text="Total de Processos: --", font=self.label_font)
        self.total_processes_label.grid(row=0, column=0, pady=(0,5), padx=10, sticky="e")
        self.total_threads_label = ctk.CTkLabel(self.process_counts_frame, text="Total de Threads: --", font=self.label_font)
        self.total_threads_label.grid(row=0, column=1, pady=(0,5), padx=10, sticky="w")
        
        self.create_process_treeview() 
        
        self.process_tree.grid(row=3, column=0, sticky="nsew", padx=5, pady=(0,10))

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # REMOVIDO: self.update_data_loop()
        # self.update_data_loop()

    def on_closing(self):
        print("Fechando aplicação...")
        self.destroy()

    def create_process_treeview(self): 
        style = ttk.Style()
        style.theme_use("clam") 
        style.configure("Treeview",
                        background="#2b2b2b", foreground="white",
                        fieldbackground="#2b2b2b", rowheight=28,
                        font=(MAIN_FONT_FAMILY, 10))
        style.map('Treeview', background=[('selected', '#0078D7')])
        style.configure("Treeview.Heading",
                        background="#3a3a3a", foreground="cyan",
                        font=(MAIN_FONT_FAMILY, 11, 'bold'), relief="flat")
        style.map("Treeview.Heading", background=[('active', '#555555')])

        self.process_tree_columns = ("PID", "Nome", "UID", "% CPU", "Memória (MB)", "Prioridade", "Estado")
        self.process_tree = ttk.Treeview(
            self.main_frame, 
            columns=self.process_tree_columns,
            show='headings',
            style="Treeview"
        )
        
        cols_width = {"PID": 70, "Nome": 200, "UID": 70, "% CPU": 80, 
                      "Memória (MB)": 120, "Prioridade": 100, "Estado": 110}
        for col_name in self.process_tree_columns:
            self.process_tree.heading(col_name, text=col_name, anchor="w")
            self.process_tree.column(col_name, anchor="w", width=cols_width.get(col_name, 80), minwidth=cols_width.get(col_name, 50))

    def update_display(self, data): 
        if not data:
            return

        # Dados CPU
        cpu_data = data.get('cpu', {})
        cpu_total_percent = cpu_data.get('cpu_total_percent', 0)
        cpu_idle_percent = cpu_data.get('cpu_idle_percent', 0)
        self.overall_cpu_progress.set(cpu_total_percent / 100)
        self.overall_cpu_usage_label.configure(text=f"Total: {cpu_total_percent:.1f}%")
        self.overall_cpu_idle_label.configure(text=f"Ocioso: {cpu_idle_percent:.1f}%")
        per_cpu_percents = cpu_data.get('per_cpu_percent', [])
        num_cores_display = int(self.num_cpu_cores) # Usar o num_cpu_cores passado no init
        for i in range(num_cores_display):
            if i < len(self.cpu_core_bars):
                if i < len(per_cpu_percents):
                    percent = per_cpu_percents[i]
                    self.cpu_core_bars[i].set(percent / 100)
                    self.cpu_core_labels_bars[i].configure(text=f"CPU {i+1}: {percent:.1f}%")
                else:
                    self.cpu_core_bars[i].set(0)
                    self.cpu_core_labels_bars[i].configure(text=f"CPU {i+1}: N/A")

        # Dados Memória
        mem_data = data.get('memory', {})
        total_mem_mb = mem_data.get('total_memory_mb', 0)
        used_mem_mb = mem_data.get('used_memory_mb', 0)
        total_mem_gb = total_mem_mb / 1024 if total_mem_mb else 0
        used_mem_gb = used_mem_mb / 1024 if used_mem_mb else 0
        
        mem_usage_percent_for_bar = mem_data.get('memory_used_percent', 0)
        self.memory_progress.set(mem_usage_percent_for_bar / 100)
        self.memory_usage_percent_label.configure(text=f"{mem_usage_percent_for_bar:.1f}% ({used_mem_gb:.1f}/{total_mem_gb:.1f} GB)")

        free_memory_mb = mem_data.get('free_memory_mb', 0)
        cache_memory_mb = mem_data.get('cache_memory_mb', 0)
        swap_used_mb = mem_data.get('swap_used_mb', 0)
        swap_total_mb = mem_data.get('swap_total_mb', 1)
        swap_free_mb = mem_data.get('swap_free_mb', 0)
        swap_cached_mb = mem_data.get('swap_cached_mb', 0)

        self.mem_detail_total_label.configure(text=f"Total: {total_mem_mb:.0f} MB ({total_mem_gb:.1f} GB)")
        self.mem_detail_used_label.configure(text=f"Usada: {used_mem_mb:.0f} MB ({used_mem_gb:.1f} GB)")
        self.mem_detail_free_label.configure(text=f"Livre: {free_memory_mb:.0f} MB ({(free_memory_mb/1024 if free_memory_mb else 0):.1f} GB)")
        self.mem_detail_cache_label.configure(text=f"Cache(RAM): {cache_memory_mb:.0f} MB")
        
        swap_used_percent = (swap_used_mb / swap_total_mb) * 100 if swap_total_mb > 0 else 0
        self.mem_detail_swap_label.configure(text=f"Swap Usado: {swap_used_mb:.0f}/{swap_total_mb:.0f}MB ({swap_used_percent:.1f}%)")
        self.mem_detail_swap_free_label.configure(text=f"Swap Livre: {swap_free_mb:.0f} MB")
        self.mem_detail_swap_cache_label.configure(text=f"Swap Cache: {swap_cached_mb:.0f} MB")

        # Contagem Processos
        self.total_processes_label.configure(text=f"Total de Processos: {cpu_data.get('process_count', 0)}")
        self.total_threads_label.configure(text=f"Total de Threads: {cpu_data.get('thread_count', 0)}")

        # Processos Treeview Atualização
        selected_item = self.process_tree.focus()
        scroll_pos_y_tuple = self.process_tree.yview()
        scroll_pos_y = scroll_pos_y_tuple[0] if scroll_pos_y_tuple else 0.0
        
        # Limpar todos os itens existentes na Treeview
        children = self.process_tree.get_children()
        if children:
            self.process_tree.delete(*children)
            
        processes_data = data.get('processes', [])
        for proc in processes_data:
            # Garante que os valores estejam no formato correto esperado pela Treeview
            proc_values = (
                proc.get('pid', 'N/A'),
                proc.get('name', 'N/A')[:25], # Limita o nome a 25 caracteres para não quebrar o layout
                proc.get('uid', 'N/A'),
                f"{proc.get('cpu_percent', 0.0):.1f}",
                f"{proc.get('memory_usage_mb', 0.0):.1f}",
                proc.get('priority', 'N/A'),
                proc.get('state', 'N/A')
            )
            # Usa o PID como iid. Se a Treeview for limpa e recarregada a cada atualização,
            # não haverá problema de iid duplicado.
            iid_str = str(proc.get('pid', 'N/A'))
            try:
                self.process_tree.insert('', 'end', values=proc_values, iid=iid_str)
            except Exception as e:
                # Este bloco de erro é para casos onde o iid pode ser inválido ou algo mais complexo.
                # Se a Treeview é limpa antes de inserir, a duplicação de iid não deveria ocorrer.
                print(f"Erro ao inserir processo {iid_str} no Treeview: {e}")
                pass 
        
        # Tenta restaurar a seleção e a posição de rolagem
        if selected_item and self.process_tree.exists(selected_item):
            try:
                self.process_tree.focus(selected_item)
                self.process_tree.selection_set(selected_item)
            except Exception: pass
        if self.process_tree.get_children():
            try: self.process_tree.yview_moveto(scroll_pos_y)
            except Exception: pass