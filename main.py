from dashboard import DashboardApp 
if __name__ == "__main__":
    app = DashboardApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        print("Aplicação interrompida pelo usuário.")
        # Assegura que on_closing é chamado se a app já existir e o método estiver disponível
        if hasattr(app, 'on_closing') and callable(app.on_closing):
            app.on_closing()
    except Exception as e:
        print(f"Um erro fatal ocorreu na aplicação: {e}")
        if hasattr(app, 'on_closing') and callable(app.on_closing):
            app.on_closing()