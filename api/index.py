"""
Vercel Serverless Function Entrypoint for Flask Application.
"""
import os
import sys

# Ensure root directory is in sys.path so modules can be imported
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app import app

# Middleware to strip '/api' prefix if present so Flask routes work seamlessly
class PrefixMiddleware:
    def __init__(self, wsgi_app, prefix='/api'):
        self.wsgi_app = wsgi_app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if path_info.startswith(self.prefix):
            environ['PATH_INFO'] = path_info[len(self.prefix):] or '/'
        return self.wsgi_app(environ, start_response)

app.wsgi_app = PrefixMiddleware(app.wsgi_app)

# Expose WSGI handler for Vercel
app = app
