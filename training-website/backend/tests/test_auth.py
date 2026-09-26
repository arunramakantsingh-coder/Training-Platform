def test_register_login_me_logout(client):
    response = client.post("/api/v1/auth/register", json={"email":"learner@example.com","full_name":"Test Learner","password":"StrongPassword123!"})
    assert response.status_code == 201
    assert client.get("/api/v1/auth/me").status_code == 200
    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.post("/api/v1/auth/login", json={"email":"learner@example.com","password":"StrongPassword123!"}).status_code == 200


def test_duplicate_and_bad_login(client):
    payload={"email":"duplicate@example.com","full_name":"Duplicate User","password":"StrongPassword123!"}
    assert client.post("/api/v1/auth/register",json=payload).status_code==201
    assert client.post("/api/v1/auth/register",json=payload).status_code==409
    assert client.post("/api/v1/auth/login",json={"email":"duplicate@example.com","password":"WrongPassword"}).status_code==401
