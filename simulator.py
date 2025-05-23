import threading
import time
import random
import uuid
import psutil # Mantido para obter o número real de cores, se necessário
from datetime import datetime

class SystemSimulator:
    def __init__(self, update_interval_seconds=5):
        self._lock = threading.Lock()
        self._current_snapshot = {}
        self._update_interval = update_interval_seconds
        
        self._update_internal_data() 

        self._active = True
        self.update_thread = threading.Thread(target=self._threaded_update_loop, daemon=True)
        self.update_thread.start()

    def _generate_new_snapshot_data(self):
        current_time = datetime.now()
        try:
            num_cores = psutil.cpu_count(logical=True)
            # A contagem de threads e processos pode ser simulada ou obtida de psutil
            # Para manter a simulação mais controlada, vamos usar valores aleatórios aqui,
            # mas psutil ainda é útil para num_cores.
            thread_count_val = random.randint(num_cores * 20, num_cores * 150)
            process_count_val = random.randint(num_cores * 10, num_cores * 50)
        except psutil.Error as e:
            print(f"Erro ao acessar dados do psutil no simulador: {e}")
            num_cores = 4 # Fallback
            thread_count_val = random.randint(100,1000)
            process_count_val = random.randint(50,200)

        cpu_total_percent = round(random.uniform(5, 95), 2)
        # Garante que cpu_idle_percent seja o complemento de cpu_total_percent (com uma pequena variação)
        cpu_idle_percent = round(max(0.0, 100.0 - cpu_total_percent - random.uniform(0, 2.5)), 2)

        cpu_data = {
            'cpu_total_percent': cpu_total_percent,
            'cpu_idle_percent': cpu_idle_percent, # Total CPU Ocioso
            'cpu_count': num_cores,
            'thread_count': thread_count_val,
            'process_count': process_count_val,
            'per_cpu_percent': [round(random.uniform(0, 100), 2) for _ in range(num_cores)]
        }

        total_mem_mb = 8 * 1024  # Simulando 8GB
        used_mem_mb = random.randint(int(total_mem_mb * 0.25), int(total_mem_mb * 0.9))
        free_mem_mb = total_mem_mb - used_mem_mb
        cache_max_possible = min(free_mem_mb, int(total_mem_mb * 0.5))
        cache_mem_mb = random.randint(0, cache_max_possible if cache_max_possible > 0 else 0)
        
        swap_total_mb = 4096 # Simulando 4GB de swap
        swap_used_mb = random.randint(0, int(swap_total_mb * 0.25)) # Swap usado até 25% do total
        swap_free_mb = swap_total_mb - swap_used_mb # Swap Livre
        # Swap Cache: uma pequena porção do swap total ou usado, simulado
        swap_cached_mb = random.randint(0, int(min(swap_used_mb * 0.15, swap_total_mb * 0.05))) 

        memory_data = {
            'total_memory_mb': total_mem_mb,
            'used_memory_mb': used_mem_mb,
            'free_memory_mb': free_mem_mb,
            'memory_used_percent': round((used_mem_mb / total_mem_mb) * 100, 2),
            'cache_memory_mb': cache_mem_mb,
            'swap_total_mb': swap_total_mb,
            'swap_used_mb': swap_used_mb,
            'swap_free_mb': swap_free_mb,      # Novo
            'swap_cached_mb': swap_cached_mb,  # Novo
        }

        processes = []
        possible_uids = [0, 1000, 1001, 99] + [random.randint(100, 200) for _ in range(3)] + [random.randint(2000,5000) for _ in range(5)]
        for _ in range(process_count_val): # Número de processos consistente com process_count_val
            pid = random.randint(1000, 99999)
            memory = random.randint(1, 500) 
            cpu = round(random.uniform(0.0, 15.0), 2)
            processes.append({
                'pid': pid,
                'name': f"process_{uuid.uuid4().hex[:6]}",
                'uid': random.choice(possible_uids), # Alterado de 'user' para 'uid'
                'cpu_percent': cpu,
                'memory_usage_mb': memory,
                'priority': random.choice(['Alta', 'Normal', 'Baixa', str(random.randint(-20, 19))]),
                'state': random.choice(['Executando', 'Dormindo', 'Zombie', 'Parado', 'Inativo']),
            })
        
        return {
            'timestamp': current_time.isoformat(),
            'cpu': cpu_data,
            'memory': memory_data,
            'processes': processes
        }

    def _update_internal_data(self):
        new_data = self._generate_new_snapshot_data()
        with self._lock:
            self._current_snapshot = new_data

    def _threaded_update_loop(self):
        while self._active:
            self._update_internal_data()
            time.sleep(self._update_interval)

    def get_full_snapshot(self):
        with self._lock:
            return self._current_snapshot.copy() if self._current_snapshot else {}

    def stop_updates(self):
        self._active = False
        if self.update_thread.is_alive():
            self.update_thread.join(timeout=max(1.0, self._update_interval / 2.0))