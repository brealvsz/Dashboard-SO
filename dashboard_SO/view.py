
import sys

def exibir(lista_processos, memoria, uso_cpu_global, uso_memoria, tempo_ocioso_global, total_processos, total_threads, uso_cpu_por_nucleo):
    print("\033[H\033[J", end='')
    
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║                           DASHBOARD DO SISTEMA                          ║")
    print("╠═══════════════════════════════════════════════════════════════════════╣")
    print(f"║ Memória Total: {memoria.get('MemTotal', 0):<15} kB                                    ║")
    print(f"║ Memória Livre: {memoria.get('MemFree', 0):<15} kB                                    ║")
    print(f"║ Memória Cache: {memoria.get('Cached', 0):<15} kB                                    ║")
    print("╠═══════════════════════════════════════════════════════════════════════╣")
    print(f"║ Swap Total   : {memoria.get('SwapTotal', 0):<15} kB                                    ║")
    print(f"║ Swap Livre   : {memoria.get('SwapFree', 0):<15} kB                                    ║")
    print(f"║ Swap Cache   : {memoria.get('SwapCached', 0):<15} kB                                    ║")
    
    swap_total = memoria.get('SwapTotal', 0)
    swap_livre = memoria.get('SwapFree', 0)
    uso_swap_percentual = 0.0
    if swap_total > 0:
        uso_swap_percentual = round(100 * (swap_total - swap_livre) / swap_total, 2)
    print(f"║ Uso do Swap  : {uso_swap_percentual:<8}%                                               ║")

    print("╠═══════════════════════════════════════════════════════════════════════╣")
    print(f"║ Uso da CPU    : {uso_cpu_global:<6}%             Tempo Ocioso: {tempo_ocioso_global:<6}%          ║")
    print(f"║ Total Processos: {total_processos:<5}           Total Threads: {total_threads:<5}           ║")
    print(f"║ Uso de Memória: {uso_memoria:<8}%                                                    ║")
    
    print("╠═══════════════════════════════════════════════════════════════════════╣")
    print("║                         Uso da CPU por Núcleo                           ║")
    print("╠═══════════════════════════════════════════════════════════════════════╣")
    
    nucleos_ordenados = sorted([k for k in uso_cpu_por_nucleo.keys() if k != 'cpu'])
    num_nucleos = len(nucleos_ordenados)
    if num_nucleos > 0:
        for i in range(0, num_nucleos, 2):
            nuc1 = nucleos_ordenados[i]
            uso1 = uso_cpu_por_nucleo.get(nuc1, 0.0)
            
            nuc2 = ""
            uso2 = 0.0
            if i + 1 < num_nucleos:
                nuc2 = nucleos_ordenados[i+1]
                uso2 = uso_cpu_por_nucleo.get(nuc2, 0.0)

            if nuc2:
                print(f"║ {nuc1.upper()}: {uso1:<5}%             {nuc2.upper()}: {uso2:<5}%               ║")
            else:
                print(f"║ {nuc1.upper()}: {uso1:<5}%                                                       ║")
    else:
        print("║ Nenhuma informação de uso por núcleo disponível.                          ║")
    print("╠═══════════════════════════════════════════════════════════════════════╣")

    print("╠════════╦═════════════════╦══════╦════════╦══════╦═══════╦═══════╦═══════╣")
    print("║ PID    ║ Nome            ║Estado║ Mem(kB)║ UID  ║Threads║ CPU (%)║ Prior.║")
    print("╠════════╬═════════════════╬══════╬════════╬══════╬═══════╬═══════╬═══════╣")
    
    for p in lista_processos:
        uid_str = str(p.uid) if p.uid != -1 else "N/A"
        threads_str = str(p.threads)
        cpu_percentual_str = f"{p.cpu_percentual:.2f}"
        prioridade_str = str(p.prioridade)

        print(f"║ {p.pid:<6} ║ {p.nome[:15]:<15} ║ {p.estado[:4]:<4} ║ {p.memoria_kb:<6} ║ {uid_str:<4} ║ {threads_str:<5} ║ {cpu_percentual_str:<6} ║ {prioridade_str:<5} ║", end='')        
        print("\033[K")
    
    print("╚════════╩═════════════════╩══════╩════════╩══════╩═══════╩═══════╩═══════╝")
    sys.stdout.flush()