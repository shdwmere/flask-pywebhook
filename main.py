from flask import Flask, render_template, request
import requests
from datetime import datetime
import random, json
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Logs handling
    nome = dados_evento.get('data', {}).get('customer', {}).get('name')
    cpf = dados_evento.get('data', {}).get('customer', {}).get('document', {}).get('number')
    email = dados_evento.get('data', {}).get('customer', {}).get('email')
    status_pagamento = dados_evento.get('data', {}).get('status')

    # Obtendo o fuso horário de Brasília
    fuso_horario_brasilia = pytz.timezone('America/Sao_Paulo')
    data_brasilia = datetime.now(fuso_horario_brasilia)
    data_brasilia_formatada = data_brasilia.strftime('%Y-%m-%d')
    momento_evento = data_brasilia_formatada


    # passando dados para o template de logs.
    logs.append({
        'momento_evento': momento_evento,
        'nome': nome,
        'cpf': cpf,
        'email': email,
        'status_pagamento': status_pagamento
    })
    # End Logs handling

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
        
    # Mail Config
    host_smtp = 'smtp.hostinger.com'
    remetente = 'contato@lojashopee.shop'
    password = 'o0cbDdFeComm@777'

    destinatario = email
    assunto = 'Recebemos o seu pedido'
    mensagem_html = f'<html><body><h1>Pedido confirmado!</h1> <p>Prezado {nome}, recebemos o seu pedido <b>ID: {id_gerado}</b>.</p> <p>Pedimos para que aguarde o prazo de 72h que enviaremos o código de rastreio de sua encomenda.</p> <p>Agradecemos a preferência, Equipe Shopee.</p></body></html>'


    if status_pagamento == 'paid':
        try:
            print(f"\033[0;35m Conectando ao servidor SMTP: '{host_smtp}'... \033[0m")
            server = smtplib.SMTP_SSL(host_smtp, port=465)

            print(f"\033[0;35m Logando no e-mail: '{remetente}'... \033[0m")
            server.login(remetente, password)

            print(f"\033[0;33m Criando mensagem HTML... \033[0m")
            msg = MIMEMultipart()
            msg['From'] = remetente
            msg['To'] = destinatario
            msg['Subject'] = assunto
            msg.attach(MIMEText(mensagem_html, 'html'))

            print(f"\033[0;36m Enviando o e-mail... \033[0m")
            server.sendmail(remetente, destinatario, msg.as_string())


            print(f'\033[1;32m E-mail enviado com sucesso. \033[0m')
            server.quit()
        except smtplib.SMTPException as e:
            print(f'\033[1;31m Falha ao enviar o e-mail: {str(e)} \033[0m')
        except Exception as e:
            print(f'Erro inesperado: {str(e)}')
    else:
        print('Sem pagamento, sem notificação.')
    
    # End Mailing Handle

    # Responder requisicoes com status code OK
    return '', 200

# Captura de logs
@app.route('/logs')
def show_logs():
    return render_template('logs.html', logs=logs, current_time=datetime.now())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)