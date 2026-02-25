from pyarchinit_mini.web_interface.app import create_app

app, socketio = create_app()

if __name__ == "__main__":
    socketio.run(app)
