from flask import Flask, render_template, jsonify, request
import os
from models import db, Eventos
from dotenv import load_dotenv
import requests
import pytz
import random, json
from datetime import datetime
from colorama import init, Fore
from modules.logs import logs, calcular_total_vendas, filtrar_logs_por_data
# e-mail modules
from modules.email_confirmar_pagamento import email_confirmar_pagamento
from modules.email_notificar_pix import email_notificar_pix
from modules.email_refused import email_notificar_refused

load_dotenv()
nome_loja = 'Loja Shoppe'

# Obtendo o fuso horário de Brasília
fuso_horario_brasilia = pytz.timezone('America/Sao_Paulo')
data_brasilia = datetime.now(fuso_horario_brasilia)
data_brasilia_formatada = data_brasilia.strftime('%Y-%m-%d')

# importante
momento_evento = data_brasilia_formatada
hora_evento = data_brasilia.strftime('%H:%M:%S')
data_logs = data_brasilia.strftime('%d/%m/%Y')




init(autoreset=True)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    db.init_app(app)

    with app.app_context():
        db.create_all()

        # Fetch events from the database
        events = Eventos.query.all()

        # Convert events to logs and add them to the existing logs
        for event in events:
            logs.append({
                'data_logs': data_logs,
                'hora_evento': hora_evento,
                'nome': event.nome_cliente,
                'status_pagamento': event.status_pagamento,
                'preco': event.preco_produto
            })

    return app

