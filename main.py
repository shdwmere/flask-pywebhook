from flask import Flask, render_template, request
import requests
from datetime import datetime
import random, json
from logs import logs, calcular_total_vendas, filtrar_logs_por_data
from essential_vars import data_logs, hora_evento, momento_evento
from email_service import send_mail_if_paid

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook_listener():

    # Capturando dados do evento recebido.
    dados_evento = request.get_json()
    
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=

    # data scraping
    nome = dados_evento.get('data', {}).get('customer', {}).get('name')
    nome_split = nome.split()[0]
    cpf = dados_evento.get('data', {}).get('customer', {}).get('document', {}).get('number')
    email = dados_evento.get('data', {}).get('customer', {}).get('email')
    status_pagamento = dados_evento.get('data', {}).get('status')
    preco_total = dados_evento.get('data', {}).get('amount')
    preco_formatado = "{:.2f}".format(float(preco_total) / 100)


    # log handling
    logs.append({
        'data_logs': data_logs,
        'hora_evento': hora_evento,
        'nome': nome_split,
        'status_pagamento': status_pagamento,
        'preco': preco_formatado
    })

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=

    # geradores
    onze_chars = random.randint(11111111111, 99999999999)
    doze_chars = random.randint(111111111111, 999999999999)
    id_gerado = '#' + str(onze_chars)
    codigo_gerado = 'BR' + str(doze_chars)

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

    # definindo Header da requisicao
    headers = {"Content-Type": "application/json"}

    # handling purcharses logic
    if status_pagamento == 'paid':
        try:
            resultado = requests.post(url=uri, data=corpo_json, headers=headers)
            resultado.raise_for_status()  # Lança uma exceção se o status da resposta não for 2xx

            resposta = resultado.json()
            print('Pagamento identificado com sucesso!')
            print(f"\033[1;32m Dados enviados com sucesso: \033[0;36m{resposta}\033[0m \033[0m")
            send_mail_if_paid(email=email, nome=nome, id_gerado=id_gerado)
        except requests.exceptions.RequestException as e:
            print(f"Erro ao fazer a solicitação: {e}")
        except ValueError as e:
            print(f"Erro ao analisar a resposta JSON: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")
    elif status_pagamento == 'waiting_payment':
        print("Pagamento pendente.")
        #print(dados_evento)
    else:
        print("Pagamento recusado.")
    # End API Logic Handle

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Responder requisicoes com status code OK
    return '', 200


@app.route('/filtro_data', methods=['GET'])
def filtro_data():
    data_selecionada = request.args.get('data_filtrada')
    # Lógica para filtrar os registros de log pela data selecionada
    logs_filtrados = filtrar_logs_por_data(logs, data_selecionada)

    total_vendas = calcular_total_vendas(logs=logs_filtrados)

    return render_template('logs.html', logs=logs_filtrados, total_vendas=total_vendas)


@app.route('/filtro_status', methods=['GET'])
def filtro_status():
    status_selecionado = request.args.get('status_filtrado')

    logs_filtrados = [log for log in logs if log['status_pagamento'] == status_selecionado]
    logs_nao_filtrados = [log for log in logs if log['status_pagamento'] != status_selecionado]
    logs_ordenados = logs_filtrados + logs_nao_filtrados

    total_vendas = calcular_total_vendas(logs=logs_filtrados)

    return render_template('logs.html', logs=logs_ordenados, total_vendas=total_vendas)


@app.route('/logs')
def show_logs():
    total_vendas = calcular_total_vendas(logs)
    return render_template('logs.html', logs=logs, current_time=datetime.now(), total_vendas=total_vendas)

# execution
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
