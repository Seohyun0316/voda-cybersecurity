"""Development entry point for the VibeSafe backend."""

from vibesafe.api import create_app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
