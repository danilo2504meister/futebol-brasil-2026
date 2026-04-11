from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    pagina = request.args.get("pagina", "🏠 Início")

    data_atualizacao = "10/04/2026"  # <-- ALTERA SÓ ISSO TODO DIA

    if pagina == "🏠 Início":
        return f"""
        <html>
        <head>
            <title>Futebol Brasil 2026</title>
        </head>
        <body style="background-color: #111; color: white; font-family: Arial; text-align: center;">

            <h1>⚽ Futebol Brasil</h1>

            <p style="color: #aaa;">🔄 Atualizado em: {data_atualizacao}</p>

            <hr>

            <h2>Páginas</h2>

            <a href="/?pagina=🏠 Início" style="color: white;">🏠 Início</a> |
            <a href="/?pagina=📈 Classificação" style="color: white;">📈 Classificação</a>

            <hr>

            <p>Bem-vindo ao seu site de resultados 👊</p>

        </body>
        </html>
        """

    elif pagina == "📈 Classificação":
        return f"""
        <html>
        <head>
            <title>Classificação</title>
        </head>
        <body style="background-color: #111; color: white; font-family: Arial; text-align: center;">

            <h1>📈 Classificação</h1>

            <p style="color: #aaa;">🔄 Atualizado em: {data_atualizacao}</p>

            <hr>

            <a href="/?pagina=🏠 Início" style="color: white;">⬅️ Voltar</a>

            <hr>

            <p>Aqui vai sua tabela depois...</p>

        </body>
        </html>
        """

    else:
        return "Página não encontrada"


if __name__ == "__main__":
    app.run(debug=True)
