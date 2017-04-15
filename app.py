# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, session, flash, redirect, url_for, jsonify, abort
import json
import os
import copy

from flask import make_response, request, current_app
from models.users import Users
from models.pagination import Pagination
from models.gitaccess import GitAccess
from models.gitgetallposts import GitGetAllPosts
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
app.config.from_object(__name__)
app.config.update(dict(
    SECRET_KEY='development key',
    DATABASE=os.path.join(app.root_path, 'git-blog.sqlite'),
    README=os.path.join(app.root_path, 'README.md'),
))


# Получение данных из файла, если такой есть
def try_file(git_name, git_repository_blog, ref=False):
    if not ref:
        try:
            f = open('static/%s_%s.txt' % (git_name.lower(), git_repository_blog.lower()))
            temp = f.readline()
        except:
            return False
        if temp:
            file = sorted(json.loads(temp), key=lambda d: d['date'], reverse=True)
            return file
        else:
            return False
    elif ref:
        try:
            f = open('static/%s_%s_branch.txt' % (git_name.lower(), git_repository_blog.lower()))
            temp = f.readline()
        except:
            return False
        if temp:
            file = sorted(json.loads(temp), key=lambda d: d['date'], reverse=True)
            return file
        else:
            return False


# Функция для получения списка тем из постов
def get_tags(file):
    tags = []
    for i in file:
        for j in i['tags']:
            tags.append(j)
    tags = list(set(tags))
    return tags


# Функция получает список постов и тег, а отдает список постов только с этим тегом отсортированные по дате
def sorted_by_tags(list, tag):
    sorted_list = []
    for one_post in list:
        if tag in one_post['tags']:
            sorted_list.append(one_post)
    return sorted(sorted_list, key=lambda d: d['date'], reverse=True)


def search(data, key, args):
    query_length = len(args)
    search_result = []
    for i in data:
        key_value = i[key][:query_length].lower()
        if key_value == args.lower():
            search_result.append({'title': i['title'], 'id': i['id']})
    return jsonify(search_result)
# Получение данных для пагинации исходя из количество постов на странице, количества постов, и текущей страницы


# начальная страница
@app.route('/index')
@app.route('/')
def homepage():
    return render_template('base.html')


@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    # Если пришли формы то запоминает их в переменные
    if request.form['git_name'] and request.form['git_repository_blog']:
        git_name = request.form['git_name']
        git_repository_blog = request.form['git_repository_blog']
        flash('Welcome to Big-Blog %s' % git_name)
        return redirect(url_for('blog', git_name=git_name, git_repository_blog=git_repository_blog))
    else:
        return redirect(url_for('homepage'))


# redirect on page not_found.html
@app.errorhandler(404)
def page_not_found(e):
    return render_template('not_found.html'), 404


@app.route('/<git_name>/<git_repository_blog>/<int:page>/<tags>')
@app.route('/<git_name>/<git_repository_blog>/<int:page>/')
@app.route('/<git_name>/<git_repository_blog>/')
def blog(git_name, git_repository_blog, tags=None, page=1):
    # Если существует файл с данными то обращается к файлу если нет то берет с гита
    file = try_file(git_name, git_repository_blog)
    if file:
        if tags:
            file = sorted_by_tags(file, tags)
        paginate = Pagination(3, page, len(file))
        return render_template('blog.html', git_name=git_name, git_repository_blog=git_repository_blog, file=file,
                               paginate=paginate, page=page, tags=tags)
    else:
        git_access = GitGetAllPosts(git_name, git_repository_blog)
        file = git_access.get_file()
        if file:
            if tags:
                file = sorted_by_tags(file, tags)
            paginate = Pagination(3, page, len(file))
            return render_template('blog.html', git_name=git_name, git_repository_blog=git_repository_blog, file=file,
                                   paginate=paginate, page=page, tags=tags)
        else:
            return redirect(url_for('homepage'))


