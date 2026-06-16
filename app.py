from flask import Flask, request, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio

from classifier import classificar_estudante

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        frequencia = float(request.form.get("frequencia"))
        media_notas = float(request.form.get("media_notas"))
        renda_familiar = int(request.form.get("renda_familiar"))
        idade = int(request.form.get("idade"))
        historico_repetencia = int(request.form.get("historico_repetencia"))

        resultado, probabilidades = classificar_estudante(
            frequencia,
            media_notas,
            renda_familiar,
            idade,
            historico_repetencia
        )

        # Criar DataFrame com as probabilidades da predição e gerar o gráfico de pizza com Plotly
        dados = pd.DataFrame({
            'Status do Aluno': ['Estáveis', 'Em Risco de Evasão'],
            'Quantidade': probabilidades
        })

        figura = px.pie(dados, values='Quantidade', names='Status do Aluno', title='Probabilidade de Risco do Aluno')
        figura.update_traces(marker=dict(colors=['#2ecc71', '#e74c3c']))
        grafico = pio.to_html(figura, full_html=False)

        return render_template(
            'index.html',
            predicao=resultado,
            grafico=grafico
        )

    return render_template('index.html', predicao=None, grafico=None)

if __name__ == "__main__":
    app.run(debug=True)