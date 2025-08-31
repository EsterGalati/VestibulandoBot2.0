from app import create_app
app = create_app()
if __name__ == "__main__":
    app.run(debug=True)

    app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True,
)
