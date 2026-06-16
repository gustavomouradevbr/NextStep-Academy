from flask import Flask, request, render_template, Response
import pandas as pd
import plotly.express as px
import plotly.io as pio
import sqlite3

from classifier import classificar_estudante

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            frequencia REAL,
            media REAL,
            renda INTEGER,
            idade INTEGER,
            repetencia INTEGER,
            resultado_texto TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=['GET', 'POST'])
def index():
    grafico = None
    resultado = None

    if request.method == 'POST':
        frequencia = float(request.form.get("frequencia"))
        media_notas = float(request.form.get("media_notas"))
        renda_familiar = int(request.form.get("renda_familiar"))
        idade = int(request.form.get("idade"))
        historico_repetencia = int(request.form.get("historico_repetencia"))

        resultado, importancias = classificar_estudante(
            frequencia, media_notas, renda_familiar, idade, historico_repetencia
        )

        # Inserir no histórico do SQLite
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO historico (frequencia, media, renda, idade, repetencia, resultado_texto)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (frequencia, media_notas, renda_familiar, idade, historico_repetencia, resultado))
        conn.commit()
        conn.close()

        # Gráfico de Importância das Variáveis (Barras Horizontais)
        if importancias:
            df_imp = pd.DataFrame(list(importancias.items()), columns=['Variável', 'Impacto'])
            df_imp = df_imp.sort_values('Impacto', ascending=True)
            figura = px.bar(df_imp, x='Impacto', y='Variável', orientation='h', title='Importância de cada Fator no Resultado')
            figura.update_traces(marker_color='#3498db')
            grafico = pio.to_html(figura, full_html=False)

        return render_template('index.html', predicao=resultado, grafico=grafico)

    return render_template('index.html', predicao=None, grafico=None)

@app.route("/dashboard")
def dashboard():
    try:
        df = pd.read_csv('estudantes.csv')
    except FileNotFoundError:
        # Fallback de segurança para o banco caso o CSV não exista ainda
        conn = sqlite3.connect('banco.db')
        df = pd.read_sql_query("SELECT * FROM historico", conn)
        conn.close()

    grafico_dispersao = ""
    grafico_hist = ""

    if not df.empty:
        col_idade = 'idade' if 'idade' in df.columns else df.columns[4] if len(df.columns) > 4 else df.columns[0]
        col_freq = 'frequencia' if 'frequencia' in df.columns else df.columns[1] if len(df.columns) > 1 else df.columns[0]
        col_renda = 'renda' if 'renda' in df.columns else df.columns[3] if len(df.columns) > 3 else df.columns[0]

        fig1 = px.scatter(df, x=col_idade, y=col_freq, title="Dispersão: Idade vs Frequência Escolar", color_discrete_sequence=['#e74c3c'])
        grafico_dispersao = pio.to_html(fig1, full_html=False)

        fig2 = px.histogram(df, x=col_renda, title="Distribuição da Renda Familiar", color_discrete_sequence=['#2ecc71'])
        grafico_hist = pio.to_html(fig2, full_html=False)

    return render_template('dashboard.html', grafico_dispersao=grafico_dispersao, grafico_hist=grafico_hist)

@app.route("/dados")
def dados():
    conn = sqlite3.connect('banco.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM historico ORDER BY id DESC')
    registros = cursor.fetchall()
    conn.close()
    return render_template('dados.html', registros=registros)

@app.route("/exportar")
def exportar():
    conn = sqlite3.connect('banco.db')
    df = pd.read_sql_query("SELECT * FROM historico", conn)
    conn.close()
    return Response(
        df.to_csv(index=False),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=historico_evasao.csv"}
    )

if __name__ == "__main__":
    app.run(debug=True)