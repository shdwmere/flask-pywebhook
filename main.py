from flask import Flask, render_template, request, requests
from datetime import datetime
import random, json

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
    
    # geradores
    onze_chars = random.randint(11111111111, 99999999999)
    doze_chars = random.randint(111111111111, 999999999999)
    id_gerado = '#' + str(onze_chars)
    codigo_gerado = 'BR' + str(doze_chars)

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Logs handling
    nome = dados_evento.get('data', {}).get('customer', {}).get('name')
    cpf = dados_evento.get('data', {}).get('customer', {}).get('document', {}).get('number')
    email = dados_evento.get('data', {}).get('customer', {}).get('email')
    status_pagamento = dados_evento.get('data', {}).get('status')
    data_registro_unformatted = dados_evento.get('data', {}).get('createdAt')
    # fomatando a data de registro
    data_obj = datetime.strptime(data_registro_unformatted, '%Y-%m-%dT%H:%M:%S.%fZ')
    data_registro_formatada = data_obj.strftime('%Y-%m-%d')

    # passando horario do evento para logs
    momento_evento = data_registro_formatada
    logs.append({
        'momento_evento': momento_evento,
        'nome': nome,
        'cpf': cpf,
        'email': email,
        'status_pagamento': status_pagamento
    })
    # End Logs handling

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=

    # API Logic Handle
    uri = "https://djamba-production.up.railway.app/api/pedidos/create/"

    payload_cliente = {
    "id_pedido": id_gerado,
    "codigo_rastreio": codigo_gerado,
    "cpf_cliente": cpf,
    "nome_cliente": nome,
    "email_cliente": email,
    "data_registro": momento_evento,
    }
    # converte os dados em formato JSON
    corpo_json = json.dumps(payload_cliente)

    headers = {"Content-Type": "application/json"}

    if status_pagamento == 'paid':
        try:
            resultado = requests.post(url=uri, data=corpo_json, headers=headers)
            resultado.raise_for_status()  # Lança uma exceção se o status da resposta não for 2xx

            resposta = resultado.json()
            print(f"Dados enviados com sucesso: {resposta}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao fazer a solicitação: {e}")
        except ValueError as e:
            print(f"Erro ao analisar a resposta JSON: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")
    elif status_pagamento == 'waiting_payment':
        print("Pagamento pendente.")
    else:
        print("Pagamento recusado.")
    # End API Logic Handle

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Mailing Handle
    # //
    # End Mailing Handle

    # Responder com status code OK
    return '', 200

# Captura de logs
@app.route('/logs')
def show_logs():
    return render_template('logs.html', logs=logs, current_time=datetime.now())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)