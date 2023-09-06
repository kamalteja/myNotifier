"""wsgi application contrller"""
from notifier.app import earth_app

if __name__ == "__main__":
    earth_app.run(
        debug=earth_app.config["DEBUG"], port=8000, host="0.0.0.0", use_reloader=False
    )
