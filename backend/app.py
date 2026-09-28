"""
Flask Application for Tone-Based Email & Message Generator.
Member 2 Module: Backend API & Service Integration.
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Ensure root project path is in sys.path so modules can be cleanly imported
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.database import create_table, save_history
from backend.ai_generator import generate_message
from backend.prompts import (
    SUPPORTED_MESSAGE_TYPES,
    SUPPORTED_TONES,
    SUPPORTED_LANGUAGES,
    SUPPORTED_LENGTHS
)
from backend.history_routes import history_bp

# Load environment variables
load_dotenv()


class PrefixMiddleware:
    """Middleware to strip '/api' prefix if present so routes work seamlessly."""
    def __init__(self, wsgi_app, prefix="/api"):
        self.wsgi_app = wsgi_app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        path_info = environ.get("PATH_INFO", "")
        if path_info.startswith(self.prefix):
            environ["PATH_INFO"] = path_info[len(self.prefix):] or "/"
        return self.wsgi_app(environ, start_response)


def create_app(test_config=None):
    """
    Application factory for Flask app.
    """
    dist_dir = os.path.join(ROOT_DIR, "frontend-react", "dist")
    if os.path.exists(dist_dir):
        app = Flask(__name__, static_folder=dist_dir, static_url_path="")
    else:
        app = Flask(__name__)
    CORS(app)
    app.wsgi_app = PrefixMiddleware(app.wsgi_app)
    
    # Initialize SQLite database table if it doesn't exist
    create_table()
    
    # Register blueprints
    app.register_blueprint(history_bp)
    
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        """
        Serves built React frontend files or API status.
        """
        if app.static_folder and path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        if app.static_folder and os.path.exists(os.path.join(app.static_folder, "index.html")):
            return send_from_directory(app.static_folder, "index.html")
        if not path:
            return jsonify({
                "status": "healthy",
                "service": "Tone-Based Email & Message Generator API"
            }), 200
        return jsonify({
            "success": False,
            "error": "Endpoint not found"
        }), 404
    
    @app.route("/health", methods=["GET"])
    def health_check():
        """
        GET /health
        Simple health check endpoint to verify backend status.
        """
        return jsonify({
            "status": "healthy",
            "service": "Tone-Based Email & Message Generator API"
        }), 200

    @app.route("/generate", methods=["POST"])
    def handle_generate():
        """
        POST /generate
        Generates email or message based on tone, language, and length settings,
        saves the result to SQLite history database, and returns formatted JSON response.
        """
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Request content type must be application/json"
            }), 400
            
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({
                "success": False,
                "error": "Invalid JSON payload"
            }), 400
            
        # Check presence of required fields
        required_fields = ["input_text", "message_type", "tone", "language", "length"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400

        input_text = data.get("input_text", "")
        message_type = data.get("message_type")
        tone = data.get("tone")
        language = data.get("language")
        length = data.get("length")

        # Validate empty/whitespace input_text
        if not isinstance(input_text, str) or not input_text.strip():
            return jsonify({
                "success": False,
                "error": "Input text is required"
            }), 400

        # Validate message_type
        if message_type not in SUPPORTED_MESSAGE_TYPES:
            return jsonify({
                "success": False,
                "error": f"Invalid message type"
            }), 400

        # Validate tone
        if tone not in SUPPORTED_TONES:
            return jsonify({
                "success": False,
                "error": f"Invalid tone"
            }), 400

        # Validate language
        if language not in SUPPORTED_LANGUAGES:
            return jsonify({
                "success": False,
                "error": f"Invalid language"
            }), 400

        # Validate length
        if length not in SUPPORTED_LENGTHS:
            return jsonify({
                "success": False,
                "error": f"Invalid length"
            }), 400

        try:
            # 1. Generate text using AI Generator
            generated_text = generate_message(
                input_text=input_text.strip(),
                message_type=message_type,
                tone=tone,
                language=language,
                length=length
            )

            # 2. Save result into database
            row_id = save_history(
                input_text=input_text.strip(),
                message_type=message_type,
                tone=tone,
                language=language,
                length=length,
                generated_text=generated_text
            )

            # 3. Return JSON response
            return jsonify({
                "success": True,
                "data": {
                    "id": row_id,
                    "message_type": message_type,
                    "tone": tone,
                    "language": language,
                    "length": length,
                    "generated_text": generated_text
                }
            }), 200

        except ValueError as ve:
            return jsonify({
                "success": False,
                "error": str(ve)
            }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Generation failed: {str(e)}"
            }), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": "Endpoint not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": "Method not allowed"
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 5000)))
    debug = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    print(f"Starting Flask application server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=debug)