# берет конкретный пост и отображает его при нажатии на readmore
@app.route('/<git_name>/<git_repository_blog>/<int:page>/post/<title>/')
def post(git_name, git_repository_blog, title, page=1, tags=None):
    f = open('static/%s_%s.txt' % (git_name.lower(), git_repository_blog.lower()))
    temp = f.readline()
    if temp:
        file = sorted(json.loads(temp), key=lambda d: d['date'], reverse=True)
        return render_template('post.html', file=file, title=title, git_repository_blog=git_repository_blog, git_name=git_name, page=page)
    else:
        return jsonify({'message': 'no such post'})


# Апи отдает данные с гита
@app.route('/<git_name>/<git_repository_blog>/api/get/<title>', methods=['GET'])
@app.route('/<git_name>/<git_repository_blog>/api/get/tags/<tag>', methods=['GET'])
@app.route('/<git_name>/<git_repository_blog>/api/get/id/<id>', methods=['GET'])
@app.route('/<git_name>/<git_repository_blog>/api/get', methods=['GET'])
@cross_origin()
def get_get_blog(git_name, git_repository_blog, title=None, id=None, tag=None):
    args = request.args.get('access_token')
    per_page = request.args.get('per_page')
    page = request.args.get('page')
    data = try_file(git_name, git_repository_blog)
    if not data:
        git_access = GitGetAllPosts(git_name, git_repository_blog, args)
        data = git_access.get_file()
        if not data:
            create_repo = git_access.create_repo(git_repository_blog)
            if create_repo.status_code == 201:
                git_access.get_file()
                users_list = Users(git_name, git_repository_blog)
                users_list.new_user()
                return jsonify({'message': 'new repo created'})
            elif create_repo.status_code == 422:
                users_list = Users(git_name, git_repository_blog)
                users_list.new_user()
                return jsonify({'message': 'repo is empty'})
            else:
                return jsonify({'message': 'unable create repo'})
    data_1 = copy.deepcopy(data)
    data_preview = []
    for j in data_1:
        try:
            del j['text_full_strings']
            del j['comments_for_post']
        except:
            pass
        data_preview.append(j)
    if tag:
        tag_data = sorted_by_tags(data_preview, tag)
        count = len(tag_data)
        paginate = Pagination(per_page, page, count)
        return jsonify({'items': tag_data[paginate.first_post:paginate.last_post+1], 'total': count})
    if title:
        one_post = [post for post in data if post['title'] == title]
        one_post.append({'message': 'no such post'})
        return jsonify(one_post[0])
    elif id:
        one_post = [post for post in data if post['id'] == id]
        one_post.append({'message': 'no such post'})
        return jsonify(one_post[0])
    else:
        args = request.args.get('title', '')
        if args:
            return search(data, 'title', args)
        else:
            count = len(data_preview)
            paginate = Pagination(per_page, page, count)
            return jsonify({'items': data_preview[paginate.first_post:paginate.last_post+1], 'total': count})


@app.route('/<git_name>/<git_repository_blog>/api/update', methods=['GET', 'POST'])
@app.route('/<git_name>/<git_repository_blog>/api/web_hook', methods=['GET', 'POST'])
@cross_origin()
def web_hook(git_name, git_repository_blog):
    args = request.args.get('access_token')
    ref = request.args.get('ref')
    git_access = GitGetAllPosts(git_name, git_repository_blog, args)
    if ref:
        git_access.get_file(ref)
        return '', 200
    git_access.get_file()
    return '', 200


# Функция для обработки изменений постов на ГитХабе
@app.route('/<git_name>/<git_repository_blog>/api/put/<id_file>/<sha>', methods=['POST', 'PUT', 'DELETE'])
@app.route('/<git_name>/<git_repository_blog>/api/put', methods=['POST', 'PUT', 'DELETE'])
@cross_origin()
def add_file(git_name, git_repository_blog, sha=None, id_file=None):
    args = request.args.get('access_token')
    if not args:
        return jsonify({'access_token': args})
    git_access = GitAccess(git_name, git_repository_blog, args)
    changes = request.json
    if request.method == 'POST':
        res = git_access.edit_post(changes, sha, id_file)
    elif request.method == 'PUT':
        res = git_access.new_post(changes)
        if res.status_code == 404 and res.json()['message'] == 'Branch post_branch not found':
            sha = (git_access.get_one_branch('master')).json()['object']['sha']
            git_access.create_branch(sha)
            res = git_access.new_post(changes)
    elif request.method == 'DELETE':
        path = 'posts/' + str(id_file)
        res = git_access.del_one_post(sha, path)
    else:
        return '', 404
    return '', res.status_code


