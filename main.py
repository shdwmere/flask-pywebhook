from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

logs = []

# Rota index
@app.route('/')
def index():
    return render_template('index.html')

# Rota para receber eventos do gateway de pagamento
@app.route('/webhook', methods=['POST'])
def webhook_listener():
    # Capturando dados do evento recebido.
    dados_evento = request.get_json()

    # Logic Handle



    # End Logic Handle
    
    # Logs handling
    nome = dados_evento.get('data', {}).get('customer', {}).get('name')
    cpf = dados_evento.get('data', {}).get('customer', {}).get('document', {}).get('number')
    email = dados_evento.get('data', {}).get('customer', {}).get('email')
    status_pagamento = dados_evento.get('data', {}).get('status')

    # passando horario do evento para logs
    momento_evento = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    logs.append({
        'momento_evento': momento_evento,
        'nome': nome,
        'cpf': cpf,
        'email': email,
        'status_pagamento': status_pagamento
    })
    # Responder com status code OK
    return '', 200

# Captura de logs
@app.route('/logs')
def show_logs():
    return render_template('logs.html', logs=logs, current_time=datetime.now())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
