# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, session, flash, redirect, url_for, jsonify, abort
import datetime
import json
import requests
import math
import os
import base64
from flask import make_response, request, current_app
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models.users import Users
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
app.config.from_object(__name__)
app.config.update(dict(
    SECRET_KEY='development key',
    DATABASE=os.path.join(app.root_path, 'git-blog.sqlite'),
    README=os.path.join(app.root_path, 'README.md'),
))


# функция открывает базу данных для последующей работы с ней
def open_base():
    Base = declarative_base()
    engine = create_engine('sqlite:///git-blog.sqlite')
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session_git = DBSession()
    return session_git


# функция получает строку и в ней находит(если есть) дату, пока в двух вариантах %y-%m-%d %H:%M и %y-%m-%d
# и приводит к стандартному виду
def get_date(string_date):
    for i in range(len(string_date)):
        try:
            date_string = datetime.datetime.strptime(string_date[i:i+14], "%y-%m-%d %H:%M")
        except:
            date_string = False
        if date_string is False:
            try:
                date_string = datetime.datetime.strptime(string_date[i:i + 8], "%y-%m-%d")
                return str(date_string)
            except:
                date_string = False
        if date_string:
            return str(date_string)
    if date_string is False:
        return 'No Date'


# Функция получает имя пользователя и репозиторий. при помощи АПИ ГИТА функция переберает файлы и создает словарь из
# постов
def get_file(git_name, git_repository):
    list_git_files = []
    git_objects = requests.get('https://api.github.com/repos/%s/%s/contents/posts?client_id=fcdfab5425d0d398e2e0&client_secret=355b83ee2e195275e33a4d2e113a085f6eaea0a2' % (git_name, git_repository))
    git_objects = git_objects.json()
    f = open('testrate.txt', 'w')
    f.write(str(git_objects))
    f.close()
    f = open('static/%s_%s.txt' % (git_name, git_repository), 'w')
    f.close()
    if str(type(git_objects)) == "<class 'dict'>":
        session['logged_in'] = False
        return False
    for git_object in git_objects:
        if git_object['type'] == 'file':
            # url = git_object['download_url']
            url = 'https://api.github.com/repos/%s/%s/contents/posts/%s?client_id=fcdfab5425d0d398e2e0&client_secret=355b83ee2e195275e33a4d2e113a085f6eaea0a2' % (git_name, git_repository, git_object['name'])
            val = {}
            resource = requests.get(url)
            resource = resource.json()
            data = resource['content']
            data = base64.b64decode(data)
            data = data.decode('utf-8')
            # data = resource.content.decode('utf-8')
            full_string = data
            if '\n' in data:
                data = [i for i in data.split('\n')]
                try:
                    data.remove('')
                except:
                    pass
            elif '\r' in data:
                data = [i for i in data.split('\r')]
            val['title'] = 'No title'
            val['sha'] = git_object['sha']
            val['id'] = git_object['name']
            val['date'] = get_date(git_object['name'])
            val['tags'] = 'No tags,'
            val['author'] = 'No author'
            val['layout'] = 'No layout'
            val['text_full_strings'] = ''
            val['text_full_md'] = ''
            counter = 0
            for i in range(len(data)):
                if '---' == data[i]:
                    counter += 1
                if counter == 2:
                    break
                key, string = test_string(data[i])
                if key and string:
                    val[key] = string
            val['text_full_strings'] = full_string[full_string.rfind('---')+3:]
            val['text_full_md'] = full_string
            list_git_files.append(val)
    f = open('static/%s_%s.txt' % (git_name, git_repository), 'w')
    f.write(json.dumps(list_git_files))
    f.close()
    return sorted(list_git_files, key=lambda d: d['date'], reverse=True)


