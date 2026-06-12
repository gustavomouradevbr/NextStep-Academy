import pickle
import numpy as np

# Tenta carregar o modelo. Caso não exista, evita quebrar o app ao iniciar
try:
    model = pickle.load(open('models/modelo_evasao.pkl', 'rb'))
except FileNotFoundError:
    model = None

def classificar_estudante(frequencia, media_notas, renda_familiar, idade, historico_repetencia):

    if model is None:
        return "Erro: Modelo não treinado. Execute model.py primeiro."

    caracteristicas = np.array([
        [frequencia, media_notas, renda_familiar, idade, historico_repetencia]
    ])

    predicao = model.predict(caracteristicas)

    mapeamento = {
        0: 'Aluno Estável',
        1: 'Alerta: Alto Risco de Evasão'
    }

    return mapeamento.get(predicao[0])