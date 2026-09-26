def test_create_and_list_organization(client):
    client.post("/api/v1/auth/register",json={"email":"orgadmin@example.com","full_name":"Org Admin","password":"StrongPassword123!"})
    create=client.post("/api/v1/organizations",json={"name":"Acme Learning"})
    assert create.status_code==201
    assert create.json()["slug"]=="acme-learning"
    organizations=client.get("/api/v1/organizations")
    assert organizations.status_code==200
    assert len(organizations.json())==1


def test_admin_endpoint_requires_platform_admin(client):
    client.post("/api/v1/auth/register",json={"email":"normal@example.com","full_name":"Normal","password":"StrongPassword123!"})
    assert client.get("/api/v1/admin/users").status_code==403