# Функция для получения токена
@app.route('/<git_name>/<git_repository_blog>/api/oauth', methods=['GET', 'POST', 'PUT'])
@cross_origin()
def oauth(git_name, git_repository_blog):
    args = request.args.get('code')
    if not args:
        return jsonify({'access_token': args})
    git_access = GitAccess(git_name, git_repository_blog, args)
    access_token = git_access.get_access_token(args)
    access_token = access_token.json()
    return jsonify(access_token)


# Функция для получения списка блогов юзера
@app.route('/api/blog_list', methods=['GET'])
@cross_origin()
def blog_list():
    users_list = Users('none', 'none')
    session_git = users_list.open_base()
    users = session_git.query(Users)
    blog_list_ = [{'name':(user.user_name).lower(), 'repo': (user.user_repo_name).lower()} for user in users]
    return jsonify(blog_list_)


# Проверка на коллаборатора
@app.route('/api/repo_master/<git_name>/<git_repository_blog>/<test_user>', methods=['GET'])
@cross_origin()
def repo_master(git_name, git_repository_blog, test_user):
    args = request.args.get('access_token')
    if not args:
        return jsonify({'access_token': args})
    git_access = GitAccess(git_name, git_repository_blog, args)
    test = git_access.test_user_rights(test_user)
    if test.status_code == 200:
        return jsonify({'access': True})
    else:
        return jsonify({'access': False})


# Получение комментариев из файла
@app.route('/<git_name>/<git_repository_blog>/api/get_comments_file', methods=['GET'])
@cross_origin()
def get_comments_from_file(git_name, git_repository_blog):
    args = request.args.get('access_token')
    # f = open('static/comments_%s_%s.json' % (git_name, git_repository_blog))
    with open('static/comments_%s_%s.json' % (git_name, git_repository_blog)) as comment_file:
        json_data = [json.loads(line) for line in comment_file]
    if json_data:
        return json_data
    else:
        return jsonify({'message': 'No comments in file'})


# Получение комментариев
@app.route('/<git_name>/<git_repository_blog>/api/get_comments/<id_file>', methods=['GET', 'PUT', 'DELETE', 'POST'])
@app.route('/<git_name>/<git_repository_blog>/api/get_comments', methods=['GET'])
@cross_origin()
def get_dict_all_comments(git_name, git_repository_blog, id_file=None):
    args = request.args.get('access_token')
    git_access = GitAccess(git_name, git_repository_blog, args)
    if request.method == 'GET':
        list_coms = git_access.get_comments()
        if id_file:
            if id_file in list_coms:
                return jsonify(list_coms[id_file])
            else:
                return jsonify([])
        else:
            return jsonify(list_coms)
    elif request.method == 'DELETE' and args:
        del_comment = git_access.del_comment(id_file)
        return '', del_comment.status_code
    elif request.method == 'POST' and args:
        data_issues = git_access.data_issue_json()
        data_issues = data_issues.json()
        data_body = request.json
        if len(data_issues) > 0:
            for issue in data_issues:
                if issue['title'] == id_file:
                    add_new = git_access.add_comment(issue['number'], data_body)
                    get_id = {}
                    if add_new.status_code == 201:
                        git_access = GitAccess(git_name, git_repository_blog, args)
                        get_id = git_access.get_comments()
                        get_id = [el for el in get_id[id_file] if el['created_at'] == add_new.json()['created_at']]
                        file_comments = open('comments_%s_%s.json' % (git_name, git_repository_blog), 'a')
                        file_comments.write(json.dumps(get_id) + '\n')
                        file_comments.close()
                    return jsonify(get_id)
        add_new_issue = git_access.add_new_issue(id_file)
        if add_new_issue.status_code == 201:
            add_new = git_access.add_comment(add_new_issue.json()['number'], data_body)
            get_id = {}
            if add_new.status_code == 201:
                git_access = GitAccess(git_name, git_repository_blog, args)
                get_id = git_access.get_comments()
                get_id = [el for el in get_id[id_file] if el['created_at'] == add_new.json()['created_at']]
                file_comments = open('static/comments_%s_%s.json' % (git_name, git_repository_blog), 'a')
                file_comments.write(json.dumps(get_id) + '\n')
                file_comments.close()
            return jsonify(get_id)
        else:
            return jsonify({})
    elif request.method == 'PUT' and args:
        data_body = request.json
        edit_comment = git_access.edit_comment(id_file, data_body)
        return '', edit_comment.status_code
    return jsonify({'message': 'No access token in request, try again'})


