from controller import Controller
import view as dashboard

def main():
    monitor = Controller(view=dashboard)
    monitor.iniciar_monitoramento()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")

if __name__ == '__main__':
    main()
