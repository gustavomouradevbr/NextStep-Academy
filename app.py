from flask import Flask, request, render_template, Response
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# Paleta de cores padrão do projeto
CORES = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']

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

        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO historico (frequencia, media, renda, idade, repetencia, resultado_texto)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (frequencia, media_notas, renda_familiar, idade, historico_repetencia, resultado))
        conn.commit()
        conn.close()

        if importancias:
            df_imp = pd.DataFrame(list(importancias.items()), columns=['Variável', 'Impacto'])
            df_imp = df_imp.sort_values('Impacto', ascending=True)
            figura = px.bar(
                df_imp, x='Impacto', y='Variável', orientation='h',
                title='Importância de cada Fator no Resultado'
            )
            figura.update_traces(marker_color='#3498db')
            figura.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            grafico = pio.to_html(figura, full_html=False)

        return render_template('index.html', predicao=resultado, grafico=grafico)

    return render_template('index.html', predicao=None, grafico=None)


@app.route("/dashboard")
def dashboard():
    try:
        df = pd.read_csv('instances/estudantes.csv')
    except FileNotFoundError:
        try:
            df = pd.read_csv('estudantes.csv')
        except FileNotFoundError:
            conn = sqlite3.connect('banco.db')
            df = pd.read_sql_query("SELECT * FROM historico", conn)
            conn.close()

    graficos = {}

    if not df.empty:
        # Normaliza os nomes das colunas para evitar erros
        df.columns = df.columns.str.strip().str.lower()

        # Mapeamento de colunas
        col_idade     = 'idade'              if 'idade'              in df.columns else df.columns[4]
        col_freq      = 'frequencia'         if 'frequencia'         in df.columns else df.columns[1]
        col_renda     = 'renda_familiar'     if 'renda_familiar'     in df.columns else (
                        'renda'              if 'renda'              in df.columns else df.columns[3])
        col_media     = 'media_notas'        if 'media_notas'        in df.columns else (
                        'media'              if 'media'              in df.columns else df.columns[2])
        col_risco     = 'risco_evasao'       if 'risco_evasao'       in df.columns else (
                        'resultado_texto'    if 'resultado_texto'    in df.columns else None)
        col_rep       = 'historico_repetencia' if 'historico_repetencia' in df.columns else (
                        'repetencia'         if 'repetencia'         in df.columns else None)

        # --- CORREÇÃO: Converter coluna de risco para numérica ---
        # O gráfico de linha 'Risco por Idade' precisa de valores numéricos para calcular a média.
        # Se a coluna de risco for texto (ex: 'Alto Risco'), esta linha converte para 1 (risco) ou 0 (estável).
        # Usamos pd.api.types.is_numeric_dtype em vez de comparar com 'object' diretamente,
        # pois no pandas 2.x/3.x colunas de texto vindas de SQL podem ter dtype 'str',
        # e a comparação "dtype == 'object'" falha silenciosamente nesse caso, quebrando
        # o groupby().mean() mais abaixo quando o dashboard usa o banco.db como fonte.
        if col_risco and not pd.api.types.is_numeric_dtype(df[col_risco]):
            df[col_risco] = df[col_risco].apply(
                lambda x: 1 if 'alto' in str(x).lower() or 'evasão' in str(x).lower() else 0
            )

        layout_base = dict(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Segoe UI, sans-serif', color='#2c3e50'),
            margin=dict(t=50, b=40, l=40, r=20)
        )

        # ── 1. Dispersão: Idade × Frequência ──────────────────────────────────
        fig1_kwargs = dict(color=col_risco) if col_risco else dict(color_discrete_sequence=['#e74c3c'])
        fig1 = px.scatter(
            df, x=col_idade, y=col_freq,
            title='Dispersão: Idade vs Frequência Escolar',
            labels={col_idade: 'Idade', col_freq: 'Frequência (%)'},
            **fig1_kwargs
        )
        fig1.update_layout(**layout_base)
        graficos['dispersao'] = pio.to_html(fig1, full_html=False)

        # ── 2. Histograma: Distribuição de Renda ─────────────────────────────
        fig2 = px.histogram(
            df, x=col_renda, nbins=10,
            title='Distribuição da Renda Familiar',
            labels={col_renda: 'Renda Familiar', 'count': 'Qtd. Estudantes'},
            color_discrete_sequence=['#2ecc71']
        )
        fig2.update_layout(**layout_base)
        graficos['hist_renda'] = pio.to_html(fig2, full_html=False)

        # ── 3. Histograma: Distribuição das Médias de Notas ───────────────────
        fig3 = px.histogram(
            df, x=col_media, nbins=15,
            title='Distribuição das Médias de Notas',
            labels={col_media: 'Média de Notas', 'count': 'Qtd. Estudantes'},
            color_discrete_sequence=['#9b59b6']
        )
        fig3.update_layout(**layout_base)
        graficos['hist_notas'] = pio.to_html(fig3, full_html=False)

        # ── 4. Box Plot: Frequência por Faixa de Renda ────────────────────────
        fig4 = px.box(
            df, x=col_renda, y=col_freq,
            title='Frequência Escolar por Faixa de Renda',
            labels={col_renda: 'Renda Familiar', col_freq: 'Frequência (%)'},
            color_discrete_sequence=['#f39c12']
        )
        fig4.update_layout(**layout_base)
        graficos['box_freq_renda'] = pio.to_html(fig4, full_html=False)

        # ── 5. Pizza / Rosca: Proporção de Risco de Evasão ───────────────────
        if col_risco:
            contagem = df[col_risco].value_counts().reset_index()
            contagem.columns = ['Risco', 'Total']
            fig5 = px.pie(
                contagem, names='Risco', values='Total',
                title='Proporção de Risco de Evasão',
                hole=0.4,
                color_discrete_sequence=['#3498db', '#e74c3c']
            )
            fig5.update_layout(**layout_base)
            graficos['pizza_evasao'] = pio.to_html(fig5, full_html=False)

            # ── 5.1. Risco Médio de Evasão por Idade ───────────────────
            risco_idade = df.groupby(col_idade)[col_risco].mean().reset_index()
            fig8 = px.line(
                risco_idade,
                x=col_idade,
                y=col_risco,
                markers=True,
                title='Risco Médio de Evasão por Idade',
                labels={
                    col_idade: 'Idade',
                    col_risco: 'Risco Médio'
                }
            )
            fig8.update_layout(**layout_base)
            graficos['risco_idade'] = pio.to_html(
                fig8,
                full_html=False
            )

        # ── 6. Barras Agrupadas: Média de Notas vs Repetência ────────────────
        if col_rep:
            df_rep = df.groupby(col_rep)[col_media].mean().reset_index()
            df_rep[col_rep] = df_rep[col_rep].map({0: 'Sem Repetência', 1: 'Com Repetência'})
            fig6 = px.bar(
                df_rep, x=col_rep, y=col_media,
                title='Média de Notas: Com vs Sem Repetência',
                labels={col_rep: 'Histórico de Repetência', col_media: 'Média de Notas'},
                color=col_rep,
                color_discrete_sequence=['#1abc9c', '#e74c3c']
            )
            fig6.update_layout(**layout_base, showlegend=False)
            graficos['barras_rep'] = pio.to_html(fig6, full_html=False)

        # ── 7. Dispersão: Frequência × Média (colorida por risco) ────────────
        scatter_kwargs = dict(color=col_risco, color_discrete_sequence=['#3498db', '#e74c3c']) \
            if col_risco else dict(color_discrete_sequence=['#3498db'])
        fig7 = px.scatter(
            df, x=col_freq, y=col_media,
            title='Frequência vs Média de Notas',
            labels={col_freq: 'Frequência (%)', col_media: 'Média de Notas'},
            **scatter_kwargs
        )
        fig7.update_layout(**layout_base)
        graficos['dispersao_freq_media'] = pio.to_html(fig7, full_html=False)

    return render_template('dashboard.html', graficos=graficos)


@app.route("/dados")
def dados():
    conn = sqlite3.connect('banco.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM historico ORDER BY id DESC')
    registros = cursor.fetchall()
    conn.close()

    # Estatísticas rápidas para o topo da página
    conn2 = sqlite3.connect('banco.db')
    df_hist = pd.read_sql_query("SELECT * FROM historico", conn2)
    conn2.close()

    stats = {}
    if not df_hist.empty:
        stats['total']      = len(df_hist)
        stats['media_freq'] = round(df_hist['frequencia'].mean(), 1)
        stats['media_nota'] = round(df_hist['media'].mean(), 1)
        stats['risco_alto'] = int((df_hist['resultado_texto'].str.contains('Alto|Evasão', case=False, na=False)).sum())

    return render_template('dados.html', registros=registros, stats=stats)


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
