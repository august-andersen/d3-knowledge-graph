"""Flask app and routes."""

import json
import logging

from flask import Flask, jsonify

from .dashboard import generate_dashboard_html


def create_app(graph_data: dict, show_labels: bool = False) -> Flask:
    app = Flask(__name__)

    # Suppress Flask request logs
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.WARNING)

    html = generate_dashboard_html(graph_data, show_labels=show_labels)

    @app.route("/")
    def index():
        return html

    @app.route("/api/graph")
    def api_graph():
        return jsonify(graph_data)

    return app
