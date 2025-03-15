import os
import logging
from flask import Flask
from dotenv import load_dotenv
from routes.main_routes import main_bp

# Carrega as variáveis de ambiente
load_dotenv()

# Configura o logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.info("Aplicação iniciada com logging configurado.")

def create_app():
    app = Flask(__name__, static_folder='static')
    
    # Registra o blueprint de rotas
    app.register_blueprint(main_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
    
#######################################################
