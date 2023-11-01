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
    id_pedido = dados_evento.get('id_pedido')
    codigo_rastreio = dados_evento.get('codigo_rastreio')
    cpf = dados_evento.get('cpf')
    nome = dados_evento.get('nome')
    email = dados_evento.get('email')
    data_registro = dados_evento.get('data_registro')
    # passando horario do evento para logs
    momento_evento = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    logs.append({
        # 'momento_evento': momento_evento,
        'dados_evento': dados_evento,
        # 'id_pedido': id_pedido,
        # 'codigo_rastreio': codigo_rastreio,
        # 'cpf': cpf,
        # 'nome': nome,
        # 'email': email,
        # 'data_registro': data_registro
        })

    # Responder com status code OK
    return '', 200

# Captura de logs
@app.route('/logs')
def show_logs():
    return render_template('logs.html', logs=logs, current_time=datetime.now())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
