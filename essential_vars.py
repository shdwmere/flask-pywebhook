import pytz
from datetime import datetime

# Obtendo o fuso horário de Brasília
fuso_horario_brasilia = pytz.timezone('America/Sao_Paulo')
data_brasilia = datetime.now(fuso_horario_brasilia)
data_brasilia_formatada = data_brasilia.strftime('%Y-%m-%d')

# importante
momento_evento = data_brasilia_formatada
hora_evento = data_brasilia.strftime('%H:%M:%S')
data_logs = data_brasilia.strftime('%d/%m/%Y')