# функция к которой обращается предидущая функция для получения заголовков отделенных ---   ---
def test_string(test):
    if 'title:' in test and ':' in test:
        return 'title', test[test.find('title:')+len('title:'):].strip()
    elif 'tags' in test and ':' in test:
        test = test[test.find('tags:')+len('tags:'):].strip()
        if ',' in test:
            tags = [j.strip() for j in test.split(',')]
        else:
            tags = [test]
        return 'tags', tags
    elif 'layout' in test and ':' in test:
        return 'layout', test[test.find('layout:')+len('layout:'):].strip()
    elif 'date' in test and ':' in test:
        test = test[test.find('date:') + len('date:'):].strip()
        test = test.strip('"')
        return 'date', get_date(test)
    elif 'author' in test and ':' in test:
        return 'author', test[test.find('author:')+len('author:'):].strip()
    else:
        return None, None


# Получение данных из файла, если такой есть
def try_file(git_name, git_repository_blog):
    try:
        f = open('static/%s_%s.txt' % (git_name, git_repository_blog))
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


# Получение данных для пагинации исходя из количество постов на странице, количества постов, и текущей страницы
class Pagination:
    def __init__(self, per_page, page, count):
        self.per_page = per_page
        self.page = page
        self.count = count
        self.first_post = self.per_page * (self.page - 1)
        self.last_post = self.per_page * (self.page - 1) + self.per_page - 1
        if self.last_post >= count - 1:
            self.last_post = count - 1
        if self.first_post > 1:
            self.has_prev = True
        else:
            self.has_prev = False
        if self.page < math.ceil(self.count/self.per_page):
            self.has_next = True
        else:
            self.has_next = False
        if self.page > 1:
            self.prev_num = page - 1
        else:
            self.prev_num = False
        if self.page < math.ceil(self.count/self.per_page):
            self.next_num = self.page + 1
        else:
            self.next_num = False

    def first_post(self):
        return self.first_post

    def last_post(self):
        return self.last_post

    def has_prev(self):
        return self.has_prev

    def has_next(self):
        return self.has_next


