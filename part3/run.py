#!/usr/bin/python3
"""Application entry point for Part 3."""

from config import Config
from hbnb import create_app


app = create_app(Config)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
