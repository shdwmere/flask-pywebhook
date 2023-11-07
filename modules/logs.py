from datetime import datetime
import pytz

logs = []

def obter_data_atual_brasilia():
    fuso_horario_brasilia = pytz.timezone('America/Sao_Paulo')
    data_brasilia = datetime.now(fuso_horario_brasilia)
    data_brasilia_formatada = data_brasilia.strftime('%Y-%m-%d')
    return data_brasilia_formatada


def filtrar_logs_por_data(logs, data):
    logs_filtrados = []

    if data:  # Verifica se há alguma data selecionada
        data_filtrada = datetime.strptime(data, '%Y-%m-%d')
    else:
        # Se nenhum valor for selecionado, usa a data atual de Brasília
        data_filtrada = datetime.now()

    for log in logs:
        data_logs = datetime.strptime(log['data_logs'], '%d/%m/%Y').date()

        if data_logs == data_filtrada.date():  # Garante que ambas são comparadas como objetos de data
            logs_filtrados.append(log)

    return logs_filtrados


# Função para calcular o total das vendas com status 'paid'
def calcular_total_vendas(logs):
    total = 0
    for log in logs:
        if log['status_pagamento'] == 'paid':
            preco = float(log['preco'].replace(',', '.'))  # convertendo o preço formatado (ex: "139.90") para float
            total += preco
    return "{:.2f}".format(total)  # formatando o total como uma string de valor monetário (ex: "139.90")