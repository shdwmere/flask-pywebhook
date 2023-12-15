import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config

def email_confirmar_pagamento(email, nome, id_gerado):    
    
    # Mail Config
    host_smtp = 'smtp.hostinger.com'
    remetente = config('HOST_MAIL')
    password = config('PASSPHRASE')

    destinatario = email
    assunto = 'Recebemos o seu pedido'
    mensagem_html = f'<html><body><h1>Pedido confirmado!</h1> <p>Prezado {nome}, recebemos o seu pedido <b>ID: {id_gerado}</b>.</p> <p>Pedimos para que aguarde o prazo de 72h que enviaremos o código de rastreio de sua encomenda.</p> <p>Agradecemos a preferência, Equipe Mercado Livre.</p></body></html>'

    try:
        print(f"\033[1;32m\n[+] Módulo de Confirmação de Pagamento carregando...\n\033[0m")
        print(f"\033[0;35m Conectando ao servidor SMTP: '{host_smtp}'... \033[0m")
        server = smtplib.SMTP_SSL(host_smtp, port=465)

        print(f"\033[0;35m Logando no e-mail: '{remetente}'... \033[0m")
        server.login(remetente, password)

        print(f"\033[0;33m Carregando template HTML... \033[0m")
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