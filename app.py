# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, session, flash, redirect, url_for, jsonify
import datetime
import json
import requests
import math
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper


app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    SECRET_KEY='development key',
))


# accept cross-server requests, need for api
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


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
    f = open('static/%s.txt' % git_name, 'w')
    f.close()
    list_git_files = []
    git_objects = requests.get('https://api.github.com/repos/%s/%s/contents/posts/' % (git_name, git_repository))
    git_objects = git_objects.json()
    if str(type(git_objects)) == "<class 'dict'>":
        session['logged_in'] = False
        return False
    for git_object in git_objects:
        if git_object['type'] == 'file':
            url = git_object['download_url']
            val = {}
            resource = requests.get(url)
            data = resource.content.decode('utf-8')
            if '\n' in data:
                data = [i for i in data.split('\n')]
                data.remove('')
            elif '\r' in data:
                data = [i for i in data.split('\r')]
            val['date'] = get_date(git_object['name'])
            val['text'] = ''
            val['tags'] = 'No tags'
            val['author'] = ''
            val['layout'] = ''
            i = 1
            while '---' != data[i]:
                key, string = test_string(data[i])
                val[key] = string
                i += 1
            val['text'] = [data[j] for j in range(i+1, len(data))]
            list_git_files.append(val)
            f = open('static/%s.txt' % git_name, 'w')
            f.write(json.dumps(list_git_files))
            f.close()
    return sorted(list_git_files, key=lambda d: d['date'], reverse=True)


# функция к которой обращается предидущая функция для получения заголовков отделенных ---   ---
def test_string(test):
    if 'title:' in test and ':' in test:
        return 'title', test[test.find('title:')+len('title:'):].strip()
    if 'tags' in test and ':' in test:
        test = test[test.find('tags:')+len('tags:'):].strip()
        if ',' in test:
            tags = [j.strip() for j in test.split(',')]
        else:
            tags = [test]
        return 'tags', tags
    if 'layout' in test and ':' in test:
        return 'layout', test[test.find('layout:')+len('layout:'):].strip()
    if 'date' in test and ':' in test:
        test = test[test.find('date:') + len('date:'):].strip()
        test = test.strip('"')
        return 'date', get_date(test)
    if 'author' in test and ':' in test:
        return 'author', test[test.find('author:')+len('author:'):].strip()


# Получение данных из файла, если такой есть
def try_file(git_name):
    f = open('static/%s.txt' % git_name)
    temp = f.readline()
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
    if request.form['git_name'] and request.form['git_repository_blog']:
        session['logged_in'] = True
        git_name = request.form['git_name']
        git_repository_blog = request.form['git_repository_blog']
        # Обновляем файл с данными
        f = open('static/%s.txt' % git_name, 'w')
        f.close()
        return redirect(url_for('blog', git_name=git_name, git_repository_blog=git_repository_blog))
    else:
        session['logged_in'] = False
        return redirect(url_for('homepage'))


# redirect on page not_found.html
@app.errorhandler(404)
def page_not_found(e):
    return render_template('not_found.html'), 404


@app.route('/<git_name>/<git_repository_blog>/<int:page>/')
@app.route('/<git_name>/<git_repository_blog>/')
def blog(git_name, git_repository_blog, page=1):
    session['logged_in'] = True
    # Если существует файл с данными то обращается к файлу если нет то берет с гита
    if try_file(git_name):
        file = try_file(git_name)
        paginate = Pagination(3, page, len(file))
        return render_template('blog.html', git_name=git_name, git_repository_blog=git_repository_blog, file=file,
                               paginate=paginate, page=page)
    else:
        file = get_file(git_name, git_repository_blog)
    if file:
        paginate = Pagination(3, page, len(file))
        return render_template('blog.html', git_name=git_name, git_repository_blog=git_repository_blog, file=file,
                               paginate=paginate, page=page)
    else:
        session['logged_in'] = False
        flash('No such name or repository or both')
        return redirect(url_for('homepage'))


# берет конкретный пост и отображает его при нажатии на readmore
@app.route('/<git_name>/<git_repository_blog>/<int:page>/post/<title>/')
def post(git_name, git_repository_blog, title, page=1):
    f = open('static/%s.txt' % git_name)
    temp = f.readline()
    file = sorted(json.loads(temp), key=lambda d: d['date'], reverse=True)
    return render_template('post.html', file=file, title=title, git_repository_blog=git_repository_blog, git_name=git_name, page=page)


# Апи отдает данные с гита
@app.route('/<git_name>/<git_repository_blog>/api/get', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_get_blog(git_name, git_repository_blog):
    data = get_file(git_name, git_repository_blog)
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')