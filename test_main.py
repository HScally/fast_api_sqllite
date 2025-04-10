from anyio.pytest_plugin import pytest_configure
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool, insert
from sqlalchemy.orm import sessionmaker

import pytest

from main import app, get_db
import models

client = TestClient(app)

# move this to test utils class
TEST_DATABASE_URL = "sqlite:///test_database.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()

app.dependency_overrides[get_db] = override_get_db

# TODO: Add the pytest annotation variables
# TODO: Organize test into classes
# TODO: Restructure project

@pytest.fixture()
def build_test_db():
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def populate_users():
    users_data = [
        {'name': 'Foo', 'email': "bar@gmail.com"},
        {'name': 'Mario', 'email': "mariomario@test.com"},
        {'name': 'Link', 'email': "triforceguy@test.com"}
    ]
    session = TestingSessionLocal()

    session.execute(insert(models.User), users_data)

    session.commit()

class TestMain:

    def test_create_user(self, build_test_db):
        json_obj = {
            "name": "pengu",
            "email": "hello@g.com"
        }
        response = client.post("/users/", json=json_obj)

        actual = response.json()

        assert response.status_code == 200

        assert "id" in actual
        assert actual["id"] == 1
        assert actual["name"] == "pengu"
        assert actual["email"] == "hello@g.com"

    def test_get_user(self, build_test_db, populate_users):
        response = client.get("/users/1")

        actual = response.json()

        assert response.status_code == 200

        assert actual["name"] == "Foo"
        assert actual["email"] == "bar@gmail.com"

    def test_get_missing_user(self, build_test_db):
        response = client.get("/users/1")

        assert response.status_code == 404, response.text

    def test_get_user_by_email(self, build_test_db, populate_users):
        response = client.get("/users/email/mariomario@test.com")

        actual = response.json()

        assert actual["name"] == "Mario"

    def test_missing_get_user_by_email(self, build_test_db):
        response = client.get("/users/email/does_not_exist@test.com")

        assert response.status_code == 404, response.text

    def test_get_users(self, build_test_db, populate_users):
        response = client.get("/users")

        actual = response.json()

        assert len(actual) == 3
        assert actual[0]["name"] == "Foo"
        assert actual[0]["email"] == "bar@gmail.com"

    def test_get_users_with_limit(self, build_test_db, populate_users):
        response = client.get("/users?limit=1")

        actual = response.json()

        assert len(actual) == 1
        assert actual[0]["name"] == "Foo"
        assert actual[0]["email"] == "bar@gmail.com"

    def test_update_user(self, build_test_db, populate_users):
        json_obj = {
            "name": "Luigi",
            "email": "luigimario@test.com"
        }

        response = client.put("/users/2", json=json_obj)

        actual = response.json()

        assert response.status_code == 200

        assert actual["id"] == 2
        assert actual["name"] == "Luigi"
        assert actual["email"] == "luigimario@test.com"

    def test_update_user_empty_payload(self, build_test_db, populate_users):
        json_obj = {
            "email": "mario@test.com"
        }

        response = client.put("/users/2", json=json_obj)

        actual = response.json()

        assert response.status_code == 200

        assert actual["id"] == 2
        assert actual["name"] == ""
        assert actual["email"] == "mario@test.com"

    def test_patch_user(self, build_test_db, populate_users):
        json_obj = {
            "name": "Kirby"
        }

        response = client.patch("/users/2", json=json_obj)

        actual = response.json()

        assert response.status_code == 200

        assert actual["id"] == 2
        assert actual["name"] == "Kirby"
        assert actual["email"] == "mariomario@test.com"

    def test_patch_user_empty_payload(self, build_test_db, populate_users):
        response = client.patch("/users/2", json={})

        actual = response.json()

        assert response.status_code == 200

        assert actual["id"] == 2
        assert actual["name"] == "Mario"
        assert actual["email"] == "mariomario@test.com"

    def test_patch_user_not_found(self, build_test_db):
        response = client.patch("/users/1", json={})

        assert response.status_code == 404, response.text

    def test_delete_user(self, build_test_db, populate_users):
        response = client.delete("/users/3")

        actual = response.json()

        assert response.status_code == 200

        assert actual["id"] == 3
        assert actual["name"] == "Link"
        assert actual["email"] == "triforceguy@test.com"

        response = client.get("/user/3")

        assert response.status_code == 404, response.text