app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook_listener():

    # Capturando dados do evento recebido.
    dados_evento = request.get_json()

    status_pagamento = dados_evento.get('status')

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=

    # data scraping
    nome = dados_evento.get('data', {}).get('customer', {}).get('name', 'Nome não encontrado')
    nome_split = nome.split()[0]
    cpf = dados_evento.get('data', {}).get('customer', {}).get('document', {}).get('number', 'CPF não encontrado')
    email = dados_evento.get('data', {}).get('customer', {}).get('email', 'Email não encontrado')
    status_pagamento = dados_evento.get('data', {}).get('status', 'Status não encontrado')
    preco_total = dados_evento.get('data', {}).get('amount', 'Preço total não encontrado')  # Considerando 'amount' como o total a ser pago
    preco_formatado = "{:.2f}".format(float(preco_total) / 100)  # Convertendo centavos para reais
    pix_data = dados_evento.get('data', {}).get('pix')
    pix_code = pix_data.get('qrcode', 'Código PIX não encontrado') if pix_data else 'Código PIX não encontrado'
    payment_method = dados_evento.get('data', {}).get('paymentMethod', 'Método de pagamento não encontrado')
           
    #log handling
    logs.append({
        'data_logs': data_logs,
        'hora_evento': hora_evento,
        'nome': nome_split,
        'status_pagamento': status_pagamento,
        'preco': preco_formatado
    })

    data_hora_evento = f'[{data_logs} - {hora_evento}]'

    def imprimir_dados_evento():
        print(f'{Fore.YELLOW}-' * 12)
        print(data_hora_evento)

        print(f'{Fore.GREEN}[+]{Fore.WHITE} Nome do cliente: {Fore.YELLOW}{nome_split}')
        print(f'{Fore.GREEN}[+]{Fore.WHITE} Preco do produto: {Fore.YELLOW}{preco_formatado}')
        print(f'{Fore.GREEN}[+]{Fore.WHITE} Método de pagamento: {Fore.YELLOW}{payment_method}')
        print(f'{Fore.GREEN}[+]{Fore.WHITE} Status do pagamento: {Fore.YELLOW}{status_pagamento}')
        print(f'{Fore.YELLOW}-' * 12)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=

    # geradores
    onze_chars = random.randint(11111111111, 99999999999)
    doze_chars = random.randint(111111111111, 999999999999)
    id_gerado = '#' + str(onze_chars)
    codigo_gerado = 'BR' + str(doze_chars)

    # API Logic Handle
    payload_cliente = {
    "id_pedido": id_gerado,
    "codigo_rastreio": codigo_gerado,
    "cpf_cliente": cpf,
    "nome_cliente": nome,
    "email_cliente": email,
    "data_registro": momento_evento,
    }

    payload_evento = {
        "data_compra": data_hora_evento,
        "nome_cliente": nome,
        "nome_loja": nome_loja,
        "preco_produto": preco_formatado,
        "metodo_pagamento": payment_method,
        "status_pagamento": status_pagamento
    }

    
    def send_to_djambadb(payload_cliente):
        djamba_create_endpoint = "https://djamba-production.up.railway.app/api/pedidos/create/"
        headers = {"Content-Type": "application/json"}
        corpo_json = json.dumps(payload_cliente)

        try:
            resultado = requests.post(url=djamba_create_endpoint, data=corpo_json, headers=headers)
            resultado.raise_for_status()  # Raises an exception if the response status is not 2xx
            resposta = resultado.json()  # Converts the response to JSON
            print(f'{Fore.GREEN}[+] DjambaDB - Pedido registrado com sucesso!')
        except requests.exceptions.RequestException as e:
            print(f"Erro ao fazer a solicitação: {e}")
        except ValueError as e:
            print(f"Erro ao analisar a resposta JSON: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")

    def send_to_eventsdb(payload_evento):
        save_event_endpoint = "https://flask-production-82d2.up.railway.app/armazenar_evento"
        headers = {"Content-Type": "application/json"}
        corpo_json = json.dumps(payload_evento)

        try:
            resultado = requests.post(url=save_event_endpoint, data=corpo_json, headers=headers)
            resultado.raise_for_status()  # Raises an exception if the response status is not 2xx
            print(f'{Fore.GREEN}[+] Evento armazenado com sucesso!')
        except requests.exceptions.RequestException as e:
            print(f"Erro ao fazer a solicitação: {e}")
        except ValueError as e:
            print(f"Erro ao analisar a resposta JSON: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")

    # handling purcharses logicc
    if status_pagamento == 'paid':
        print('\n')
        print(f"{Fore.GREEN}[+] Pagamento aprovado.")
        imprimir_dados_evento()
        send_to_djambadb(payload_cliente)
        send_to_eventsdb(payload_evento)
        email_confirmar_pagamento(email=email, nome=nome, nome_loja=nome_loja, id_gerado=id_gerado)
        print('\n')

    elif status_pagamento == 'waiting_payment':
        print('\n')
        print(f"{Fore.YELLOW}[*] Pagamento pendente.")
        imprimir_dados_evento()
        print('\n')

        # checa se o pagamento é via PIX e dispara um e-mail de notificação com o código
        if payment_method == 'pix':
            print(f"{Fore.YELLOW}[+] Pagamento via PIX identificado.")
            email_notificar_pix(email=email, nome=nome, nome_loja=nome_loja, pix_code=pix_code)

    else:
        print('\n')
        print(f"{Fore.RED}[-] Pagamento recusado.")
        imprimir_dados_evento()
        email_notificar_refused(email=email, nome=nome, nome_loja=nome_loja)
        print('\n')
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

    # Render the template with the logs and total sales
    return render_template('logs.html', logs=logs, total_vendas=total_vendas)

@app.route('/armazenar_evento', methods=['POST'])
def armazenar_evento():
    dados_evento = request.get_json()

    nome = dados_evento.get('data', {}).get('customer', {}).get('name', 'Nome não encontrado')
    nome_split = nome.split()[0]
    preco_total = str(dados_evento.get('data', {}).get('amount', 'Preço total não encontrado'))
    data_br_string = str(data_logs)
    payment_method = dados_evento.get('data', {}).get('paymentMethod', 'Método de pagamento não encontrado')
    status_pagamento = dados_evento.get('data', {}).get('status', 'Status não encontrado')

    new_evento = Eventos (
        data_compra=data_br_string,
        nome_cliente=nome_split,
        nome_loja=nome_loja,
        preco_produto=preco_total,
        metodo_pagamento=payment_method,
        status_pagamento=status_pagamento
        )

    db.session.add(new_evento)
    db.session.commit()
    return jsonify({'message': 'Evento armazenado com sucesso!'}), 201

# execution
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)