import pytest
import httpx

KEYCLOAK_URL = "http://localhost:8080"
REALM = "fastapi-library"
CLIENT_ID = "fastapi-library"
CLIENT_SECRET = "UnejAGrjZvBGjxRefFNHoQ6cBEIfVpl1"
DOMAIN_URL = "http://localhost:8000"
FASTAPI_URL = f"{DOMAIN_URL}/api"

ADMIN_USER = "admin"
ADMIN_PASS = "admin"
TEST_USER = "user"
TEST_PASS = "user"

def get_token(username, password):
    data = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": username,
        "password": password,
    }
    url = f"{DOMAIN_URL}/token"
    response = httpx.post(url, data=data)
    assert response.status_code == 200, f"Token error: {response.text}"
    return response.json()["access_token"]

@pytest.fixture(scope="session")
def admin_token():
    return get_token(ADMIN_USER, ADMIN_PASS)

@pytest.fixture(scope="session")
def user_token():
    return get_token(TEST_USER, TEST_PASS)

def test_access_protected_without_token():
    response = httpx.get(f"{FASTAPI_URL}/bookmark/list/")
    assert response.status_code == 401

def test_access_protected_with_invalid_token():
    headers = {"Authorization": "Bearer invalidtoken"}
    response = httpx.get(f"{FASTAPI_URL}/bookmark/list/", headers=headers)
    assert response.status_code == 401

def test_admin_can_list_users(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = httpx.get(f"{FASTAPI_URL}/user/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_user_cannot_list_users(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = httpx.get(f"{FASTAPI_URL}/user/", headers=headers)
    assert response.status_code in (401, 403)

def test_user_crud_bookmarks(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Create
    data = {"title": "pytest bookmark", "url": "https://pytest.org"}
    response = httpx.post(f"{FASTAPI_URL}/bookmark/", json=data, headers=headers)
    assert response.status_code == 201
    bookmark = response.json()
    bookmark_id = bookmark["id"]

    # List
    response = httpx.get(f"{FASTAPI_URL}/bookmark/list/", headers=headers)
    assert response.status_code == 200
    bookmarks = response.json()
    assert any(b["id"] == bookmark_id for b in bookmarks)

    # Update
    update_data = {"id": bookmark_id, "title": "pytest bookmark updated"}
    response = httpx.patch(f"{FASTAPI_URL}/bookmark/", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "pytest bookmark updated"

    # Delete
    response = httpx.delete(f"{FASTAPI_URL}/bookmark/", params={"bookmark_id": bookmark_id}, headers=headers)
    assert response.status_code == 204

def test_user_cannot_delete_others_bookmark(user_token, admin_token):
    # Admin creates a bookmark (debe enviar user_id)
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    # Para el test, el admin se crea un bookmark para sí mismo (puedes cambiar el user_id si quieres)
    data = {"title": "admin bookmark", "url": "https://admin.org", "user_id": 1}
    response = httpx.post(f"{FASTAPI_URL}/bookmark/", json=data, headers=headers_admin)
    assert response.status_code == 201
    bookmark_id = response.json()["id"]

    # User tries to delete admin's bookmark
    headers_user = {"Authorization": f"Bearer {user_token}"}
    response = httpx.delete(f"{FASTAPI_URL}/bookmark/", params={"bookmark_id": bookmark_id}, headers=headers_user)
    assert response.status_code in (401, 403, 404)

    # Cleanup: admin deletes the bookmark
    response = httpx.delete(f"{FASTAPI_URL}/bookmark/", params={"bookmark_id": bookmark_id}, headers=headers_admin)
    assert response.status_code == 204

def test_create_bookmark_invalid_data(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    data = {"title": ""}  # Missing URL
    response = httpx.post(f"{FASTAPI_URL}/bookmark/", json=data, headers=headers)
    assert response.status_code == 422

def test_not_found_bookmark(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = httpx.get(f"{FASTAPI_URL}/bookmark/999999", headers=headers)
    assert response.status_code == 404