from .conftest import register_user, login_token, auth_headers

def test_create_list_get_delete_project(client):
    register_user(client, "osimhen", "gala")
    tok = login_token(client, "osimhen", "gala")

    c = client.post("/projects", headers=auth_headers(tok), json={"name": "ProjA", "desc": "desc"})
    assert c.status_code == 201, c.text
    pid = c.json()["id"]

    lst = client.get("/projects")
    assert lst.status_code == 200
    assert any(p["id"] == pid for p in lst.json())

    g = client.get(f"/projects/{pid}")
    assert g.status_code == 200
    assert g.json()["name"] == "ProjA"

    d = client.delete(f"/projects/{pid}", headers=auth_headers(tok))
    assert d.status_code == 204

    g2 = client.get(f"/projects/{pid}")
    assert g2.status_code == 404

def test_project_name_unique_per_owner(client):
    register_user(client, "osimhen", "gala")
    t1 = login_token(client, "osimhen", "gala")
    register_user(client, "icardi", "mauro")
    t2 = login_token(client, "icardi", "mauro")

    r1 = client.post("/projects", headers=auth_headers(t1), json={"name": "Same", "desc": ""})
    assert r1.status_code == 201
    r1b = client.post("/projects", headers=auth_headers(t1), json={"name": "Same", "desc": ""})
    assert r1b.status_code == 409

    r2 = client.post("/projects", headers=auth_headers(t2), json={"name": "Same", "desc": ""})
    assert r2.status_code == 201

def test_only_owner_can_delete_project(client):
    register_user(client, "osimhen", "gala")
    to = login_token(client, "osimhen", "gala")
    register_user(client, "icardi", "mauro")
    tx = login_token(client, "icardi", "mauro")

    c = client.post("/projects", headers=auth_headers(to), json={"name": "DelMe", "desc": ""})
    pid = c.json()["id"]

    d_bad = client.delete(f"/projects/{pid}", headers=auth_headers(tx))
    assert d_bad.status_code == 403