@app.route('/<git_name>/<git_repository_blog>/api/lock_comments/<id_file>', methods=['GET', 'DELETE'])
def lock_comments(git_name, git_repository_blog, id_file=None):
    args = request.args.get('access_token')
    if not args:
        return jsonify({'access_token': args})
    git_access = GitAccess(git_name, git_repository_blog, args)
    data_issues = git_access.data_issue_json()
    data_issues = data_issues.json()
    if len(data_issues) > 0:
        for issue in data_issues:
            if issue['title'] == id_file:
                if request.method == 'GET':
                    lock_issue = git_access.lock_issue(issue['number'])
                    if lock_issue.status_code == 204:
                        return jsonify({'status': False})
                    else:
                        return jsonify({'status': True})
                elif request.method == 'DELETE':
                    lock_issue = git_access.unlock_issue(issue['number'])
                    if lock_issue.status_code == 204:
                        return jsonify({'status': True})
                    else:
                        return jsonify({'message': 'error'})
    add_new_issue = git_access.add_new_issue(id_file)
    if add_new_issue.status_code == 201:
        if request.method == 'GET':
            lock_issue = git_access.lock_issue(add_new_issue.json()['number'])
            if lock_issue.status_code == 204:
                return jsonify({'status': False})
            else:
                jsonify({'status': True})
    else:
        jsonify({'status': True})


@app.route('/<git_name>/<git_repository_blog>/api/lock_status/<id_file>', methods=['GET'])
def lock_status(git_name, git_repository_blog, id_file=None):
    args = request.args.get('access_token')
    git_access = GitAccess(git_name, git_repository_blog, args)
    return jsonify({'status': git_access.lock_status_comment(id_file)})


@app.route('/<git_name>/<git_repository_blog>/api/del_repo', methods=['DELETE', 'GET', 'POST'])
@cross_origin()
def del_repo(git_name, git_repository_blog):
    args = request.args.get('access_token')
    if not args:
        return jsonify({'access_token': args})
    git_access = GitAccess(git_name, git_repository_blog, args)
    data = git_access.get_all_posts()
    users_list = Users(git_name, git_repository_blog)
    session_git = users_list.open_base()
    users = session_git.query(Users)
    if data.status_code == 200:
        for dir_ in data.json():
            git_access.del_one_post(dir_['sha'], dir_['path'])
        for user in users:
            if user.user_name == git_name.lower() and user.user_repo_name == git_repository_blog.lower():
                session_git.delete(user)
        session_git.commit()
        session_git.close()
        git_access.del_branch()
        return '', 200
    else:
        for user in users:
            if user.user_name == git_name.lower() and user.user_repo_name == git_repository_blog.lower():
                session_git.delete(user)
        session_git.commit()
        session_git.close()
        git_access.del_branch()
        return '', 200


