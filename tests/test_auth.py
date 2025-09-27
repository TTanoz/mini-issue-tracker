from .conftest import register_user, login_token, auth_headers

def test_register_and_login_and_me(client):
    r = register_user(client, username="osimhen", password="gala1905")
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "osimhen"
    assert "id" in data

    token = login_token(client, "osimhen", "gala1905")
    me = client.get("/users/me", headers=auth_headers(token))
    assert me.status_code == 200
    me_data = me.json()
    assert me_data["username"] == "osimhen"

def test_register_duplicate_username(client):
    u1 = register_user(client, username="osimhen", password="gala1905")
    u2 = register_user(client, username="osimhen", password="1905gala")
    assert u2.status_code == 409

def test_change_password_and_relogin(client):
    register_user(client, username="osimhen", password="gala1905")
    t = login_token(client, "osimhen", "gala1905")
    res = client.post("/users/me/change-password", headers=auth_headers(t), json={"old_password": "gala1905", "new_password": "1905gala"})
    assert res.status_code == 204
    bad = client.post("/auth/login", json={"username": "osimhen", "password": "gala1905"})
    assert bad.status_code == 401
    t2 = login_token(client, "osimhen", "1905gala")
    assert isinstance(t2, str) and len(t2) > 10

