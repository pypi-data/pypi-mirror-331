from flask import Response, jsonify


def ping_2() -> Response:
    """Test route to verify that the server is online."""
    return jsonify({"message": "pong_2"})
