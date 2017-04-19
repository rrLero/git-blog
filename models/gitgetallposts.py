from models.gitaccess import GitAccess
import datetime
from models.users import Users
import base64
import json


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
    elif 'preview' in test and ':' in test:
        return 'preview', test[test.find('preview:')+len('preview:'):].strip()
    elif 'date' in test and ':' in test:
        test = test[test.find('date:') + len('date:'):].strip()
        test = test.strip('"')
        return 'date', get_date(test)
    elif 'author' in test and ':' in test:
        return 'author', test[test.find('author:')+len('author:'):].strip()
    else:
        return None, test


def get_file(path, data):
    f = open(path, 'w')
    if data:
        f.write(json.dumps(data))
    f.close()
    return 'ok'


# Функция получает имя пользователя и репозиторий. при помощи АПИ ГИТА функция переберает файлы и создает словарь из
# постов
class GitGetAllPosts(GitAccess):
    def get_posts_json(self, ref=False):
        list_git_files = []
        git_objects = self.get_all_posts(ref)
        git_objects = git_objects.json()
        f = open('static/%s_%s.txt' % (self.git_name.lower(), self.git_repository_blog.lower()), 'w')
        f.close()
        if str(type(git_objects)) == "<class 'dict'>":
            return False
        data_comments = self.get_comments()
        for git_object in git_objects:
            if git_object['type'] == 'file':
                val = {}
                resource = self.get_one_post(git_object['name'], ref).json()
                data = resource['content']
                data = base64.b64decode(data)
                data = data.decode('utf-8')
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
                val['preview'] = 'No Preview'
                val['text_full_strings'] = ''
                val['comments_for_post'] = 'No comments'
                # val['text_full_md'] = ''
                val['comments'] = 0
                val['comments_status'] = self.lock_status_comment(val['id'])
                if val['id'] in data_comments:
                    val['comments'] = len(data_comments[val['id']])
                    val['comments_for_post'] = data_comments[val['id']]
                counter = 0
                str_counter = 0
                new_key = []
                for i in range(len(data)):
                    if '---' == data[i]:
                        counter += 1
                    if counter == 2:
                        str_counter += len(data[i]) + 1
                        break
                    key, string = test_string(data[i])
                    if key and string:
                        val[key] = string
                        new_key.append(key)
                    if not key and string and len(new_key) > 0:
                        if 'layout' not in string and type(val[new_key[-1]]) != list:
                            val[new_key[-1]] = val[new_key[-1]] + '\n' + string
                    str_counter += len(data[i]) + 1
                val['text_full_strings'] = full_string[str_counter:]
                list_git_files.append(val)
        return list_git_files

    def get_file(self, ref=False):
        list_git_files = self.get_posts_json(ref)
        if not list_git_files:
            list_git_files = False
            if ref:
                get_file('static/%s_%s_branch.txt' % (self.git_name.lower(), self.git_repository_blog.lower()),
                         list_git_files)
            elif not ref:
                get_file('static/%s_%s.txt' % (self.git_name.lower(), self.git_repository_blog.lower()),
                         list_git_files)
            return False
        if ref:
            get_file('static/%s_%s_branch.txt' % (self.git_name.lower(), self.git_repository_blog.lower()),
                     list_git_files)
        elif not ref:
            get_file('static/%s_%s.txt' % (self.git_name.lower(), self.git_repository_blog.lower()),
                     list_git_files)
        session_git = Users.open_base(self)
        users = session_git.query(Users)
        new_user = True
        for user in users:
            if user.user_name == self.git_name.lower() and user.user_repo_name == self.git_repository_blog.lower():
                session_git.close()
                new_user = False
        if new_user:
            new_user = Users(user_name=self.git_name.lower(), user_repo_name=self.git_repository_blog.lower())
            session_git.add(new_user)
            session_git.commit()
            session_git.close()
        return sorted(list_git_files, key=lambda d: d['date'], reverse=True)