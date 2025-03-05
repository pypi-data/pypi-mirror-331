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
router = init(config)
app.include_router(router, prefix=f"/api/{prefix}")
client_comments = TestClient(app)
client_comments_prefix = f"/api/{prefix}/comments"

def test_create_comment():
    response = client_comments.post(client_comments_prefix + "/", json={
        "comment": "This is a test comment.",
        "user_id": 1,
        "conversation_id": 1
    })
    assert response.status_code == 201
    comment = response.json()
    assert comment["comment"] == "This is a test comment."
    assert comment["user_id"] == 1
    assert comment["conversation_id"] == 1
    assert comment["moderated"] == False
    assert comment["approved"] == False

    # Clean up
    comment_id = comment["id"]
    response = client_comments.delete(client_comments_prefix + f"/{comment_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_read_comment():
    # Create a comment first
    response = client_comments.post(client_comments_prefix + "/", json={
        "comment": "This is a test comment.",
        "user_id": 1,
        "conversation_id": 1
    })
    comment_id = response.json()["id"]

    response = client_comments.get(client_comments_prefix + f"/{comment_id}")
    assert response.status_code == 200
    comment = response.json()
    assert comment["comment"] == "This is a test comment."
    assert comment["user_id"] == 1
    assert comment["conversation_id"] == 1

    # Clean up
    response = client_comments.delete(client_comments_prefix + f"/{comment_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_read_comments():
    response = client_comments.get(client_comments_prefix + "/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Check if it returns a list of comments


def test_update_comment():
    # Create a comment first
    response = client_comments.post(client_comments_prefix + "/", json={
        "comment": "This is a test comment.",
        "user_id": 1,
        "conversation_id": 1
    })
    comment_id = response.json()["id"]

    response = client_comments.patch(client_comments_prefix + f"/{comment_id}", json={"comment": "Updated comment"})
    assert response.status_code == 200
    updated_comment = response.json()
    assert updated_comment["comment"] == "Updated comment"

    # Clean up
    response = client_comments.delete(client_comments_prefix + f"/{comment_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_delete_comment():
    # Create a comment first
    response = client_comments.post(client_comments_prefix + "/", json={
        "comment": "This is a test comment.",
        "user_id": 1,
        "conversation_id": 1
    })
    comment_id = response.json()["id"]

    response = client_comments.delete(client_comments_prefix + f"/{comment_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # Try to get the deleted comment (should return 404)
    response = client_comments.get(client_comments_prefix + f"/{comment_id}")
    assert response.status_code == 404
