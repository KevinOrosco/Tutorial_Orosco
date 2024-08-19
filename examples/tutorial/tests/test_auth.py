import pytest
from flask import g
from flask import session
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from flaskr.db import get_db


def test_register(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/auth/register").status_code == 200

    # test that successful registration redirects to the login page
    response = client.post("/auth/register", data={"username": "a", "password": "b", "repassword": "c", "email": "d"})
    assert response.headers["Location"] == "/auth/login"

    # test that the user was inserted into the database
    with app.app_context():
        usuario = get_db().execute("SELECT * FROM user WHERE username = 'a' ").fetchone()
        assert (usuario is not None)
        assert(check_password_hash(usuario['password'], 'b'))


@pytest.mark.parametrize(
    ("username", "password", "repassword", "email", "message"),
    (
        ("", "b", "24", "d","Nombre de usuario requerido."),
        ("a", "", "24", "d","Contraseña requerida"),
        ("a", "b", "", "d","Verificacion requerida"),
        ("a", "b", "24", "","Email requerido"),
        ("a", "b", "24", "d","Las contraseñas no coinciden"),
        ("test", "test", "test", "test","Ya esta registrado"),
    ),
)

def test_register_validate_input(client, username, password, message):
    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )
    assert message in response.data.decode()


def test_login(client, auth):
    # test that viewing the page renders without template errors
    assert client.get("/auth/login").status_code == 200

    # test that successful login redirects to the index page
    response = auth.login()
    assert response.headers["Location"] == "/"

    # login request set the user_id in the session
    # check that the user is loaded from the session
    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("a", "test", "Incorrect username."), 
     ("test", "a", "Incorrect password.")),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data.decode()


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
