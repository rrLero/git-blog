from flask_restful import reqparse, abort, Resource
from models.gitaccess import GitAccess
from flask import jsonify


parser = reqparse.RequestParser()
parser.add_argument('access_token')


def auth():
    args = parser.parse_args()
    access_token = args.get('access_token')
    if not access_token:
        return False
    return access_token


class Likes(Resource):
    def get(self, git_name, git_repository_blog, id_comment):
        access_token = auth()
        if not access_token:
            return {'access_token': access_token}, 401
        git_access = GitAccess(git_name, git_repository_blog, access_token)
        likes = git_access.get_reaction(id_comment)
        list_likes = [one_like for one_like in likes.json()]
        return list_likes

    def post(self, git_name, git_repository_blog, id_comment):
        access_token = auth()
        if not access_token:
            return {'access_token': access_token}, 401
        git_access = GitAccess(git_name, git_repository_blog, access_token)
        root_parser = parser.add_argument('content', required=True, type=str, location='json')
        json_data = root_parser.parse_args(strict=True)
        create_like = git_access.create_reaction(id_comment, json_data)
        return '', create_like.status_code



