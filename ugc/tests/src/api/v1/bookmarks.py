import sys
from unittest.mock import patch

import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from http import HTTPStatus

sys.path.append("ugc/api/src/")
from main import ugc_blueprint


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(ugc_blueprint)
    app.config["JWT_SECRET_KEY"] = "test_secret"
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def access_token(app):
    with app.app_context():
        return create_access_token(identity=1)


@patch("service.bookmark_service.get_bookmark_service")
def test_add_bookmark(mock_get_bookmark_service, client, access_token):
    mock_service = mock_get_bookmark_service.return_value
    mock_service.create.return_value = None

    response = client.post("/api/v1/123/bookmark", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == HTTPStatus.OK
    assert response.json == {"success": True}
    mock_service.create.assert_called_once_with({"movie_id": 123, "user_id": 1})


@patch("service.bookmark_service.get_bookmark_service")
def test_delete_bookmark_success(mock_get_bookmark_service, client, access_token):
    mock_service = mock_get_bookmark_service.return_value
    mock_service.get_by_movie_id_and_user_id.return_value = {
        "id": 1,
        "movie_id": 123,
        "user_id": 1,
    }
    mock_service.delete.return_value = None

    response = client.delete("/api/v1/123/bookmark", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == HTTPStatus.OK
    assert response.json == {"success": True}
    mock_service.delete.assert_called_once_with({"id": 1, "movie_id": 123, "user_id": 1})


@patch("service.bookmark_service.get_bookmark_service")
def test_delete_bookmark_not_found(mock_get_bookmark_service, client, access_token):
    mock_service = mock_get_bookmark_service.return_value
    mock_service.get_by_movie_id_and_user_id.return_value = None

    response = client.delete("/api/v1/123/bookmark", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {"message": "Bookmark not found"}
