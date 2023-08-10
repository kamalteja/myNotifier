from hello import app


if __name__ == "__main__":
    # app.config["DEBUG"] = True
    app.run(debug=False, port=8000)
