from .conftest import register_user, login_token, auth_headers

def test_get_me_and_list_users(client):
    username1 = "osimhen"
    password1 = "gala1905"
    register_user(client, username1, password1)
    token1 = login_token(client, username1, password1)

    me = client.get("/users/me", headers=auth_headers(token1))
    assert me.status_code == 200
    data = me.json()
    assert data["username"] == username1
    assert "id" in data

    username2 = "icardi"
    password2 = "mauro"
    register_user(client, username2, password2)

    lst = client.get("/users", headers=auth_headers(token1))
    assert lst.status_code == 200
    usernames = [u["username"] for u in lst.json()]
    assert username1 in usernames
    assert username2 in usernames

def test_get_user_by_id(client):
    username = "davinson"
    password = "sanchez"
    r = register_user(client, username, password)
    uid = r.json()["id"]

    token = login_token(client, username, password)

    g = client.get(f"/users/{uid}", headers=auth_headers(token))
    assert g.status_code == 200
    assert g.json()["username"] == username

    g2 = client.get("/users/9999", headers=auth_headers(token))
    assert g2.status_code == 404
