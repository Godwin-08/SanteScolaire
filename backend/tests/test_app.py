from app import create_app


def test_create_app_uses_env(monkeypatch):
    monkeypatch.setenv("DB_PASSWORD", "test-password")
    monkeypatch.setenv("SECRET_KEY", "test-secret")

    app = create_app()

    assert app.config["MYSQL_PASSWORD"] == "test-password"
    assert app.config["SECRET_KEY"] == "test-secret"