@app.route('/api/pagination', methods=['GET', 'POST'])
@cross_origin()
def pagination():
    page_args = request.json
    try:
        paginate = Pagination(page_args['per_page'], page_args['page'], page_args['count'])
        return jsonify({'has_next': paginate.has_next, 'has_prev': paginate.has_prev, 'first_post': paginate.first_post, 'last_post': paginate.last_post})
    except:
        return jsonify({'message': 'no params required received'})


@app.route('/<git_name>/<git_repository_blog>/api/get_branch_posts', methods=['GET'])
@cross_origin()
def get_branch_posts(git_name, git_repository_blog):
    args = request.args.get('access_token')
    per_page = request.args.get('per_page')
    page = request.args.get('page')
    if not args:
        return jsonify({'access_token': args})
    git_access = GitGetAllPosts(git_name, git_repository_blog, args)
    ref = True
    branch_posts = try_file(git_name, git_repository_blog, ref)
    if not branch_posts:
        branch_posts = git_access.get_posts_json('post_branch')
    list_branch_post = []
    if branch_posts:
        posts = try_file(git_name, git_repository_blog)
        if not posts:
            posts = git_access.get_posts_json()
            if not posts:
                posts = []
        for branch_post in branch_posts:
            if branch_post not in posts:
                list_branch_post.append(branch_post)
        branch_posts = sorted(list_branch_post, key=lambda d: d['date'], reverse=True)
        count = len(branch_posts)
        paginate = Pagination(per_page, page, count)
        return jsonify({'items': branch_posts[paginate.first_post:paginate.last_post + 1], 'total': count})
    else:
        return jsonify({"items": [], "total": 0})


@app.route('/<git_name>/<git_repository_blog>/api/branch/remove/<id_file>', methods=['DELETE', 'GET', 'POST', 'PUT'])
@cross_origin()
def remove_post_to_master(git_name, git_repository_blog, id_file):
    args = request.args.get('access_token')
    if not args:
        return jsonify({'access_token': args})
    git_access = GitGetAllPosts(git_name, git_repository_blog, args)
    ref = True
    data = git_access.get_one_post(id_file, ref)
    status = 404
    if data.status_code != 200:
        return '', data.status_code
    sha = data.json()['sha']
    path = data.json()['path']
    if request.method == 'PUT':
        status = data.status_code
        content = data.json()['content']
        ref = False
        new_post = git_access.new_post(content, ref, id_file)
        if new_post.status_code == 201:
            ref = True
            del_post = git_access.del_one_post(sha, path, ref)
            status = del_post.status_code
        return '', status
    elif request.method == 'DELETE':
        if data.status_code == 200:
            ref = True
            del_post = git_access.del_one_post(sha, path, ref)
            status = del_post.status_code
        return '', status
    elif request.method == 'POST':
        changes = request.json
        ref = True
        edit = git_access.edit_post(changes, sha, id_file, ref)
        status = edit.status_code
        return '', status
    elif request.method == 'GET':
        ref = True
        all_post_data = try_file(git_name, git_repository_blog, ref)
        if not all_post_data:
            all_post_data = git_access.get_file(ref)
        for one_post in all_post_data:
            if id_file == one_post['id']:
                return jsonify(one_post)


@app.route('/<git_name>/<git_repository_blog>/api/put/master', methods=['PUT'])
def push_master(git_name, git_repository_blog):
    args = request.args.get('access_token')
    if not args:
        return jsonify({'access_token': args})
    git_access = GitAccess(git_name, git_repository_blog, args)
    changes = request.json
    ref = False
    res = git_access.new_post(changes, ref)
    return '', res.status_code


@app.after_request
def add_cors(resp):
    """ Ensure all responses have the CORS headers. This ensures any failures are also accessible
        by the client. """
    resp.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET, PUT, DELETE'
    resp.headers['Access-Control-Allow-Headers'] = request.headers.get(
        'Access-Control-Request-Headers', 'Authorization')
    # set low for debugging
    if app.debug:
        resp.headers['Access-Control-Max-Age'] = '1'
    return resp


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')