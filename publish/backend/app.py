"""Local-only entry point for the VibeSafe backend."""

from vibesafe.api import create_app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=38457,
        debug=False,
        use_reloader=False,
    )
