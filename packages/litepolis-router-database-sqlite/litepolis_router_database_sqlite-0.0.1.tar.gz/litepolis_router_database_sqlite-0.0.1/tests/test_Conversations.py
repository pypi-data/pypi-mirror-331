from fastapi.testclient import TestClient
from litepolis_router_database_sqlite import *
from fastapi import FastAPI

app = FastAPI()
router = init()
app.include_router(router, prefix=f"/api/{prefix}")
client_conversations = TestClient(app)


def test_create_conversation():
    response = client_conversations.post(f"/api/{prefix}/conversations/", json={
        "title": "Test Conversation",
        "description": "This is a test conversation.",
        "creator_id": 1
    })
    assert response.status_code == 201
    conversation = response.json()
    assert conversation["title"] == "Test Conversation"
    assert conversation["description"] == "This is a test conversation."
    assert conversation["creator_id"] == 1
    conversation_id = conversation["id"]

    # Clean up
    response = client_conversations.delete(f"/api/{prefix}/conversations/{conversation_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_read_conversation():
    # Create a conversation first
    response = client_conversations.post(f"/api/{prefix}/conversations/", json={
        "title": "Test Conversation",
        "description": "This is a test conversation.",
        "creator_id": 1
    })
    conversation_id = response.json()["id"]

    response = client_conversations.get(f"/api/{prefix}/conversations/{conversation_id}")
    assert response.status_code == 200
    conversation = response.json()
    assert conversation["title"] == "Test Conversation"
    assert conversation["description"] == "This is a test conversation."
    assert conversation["creator_id"] == 1

    # Clean up
    response = client_conversations.delete(f"/api/{prefix}/conversations/{conversation_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_read_conversations():
    response = client_conversations.get(f"/api/{prefix}/conversations/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Check if it returns a list of conversations


def test_update_conversation():
    # Create a conversation first
    response = client_conversations.post(f"/api/{prefix}/conversations/", json={
        "title": "Test Conversation",
        "description": "This is a test conversation.",
        "creator_id": 1
    })
    conversation_id = response.json()["id"]

    response = client_conversations.patch(f"/api/{prefix}/conversations/{conversation_id}", json={"description": "Updated description"})
    assert response.status_code == 200
    updated_conversation = response.json()
    assert updated_conversation["description"] == "Updated description"

    # Clean up
    response = client_conversations.delete(f"/api/{prefix}/conversations/{conversation_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_delete_conversation():
    # Create a conversation first
    response = client_conversations.post(f"/api/{prefix}/conversations/", json={
        "title": "Test Conversation",
        "description": "This is a test conversation.",
        "creator_id": 1
    })
    conversation_id = response.json()["id"]

    response = client_conversations.delete(f"/api/{prefix}/conversations/{conversation_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # Try to get the deleted conversation (should return 404)
    response = client_conversations.get(f"/api/{prefix}/conversations/{conversation_id}")
    assert response.status_code == 404
