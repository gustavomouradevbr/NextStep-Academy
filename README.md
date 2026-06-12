# Configuração e Execução do Projeto

## Extensões Recomendadas para o VS Code

1. **Python (Microsoft):** 
2. **Jupyter (Microsoft):** 
3. **Jinja (Whonore) ou Jinja HTML Snippets:** 
4. **HTML CSS Support:** 

---

## 📦 Bibliotecas e Dependências

As principais bibliotecas utilizadas no projeto e listadas no arquivo `requirements.txt` são:

* **Flask:** Framework web para o desenvolvimento do backend e das rotas da aplicação.
* **pandas:** Manipulação, limpeza e análise descritiva das bases de dados.
* **numpy:** Operações matemáticas e manipulação de arrays multidimensionais para os modelos.
* **scikit-learn:** Ferramentas de Machine Learning para o treinamento, avaliação e exportação do modelo preditivo.
* **plotly:** Geração de gráficos dinâmicos e interativos integrados à interface web.

---

## Como Executar o Projeto

1. **Criar o Ambiente Virtual (venv):**
   ```bash
   python -m venv venv
   ```

2. **Ativar o Ambiente Virtual:**
   * **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
   * **Windows (CMD):** `.\venv\Scripts\activate.bat`
   * **Linux / macOS:** `source venv/bin/activate`
   
   *(Dica: Se aparecer um `(venv)` no início da linha do seu terminal, significa que já está ativado! O VS Code costuma fazer isso automaticamente).*

3. **Instalar todas as Dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Treinar o Modelo Inicial (Necessário para a primeira execução):**
   ```bash
   python model.py
   ```

5. **Iniciar o Servidor Flask:**
   ```bash
   python app.py
   ```

6. **Acessar a Aplicação:**
   Abra o seu navegador e acesse o endereço local: http://127.0.0.1:5000