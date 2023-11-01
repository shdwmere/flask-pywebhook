from flask import Flask, render_template

app = Flask(__name__)

# Rota index
@app.route('/')
def index():
    return render_template('./test.html')

# Rota para receber eventos do gateway de pagamento
@app.route('/webhook', methods=['POST'])
def webhook_listener():
    # Capturando dados enviados no webhook
    data = request.get_json()

    # Processamento dos dados recebidos (apenas imprimir por enquanto)
    print("Evento capturado:")
    print(data)

    # Aqui você pode adicionar a lógica para processar os eventos do gateway de pagamento. Por exemplo, atualizar um banco de dados, enviar notificações, etc.

    # Responder ao gateway de pagamento indicando que o evento foi recebido com sucesso (código 200)
    return '', 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
