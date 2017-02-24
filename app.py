from flask import Flask, render_template, request, session, flash, redirect, url_for
import os
import urllib.request
import urllib
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
    try:
        git_objects = urllib.request.urlopen('https://api.github.com/repos/%s/%s/contents/' % (git_name, git_repository))
    except urllib.error.HTTPError:
        session['logged_in'] = False
        return False
    git_objects = git_objects.read()
    git_objects = json.loads(git_objects)
    for git_object in git_objects:
        url = git_object['download_url']
        val = {}
        resource = urllib.request.urlopen(url)
        data = resource.readlines()
        for el in data:
            if ':' in el.decode('utf-8'):
                x,y = (el.decode('utf-8')).split(':')
                val[x] = y.rstrip()
            else:
                val['date'] = 'ERROR'
                val['title'] = "can't build blog"
                val['text'] = 'your file should be with title:...., date:....., text:.....'
        list_git_files.append(val)
    return sorted(list_git_files, key=lambda d: d['date'], reverse=True)


@app.route('/index')
@app.route('/')
def homepage():
    return render_template('base.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('homepage'))


@app.route('/login', methods=['POST'])
def login():
    if request.form['git_name'] and request.form['git_repository_blog']:
        session['logged_in'] = True
        git_name = request.form['git_name']
        git_repository_blog = request.form['git_repository_blog']
        return redirect(url_for('blog', git_name=git_name, git_repository_blog=git_repository_blog))
    else:
        session['logged_in'] = False
        return redirect(url_for('homepage'))


@app.route('/<git_name>/<git_repository_blog>/')
def blog(git_name, git_repository_blog):
    session['logged_in'] = True
    if get_file(git_name, git_repository_blog):
        file = get_file(git_name, git_repository_blog)
        return render_template('blog.html', git_name=git_name, git_repository_blog=git_repository_blog, file=file)
    else:
        session['logged_in'] = False
        flash('No such name or repository or both')
        return redirect(url_for('homepage'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')