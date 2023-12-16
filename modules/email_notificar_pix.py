import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config

def email_notificar_pix(email, nome, nome_loja, pix_code):    
    
    # Mail Config
    host_smtp = 'smtp.hostinger.com'
    remetente = config('HOST_MAIL')
    password = config('PASSPHRASE')

    with open('./templates/mail/pix.html', 'r') as file:
        html_template = file.read()

    destinatario = email
    assunto = f'{nome_loja} - Pague seu produto com PIX!'
    mensagem_html = html_template.format(nome=nome, pix_code=pix_code, nome_loja=nome_loja)
    
    try:
        print(f"\033[1;32m \n[+] Módulo de Notificação PIX carregando...\n\033[0m")
        server = smtplib.SMTP_SSL(host_smtp, port=465)
        server.login(remetente, password)
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(mensagem_html, 'html'))

        server.sendmail(remetente, destinatario, msg.as_string())

        print(f'\033[1;32m E-mail com codigo PIX enviado. \033[0m')
        server.quit()
    except smtplib.SMTPException as e:
        print(f'\033[1;31m Falha ao enviar o e-mail: {str(e)} \033[0m')
    except Exception as e:
        print(f'Erro inesperado: {str(e)}')