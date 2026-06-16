import pickle
import numpy as np

# Tenta carregar o modelo. Caso não exista, evita quebrar o app ao iniciar
try:
    model = pickle.load(open('models/modelo_evasao.pkl', 'rb'))
except FileNotFoundError:
    model = None

def classificar_estudante(frequencia, media_notas, renda_familiar, idade, historico_repetencia):

    if model is None:
        return "Erro: Modelo não treinado. Execute model.py primeiro.", [0, 0]

    caracteristicas = np.array([
        [frequencia, media_notas, renda_familiar, idade, historico_repetencia]
    ])

    predicao = model.predict(caracteristicas)
    probabilidades = model.predict_proba(caracteristicas)[0]
    
    prob_estavel = round(probabilidades[0] * 100, 2)
    prob_risco = round(probabilidades[1] * 100, 2)

    mapeamento = {
        0: 'Aluno Estável',
        1: 'Alerta: Alto Risco de Evasão'
    }

    return mapeamento.get(predicao[0]), [prob_estavel, prob_risco]