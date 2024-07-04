from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sentry_sdk import capture_message
from service.bookmark_service import get_bookmark_service
from werkzeug.exceptions import NotFound
from http import HTTPStatus

blueprint = Blueprint("bookmark", __name__, url_prefix="/api/v1")


@blueprint.route("/<movie_id>/bookmark", methods=["POST"])
@jwt_required
def add_bookmark(movie_id: int):
    user_id = get_jwt_identity()

    bookmark_service = get_bookmark_service()
    bookmark_service.create({"movie_id": movie_id, "user_id": user_id})
    capture_message(f"Bookmark has been added successfully for user {user_id} and movie {movie_id}")

    return jsonify({"success": True}), HTTPStatus.OK


@blueprint.route("/<movie_id>/bookmark", methods=["DELETE"])
@jwt_required
def delete_bookmark(movie_id: int):
    user_id = get_jwt_identity()

    bookmark_service = get_bookmark_service()
    bookmark = bookmark_service.get_by_movie_id_and_user_id(movie_id, user_id)

    if not bookmark:
        capture_message(f"Bookmark not found for user {user_id} and movie {movie_id}")
        raise NotFound(description="Bookmark not found")

    bookmark_service.delete(bookmark)

    capture_message(f"Bookmark has been deleted successfully for user {user_id} and movie {movie_id}")
    return jsonify({"success": True}), HTTPStatus.OK
