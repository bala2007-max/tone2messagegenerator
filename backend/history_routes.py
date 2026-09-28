"""
History Routes Blueprint for Tone-Based Email & Message Generator.
Member 2 Module: History API Endpoints.
Integrates directly with Member 3 database module (database/database.py).
"""

from flask import Blueprint, jsonify, request
from database.database import (
    get_history,
    get_history_by_id,
    delete_history,
    clear_history
)

history_bp = Blueprint("history", __name__)


@history_bp.route("/history", methods=["GET"])
def handle_get_all_history():
    """
    GET /history
    Retrieves all generated message history records sorted by newest first.
    """
    try:
        tone = request.args.get("tone") or None
        message_type = request.args.get("type") or None
        records = get_history(tone=tone, message_type=message_type)
        return jsonify({
            "success": True,
            "data": records
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to retrieve history: {str(e)}"
        }), 500


@history_bp.route("/history/<int:history_id>", methods=["GET"])
def handle_get_history_by_id(history_id: int):
    """
    GET /history/<id>
    Retrieves a single message history record by ID.
    """
    try:
        record = get_history_by_id(history_id)
        if not record:
            return jsonify({
                "success": False,
                "error": "History record not found"
            }), 404
            
        return jsonify({
            "success": True,
            "data": record
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to retrieve history record: {str(e)}"
        }), 500


@history_bp.route("/history/<int:history_id>", methods=["DELETE"])
def handle_delete_history_by_id(history_id: int):
    """
    DELETE /history/<id>
    Deletes a single message history record by ID.
    """
    try:
        success = delete_history(history_id)
        if not success:
            return jsonify({
                "success": False,
                "error": "History record not found"
            }), 404
            
        return jsonify({
            "success": True,
            "message": "History record deleted successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to delete history record: {str(e)}"
        }), 500


@history_bp.route("/history", methods=["DELETE"])
def handle_clear_all_history():
    """
    DELETE /history
    Clears all history records from the database.
    """
    try:
        deleted_count = clear_history()
        return jsonify({
            "success": True,
            "message": "All history records cleared successfully",
            "deleted_count": deleted_count
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to clear history: {str(e)}"
        }), 500
