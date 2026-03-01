#!/usr/bin/python3
"""Application entry point for Part 2."""

from hbnb import create_app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