# начальная страница
@app.route('/index')
@app.route('/')
def homepage():
    return render_template('base.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('homepage'))


@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    # Если пришли формы то запоминает их в переменные
    session['logged_in'] = False
    if request.form['git_name'] and request.form['git_repository_blog']:
        git_name = request.form['git_name']
        git_repository_blog = request.form['git_repository_blog']
        # Обновляем файл с данными
        session_git = open_base()
        users = session_git.query(Users)
        for user in users:
            if user.user_name == git_name and user.user_repo_name == git_repository_blog:
                session['logged_in'] = True
                session_git.close()
                flash('Welcome to Big-Blog %s' %git_name)
                session['logged_in'] = True
                return redirect(url_for('blog', git_name=git_name, git_repository_blog=git_repository_blog))

        file = get_file(git_name, git_repository_blog)
        if file:
            session_git = open_base()
            new_user = Users(user_name=git_name, user_repo_name=git_repository_blog)
            session_git.add(new_user)
            session_git.commit()
            session_git.close()
            session['logged_in'] = True
            flash('You were registered')
            session['logged_in'] = True
            return redirect(url_for('blog', git_name=git_name, git_repository_blog=git_repository_blog))
        else:
            flash('Your name or user name incorrect')
            return redirect(url_for('homepage'))
    else:
        return redirect(url_for('homepage'))


def search(data, key, args):
    query_length = len(args)
    search_result = []
    for i in data:
        key_value = i[key][:query_length].lower()
        if key_value == args.lower():
            search_result.append({'title': i['title'], 'id': i['id']})
    return jsonify(search_result)


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
        session['logged_in'] = True
        if tags:
            file = sorted_by_tags(file, tags)
        paginate = Pagination(3, page, len(file))
        return render_template('blog.html', git_name=git_name, git_repository_blog=git_repository_blog, file=file,
                               paginate=paginate, page=page, tags=tags)
    else:
        session['logged_in'] = False
        return redirect(url_for('homepage'))


# берет конкретный пост и отображает его при нажатии на readmore
@app.route('/<git_name>/<git_repository_blog>/<int:page>/post/<title>/')
def post(git_name, git_repository_blog, title, page=1, tags=None):
    f = open('static/%s_%s.txt' % (git_name, git_repository_blog))
    temp = f.readline()
    file = sorted(json.loads(temp), key=lambda d: d['date'], reverse=True)
    return render_template('post.html', file=file, title=title, git_repository_blog=git_repository_blog, git_name=git_name, page=page)


# Апи отдает данные с гита
@app.route('/<git_name>/<git_repository_blog>/api/get/<title>', methods=['GET'])
@app.route('/<git_name>/<git_repository_blog>/api/get/id/<id>', methods=['GET'])
@app.route('/<git_name>/<git_repository_blog>/api/get', methods=['GET'])
@cross_origin()
def get_get_blog(git_name, git_repository_blog, title=None, id=None ):
    data = try_file(git_name, git_repository_blog)
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
            return jsonify(data)


@app.route('/<git_name>/<git_repository_blog>/api/update', methods=['GET', 'POST'])
@cross_origin()
def update(git_name, git_repository_blog):
    get_file(git_name, git_repository_blog)
    return redirect(url_for('blog', git_name=git_name, git_repository_blog=git_repository_blog, tags=None, page=1))


@app.route('/<git_name>/<git_repository_blog>/api/web_hook', methods=['GET', 'POST'])
@cross_origin()
def web_hook(git_name, git_repository_blog):
    get_file(git_name, git_repository_blog)
    return '', 200


# Функция для обработки изменений постов на ГитХабе
@app.route('/<git_name>/<git_repository_blog>/api/put/<id_file>/<sha>', methods=['POST', 'PUT', 'DELETE'])
@app.route('/<git_name>/<git_repository_blog>/api/put', methods=['POST', 'PUT', 'DELETE'])
@cross_origin()
def add_file(git_name, git_repository_blog, sha=None, id_file=None):
    put_dict_git = {
      "message": "my commit message",
      "author":     {
                    "name": git_name,
                    "email": "%s@email.com" %git_repository_blog
                    },
                }
    args = request.args.get('access_token')
    changes = request.json
    if request.method == 'POST':
        file_data = changes['text_full_md']
        file_data = file_data.encode()
        file_data = base64.encodebytes(file_data)
        file_data = file_data.decode()
        put_dict_git['sha'] = sha
        put_dict_git['content'] = file_data
        url = 'https://api.github.com/repos/%s/%s/contents/posts/%s?access_token=%s' % (
                git_name, git_repository_blog, id_file, args)
        res = requests.put(url, json=put_dict_git)
    elif request.method == 'PUT':
        file_data = changes['text_full_md']
        file_name = changes['filename']
        file_data = file_data.encode()
        file_data = base64.encodebytes(file_data)
        file_data = file_data.decode()
        put_dict_git['content'] = file_data
        url = 'https://api.github.com/repos/%s/%s/contents/posts/%s?access_token=%s' %(
                git_name, git_repository_blog, file_name, args)
        res = requests.put(url, json=put_dict_git)
    elif request.method == 'DELETE':
        put_dict_git['sha'] = sha
        url = 'https://api.github.com/repos/%s/%s/contents/posts/%s?access_token=%s' % (
                git_name, git_repository_blog, id_file, args)
        res = requests.delete(url, json=put_dict_git)
    else:
        return 404
    return '', res.status_code


@app.route('/<git_name>/<git_repository_blog>/api/oauth', methods=['GET', 'POST', 'PUT'])
@cross_origin()
def oauth(git_name, git_repository_blog):
    args = request.args.get('code')
    headers = {'Accept': 'application/json'}
    access_token = requests.post('https://github.com/login/oauth/access_token?client_id=48f5b894f42ae1f869d2'
                                        '&client_secret=e289a8e72533f127ba873f0dec05908e6846866b&code=%s&'
                                        '&redirect_uri=http://acid.zzz.com.ua/%s/%s/page/1' % (args, git_name, git_repository_blog), headers=headers)
    access_token = access_token.json()
    return jsonify(access_token)


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