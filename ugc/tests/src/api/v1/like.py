import sys
from http import HTTPStatus
from unittest.mock import patch

import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from main import db, ugc_blueprint
from models.like import Like

sys.path.append("ugc/api/src/")


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test_secret"
    db.init_app(app)
    app.register_blueprint(ugc_blueprint)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def access_token(app):
    with app.app_context():
        return create_access_token(identity=1)


@patch("models.like.Like.query")
@patch("models.like.db.session")
def test_add_like(mock_session, mock_query, client, access_token):
    mock_query.filter_by.return_value.first.return_value = None

    response = client.post("/ugc/api/v1/123/like", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == HTTPStatus.OK
    assert mock_session.add.called
    assert mock_session.commit.called


@patch("models.like.Like.query")
@patch("models.like.db.session")
def test_add_dislike(mock_session, mock_query, client, access_token):
    mock_query.filter_by.return_value.first.return_value = None

    response = client.post("/ugc/api/v1/123/dislike", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == HTTPStatus.OK
    assert mock_session.add.called
    assert mock_session.commit.called


# Тест для увеличения количества лайков
@patch("models.like.Like.query")
@patch("models.like.db.session")
def test_increment_like(mock_session, mock_query, client, access_token):
    mock_like = Like(movie_id=123, user_id=1, like=1, dislike=0)
    mock_query.filter_by.return_value.first.return_value = mock_like

    response = client.post("/ugc/api/v1/123/like", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == HTTPStatus.OK
    assert mock_like.like == 2
    assert mock_session.commit.called


@patch("models.like.Like.query")
@patch("models.like.db.session")
def test_increment_dislike(mock_session, mock_query, client, access_token):
    mock_like = Like(movie_id=123, user_id=1, like=0, dislike=1)
    mock_query.filter_by.return_value.first.return_value = mock_like

    response = client.post("/ugc/api/v1/123/dislike", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == HTTPStatus.OK
    assert mock_like.dislike == 2
    assert mock_session.commit.called
