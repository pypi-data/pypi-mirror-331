import configparser
from fastapi.testclient import TestClient
from litepolis_router_database_sqlite import *
from fastapi import FastAPI

app = FastAPI()
config = configparser.ConfigParser()
package_name = "litepolis_router_database_sqlite"
config.add_section(package_name)
for k, v in DEFAULT_CONFIG.items():
    config.set(package_name, k, v)
config.set(package_name, "sqlite_url", "sqlite:///database-test.db")
router = init(config)
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

