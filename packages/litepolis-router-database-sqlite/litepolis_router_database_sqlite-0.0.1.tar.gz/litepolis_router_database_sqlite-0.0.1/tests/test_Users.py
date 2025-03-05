from fastapi.testclient import TestClient
from litepolis_router_database_sqlite import *
from fastapi import FastAPI

app = FastAPI()
router = init()
app.include_router(router, prefix=f"/api/{prefix}")
client_users = TestClient(app)


def test_create_user():
    response = client_users.post(f"/api/{prefix}/users/", json={
        "email": "test@example.com",
        "password": "password",
        "privilege": "user"
    })
    assert response.status_code == 201
    user = response.json()
    assert user["email"] == "test@example.com"
    assert "id" in user

    # Clean up (delete the created user)
    user_id = user["id"]
    response = client_users.delete(f"/api/{prefix}/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_read_user():
    # Create a user first for testing
    response = client_users.post(f"/api/{prefix}/users/", json={
        "email": "test@example.com",
        "password": "password",
        "privilege": "user"
    })
    assert response.status_code == 201
    user = response.json()
    user_id = user["id"]

    response = client_users.get(f"/api/{prefix}/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == user

    # Clean up
    response = client_users.delete(f"/api/{prefix}/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_read_users():
    response = client_users.get(f"/api/{prefix}/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Check if it returns a list of users


def test_update_user():
    # Create a user first
    response = client_users.post(f"/api/{prefix}/users/", json={
        "email": "test@example.com",
        "password": "password",
        "privilege": "user"
    })
    user_id = response.json()["id"]

    response = client_users.patch(f"/api/{prefix}/users/{user_id}", json={"privilege": "admin"})
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["privilege"] == "admin"

    # Clean up
    response = client_users.delete(f"/api/{prefix}/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_delete_user():
    # Create a user first
    response = client_users.post(f"/api/{prefix}/users/", json={
        "email": "test@example.com",
        "password": "password",
        "privilege": "user"
    })
    user_id = response.json()["id"]

    response = client_users.delete(f"/api/{prefix}/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # Try to get the deleted user (should return 404)
    response = client_users.get(f"/api/{prefix}/users/{user_id}")
    assert response.status_code == 404


