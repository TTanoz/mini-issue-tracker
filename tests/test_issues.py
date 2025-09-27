from sqlalchemy.exc import IntegrityError
from .conftest import register_user, login_token, auth_headers

def _create_project(client, token, name="P", desc=""):
    r = client.post("/projects", headers=auth_headers(token), json={"name": name, "desc": desc})
    assert r.status_code == 201, r.text
    return r.json()["id"]

def test_issue_create_list_get_patch_delete(client):
    register_user(client, "osimhen", "gala")
    tr = login_token(client, "osimhen", "gala")
    pid = _create_project(client, tr, "ISSUEPROJ")

    c = client.post(
        f"/projects/{pid}/issues",
        headers=auth_headers(tr),
        json={"title": "Bug 1", "desc": "details", "status": "open", "priority": "medium", "assignee_id": None},
    )
    assert c.status_code == 201, c.text
    issue_id = c.json()["id"]

    lst = client.get(f"/projects/{pid}/issues")
    assert lst.status_code == 200
    assert any(i["id"] == issue_id for i in lst.json())

    g = client.get(f"/issues/{issue_id}")
    assert g.status_code == 200
    assert g.json()["title"] == "Bug 1"

    p = client.patch(
        f"/issues/{issue_id}",
        headers=auth_headers(tr),
        json={"status": "closed", "title": "Bug 1 fixed"},
    )
    assert p.status_code == 200
    assert p.json()["status"] == "closed"
    assert p.json()["title"] == "Bug 1 fixed"

    d = client.delete(f"/issues/{issue_id}", headers=auth_headers(tr))
    assert d.status_code == 204

def test_issue_title_unique_per_project(client):
    register_user(client, "osimhen", "gala")
    t = login_token(client, "osimhen", "gala")
    p1 = _create_project(client, t, "P1")
    p2 = _create_project(client, t, "P2")

    body = {"title": "SameTitle", "desc": "", "status": "open", "priority": "medium"}

    a = client.post(f"/projects/{p1}/issues", headers=auth_headers(t), json=body)
    assert a.status_code == 201

    b = client.post(f"/projects/{p1}/issues", headers=auth_headers(t), json=body)
    assert b.status_code == 409

    c = client.post(f"/projects/{p2}/issues", headers=auth_headers(t), json=body)
    assert c.status_code == 201

def test_only_osimhenorter_can_modify_or_delete_issue(client):
    register_user(client, "osimhen2", "gala")
    tr = login_token(client, "osimhen2", "gala")
    register_user(client, "icardi", "mauro")
    to = login_token(client, "icardi", "mauro")

    pid = _create_project(client, tr, "P-Edit")

    created = client.post(
        f"/projects/{pid}/issues",
        headers=auth_headers(tr),
        json={"title": "EditMe", "desc": "", "status": "open", "priority": "medium"},
    )
    iid = created.json()["id"]

    patch_bad = client.patch(f"/issues/{iid}", headers=auth_headers(to), json={"desc": "oops"})
    assert patch_bad.status_code in (403, 404)

    del_bad = client.delete(f"/issues/{iid}", headers=auth_headers(to))
    assert del_bad.status_code in (403, 404)
