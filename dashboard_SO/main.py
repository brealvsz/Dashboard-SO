# main.py
from controller import Controller
from view_grafica import DashboardApp 
from model import sistema # Precisamos importar sistema aqui para obter o número de núcleos

def main():
    # Obtém o número de núcleos do sistema usando seu módulo 'sistema'.
    # Isso é feito aqui no 'Main' para que a View possa inicializar suas barras de CPU
    # com o número correto de elementos.
    numero_nucleos_cpu = sistema.obter_numero_nucleos_cpu() 

    # Cria a instância da View (DashboardApp), passando o número de núcleos.
    # A View não deve mais obter essas informações por conta própria.
    app_view = DashboardApp(num_cpu_cores_param=numero_nucleos_cpu)

    # Cria a instância do Controller, passando a instância da View.
    # O Controller agora tem a referência para a interface gráfica que ele deve atualizar.
    dashboard_controller = Controller(view_instance=app_view)
    
    # Inicia o monitoramento de dados através do Controller.
    # O Controller iniciará sua própria thread de atualização.
    dashboard_controller.iniciar_monitoramento()
    
    # Inicia o loop principal do CustomTkinter.
    # Isso mantém a janela da aplicação aberta e responsiva a eventos.
    app_view.mainloop()

if __name__ == '__main__':
    main()