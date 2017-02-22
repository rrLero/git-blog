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
url = 'https://raw.githubusercontent.com/rrLero/git-blog-content/master/README.md'
response = urllib.request.urlopen(url)
data = response.read()


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
    if request.form['gitname'] and request.form['gitrepositoryblog']:
        session['logged_in'] = True
        flash('You were logged in')
    else:
        session['logged_in'] = False
        return redirect(url_for('base.html'))
    gitname = request.form['gitname']
    gitrepositoryblog = request.form['gitrepositoryblog']
    working_name['gitname'] = gitname
    working_name['gitrepositoryblog'] = gitrepositoryblog
    return render_template('blog.html', gitname=gitname, gitrepositoryblog=gitrepositoryblog, file=file)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')