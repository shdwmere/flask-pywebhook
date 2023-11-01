from flask import Flask, render_template, request

app = Flask(__name__)

logs = []

# Rota index
@app.route('/')
def index():
    return render_template('index.html')

# Rota para receber eventos do gateway de pagamento
@app.route('/webhook', methods=['POST'])
def webhook_listener():
    # Capturando dados enviados no webhook
    data = request.get_json()

    # Capturando dados recebidos e jogando para um template logs
    logs.append("Evento capturado:")
    logs.append(str(data))

    # Aqui você pode adicionar a lógica para processar os eventos do gateway de pagamento. Por exemplo, atualizar um banco de dados, enviar notificações, etc.

    # Responder ao gateway de pagamento indicando que o evento foi recebido com sucesso (código 200)
    return '', 200

@app.route('/logs')
def show_logs():
    return render_template('logs.html', logs=logs)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
