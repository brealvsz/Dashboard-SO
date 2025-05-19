import os

def exibir(processos, memoria, uso_memoria, uso_cpu, tempo_ocioso, total_proc, total_threads):
    os.system('clear') 
    print("=== DASHBOARD DO SISTEMA ===\n")
    print(f"Memória Total: {memoria.get('MemTotal', 0)} kB")
    print(f"Memória Livre: {memoria.get('MemFree', 0)} kB\n")
    print(f"Uso da CPU         : {uso_cpu}%")
    print(f"Tempo Ocioso       : {tempo_ocioso}%")
    print(f"Total de Processos : {total_proc}")
    print(f"Total de Threads   : {total_threads}")
    print(f"Uso de Memória     : {uso_memoria}%\n")
    print("PID\tNome\t\tEstado\t\tMem(kB)\tThreads")
    for p in processos[:10]: 
        print(f"{p.pid}\t{p.name[:10]}\t{p.estado}\t{p.memoriaKB}\t{p.threads}")
