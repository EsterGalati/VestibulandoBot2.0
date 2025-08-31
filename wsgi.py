# wsgi.py
from app import create_app

app = create_app()
# cookies p/ DEV
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
)

if __name__ == "__main__":
    app.run(debug=True)
