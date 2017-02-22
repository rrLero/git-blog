from flask import Flask, render_template, request, session, flash, redirect, url_for
import os
import urllib.request
import urllib


app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    SECRET_KEY='development key',
))
working_name = {}


# считываем с репозитория git-blog-content файл README.md и читаем в переменную file
def get_file(git_name, git_repository):
    url = 'https://raw.githubusercontent.com/%s/%s/master/README.md' % (git_name, git_repository)
    print(url)
    response = urllib.request.urlopen(url)
    data = response.read()
    file = data.decode('utf-8')
    return file


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
    working_name['git_name'] = git_name
    working_name['git_repository_blog'] = git_repository_blog
    file = get_file(git_name, git_repository_blog)
    return render_template('blog.html', git_name=git_name, git_repository_blog=git_repository_blog, file=file)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')