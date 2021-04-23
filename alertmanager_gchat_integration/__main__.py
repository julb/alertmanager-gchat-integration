import os

from .app import app

def run():
    port = os.environ.get('PORT', 8080)
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    run()
