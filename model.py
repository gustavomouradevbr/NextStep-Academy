import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

# 1. Carregar a base de dados
df = pd.read_csv('instances/estudantes.csv')

# 2. Multiplicar os dados temporariamente (caso ainda esteja usando a base curta de 6 linhas)
df = pd.concat([df]*10, ignore_index=True)

# 3. Separar as variáveis explicativas (X) da variável alvo (y)
# Ao usar o 'drop', a variável X fica com exatamente as 5 colunas enviadas pelo formulário
X = df.drop('risco_evasao', axis=1)
y = df['risco_evasao']

# 4. Treinar o modelo correto (Random Forest)
modelo_final = RandomForestClassifier(random_state=42)
modelo_final.fit(X, y)

# 5. Salvar o modelo sobrescrevendo o arquivo problemático
os.makedirs('models', exist_ok=True)
with open('models/modelo_evasao.pkl', 'wb') as f:
    pickle.dump(modelo_final, f)

print("✅ Modelo corrigido e treinado com 5 variáveis! Salvo em models/modelo_evasao.pkl")