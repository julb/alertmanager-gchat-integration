import os

from .app import app

if __name__ == '__main__':
    port = os.environ['PORT'] if 'PORT' in os.environ else 8080
    app.run(host='0.0.0.0', port=port)
