from .conftest import register_user, login_token, auth_headers

def _create_project(client, token, name="PC", desc=""):
    res = client.post("/projects", headers=auth_headers(token), json={"name": name, "desc": desc})
    assert res.status_code == 201, res.text
    return res.json()["id"]

def _create_issue(client, token, pid, title="CMT-ISSUE"):
    res = client.post(
        f"/projects/{pid}/issues",
        headers=auth_headers(token),
        json={"title": title, "desc": "", "status": "open", "priority": "medium"},
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]

def test_comment_crud_and_permissions(client):
    register_user(client, "osimhen", "gala")
    ta = login_token(client, "osimhen", "gala")
    register_user(client, "icardi", "gala")
    to = login_token(client, "icardi", "gala")

    pid = _create_project(client, ta, "P-CMT")
    iid = _create_issue(client, ta, pid, "IssueForComments")

    c = client.post(f"/issues/{iid}/comments", headers=auth_headers(ta), json={"content": "first!"})
    assert c.status_code == 201, c.text
    cid = c.json()["id"]

    lst = client.get(f"/issues/{iid}/comments")
    assert lst.status_code == 200
    assert any(x["id"] == cid for x in lst.json())

    g = client.get(f"/comments/{cid}")
    assert g.status_code == 200
    assert g.json()["content"] == "first!"

    p = client.patch(f"/comments/{cid}", headers=auth_headers(ta), json={"content": "edited"})
    assert p.status_code == 200
    assert p.json()["content"] == "edited"

    p_bad = client.patch(f"/comments/{cid}", headers=auth_headers(to), json={"content": "hack"})
    assert p_bad.status_code == 403

    d_bad = client.delete(f"/comments/{cid}", headers=auth_headers(to))
    assert d_bad.status_code == 403

    d = client.delete(f"/comments/{cid}", headers=auth_headers(ta))
    assert d.status_code == 204
