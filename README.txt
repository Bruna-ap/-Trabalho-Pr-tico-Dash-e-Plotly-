Trabalho Prático Dash e Plotly - Dashboard Quadro de Medalhas Olímpicas

Para executar:
1. Instale Python.
2. Abra esta pasta no VS Code.
3. No terminal: python -m venv .venv
4. No PowerShell: .venv\Scripts\Activate.ps1
5. Execute: pip install -r requirements.txt
6. Execute: python app.py
7. Abra http://127.0.0.1:8050

Render:
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:server

Link público do Render: https://dashboard-medalhas-olimpicas-bruna.onrender.com.

O arquivo Country_Medals.csv é necessário para os gráficos e deve permanecer na raiz da pasta.
