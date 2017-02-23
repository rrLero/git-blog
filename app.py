from flask import Flask, render_template, request, session, flash, redirect, url_for
import os
import urllib.request
import urllib
import requests
import json


app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    SECRET_KEY='development key',
))


# url = 'https://raw.githubusercontent.com/rrlero/git-blog-content/master'
# x = urllib.request.urlopen('https://api.github.com/repos/rrlero/git-blog-content/contents/')
# y = x.read()
# y = json.loads(y)
# for el in y:
#     print(el['name'])


# считываем с репозитория git-blog-content файл README.md и читаем в переменную file
def get_file(git_name, git_repository):
    list_git_files = []
    git_objects = urllib.request.urlopen('https://api.github.com/repos/%s/%s/contents/' % (git_name, git_repository))
    git_objects_1 = git_objects.read()
    git_objects_2 = json.loads(git_objects_1)
    for git_object in git_objects_2:
        url = git_object['download_url']
        val = {}
        resource = urllib.request.urlopen(url)
        data = resource.readlines()
        for el in data:
            if (el.decode('utf-8')).split(':'):
                x,y = (el.decode('utf-8')).split(':')
                val[x] = y.rstrip()
        list_git_files.append(val)
    return list_git_files


@app.route('/index')
@app.route('/')
def homepage():
    return render_template('base.html')


# логинемся
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return render_template('base.html')


@app.route('/blog/', methods=['POST'])
def blog():
    if request.form['git_name'] and request.form['git_repository_blog']:
        session['logged_in'] = True
        flash('You were logged in')
    else:
        session['logged_in'] = False
        return redirect(url_for('base.html'))
    git_name = request.form['git_name']
    git_repository_blog = request.form['git_repository_blog']
    file = get_file(git_name, git_repository_blog)
    return render_template('blog.html', git_name=git_name, git_repository_blog=git_repository_blog, file=file)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')