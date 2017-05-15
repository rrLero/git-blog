import requests
import datetime
import base64
from models.textovka import Textovka
import json


textovka = Textovka()


def encode_64(text):
    file_data = text
    file_data = file_data.encode()
    file_data = base64.encodebytes(file_data)
    file_data = file_data.decode()
    return file_data


def open_file_comments(path):
    try:
        f = open(path).readlines()
        json_data = [json.loads(line) for line in f]
        com_id = [{'post_id': el['post_id'], 'id': el['id']} for el in json_data]
        return com_id
    except:
        return False


def filtered_comments(list_coms, git_name, git_repository_blog):
    try:
        list_of_test_coms = open_file_comments('static/comments_%s_%s.json' % (git_name, git_repository_blog))
    except:
        return list_coms
    if not list_of_test_coms:
        return list_coms
    else:
        try:
            for list_of_test_com in list_of_test_coms:
                key = list_of_test_com['post_id']
                val = list_of_test_com['id']
                try:
                    list_coms[key]
                except:
                    continue
                for list_com in list_coms[key]:
                    if list_com['id'] == val:
                        list_coms[key].remove(list_com)
                        break
        except:
            return list_coms
        return list_coms


class GitAccess:
    def __init__(self, git_name, git_repository_blog, access_token=None):
        self.git_name = git_name
        self.git_repository_blog = git_repository_blog
        self.access_token = access_token
        self.put_dict_git = {
            textovka.get_text('message'): textovka.get_text('commit'),
            textovka.get_text('author'): {
                textovka.get_text('name'): self.git_name,
                textovka.get_text('email'): "%s@emailemail.com" % self.git_repository_blog
            },
        }
        if self.access_token:
            self.auth_ = 'access_token=%s' % self.access_token
        else:
            f = open('static/client_id.txt')
            client_id = f.readline()
            self.auth_ = client_id
            f.close()

    def lock_status_comment(self, id_file=None):
        data_issue = self.data_issue_json()
        data_issue = data_issue.json()
        if len(data_issue) > 0:
            for issue in data_issue:
                try:
                    if issue['title'] == id_file:
                        if issue['locked']:
                            return False
                        else:
                            return True
                except:
                    return 'error'
        else:
            return True
        return True

    def get_comments(self):
        comments = self.data_issue_json()
        comments_dict = {}
        if comments.status_code == 200 and len(comments.json()) != 0:
            for i in range(len(comments.json())):
                comment = self.get_comment(comments.json()[i]['number'])
                all_com = []
                for one_comment in comment.json():
                    com = {'user': one_comment['user']['login'], 'created_at': one_comment['created_at'],
                           'body': one_comment['body'], 'avatar_url': one_comment['user']['avatar_url'],
                           'id': one_comment['id']}
                    all_com.append(com)
                comments_dict[comments.json()[i]['title']] = all_com
        return filtered_comments(comments_dict, self.git_name, self.git_repository_blog)

    def del_comment(self, id_file):
        del_comment_ = requests.delete(
            'https://api.github.com/repos/%s/%s/issues/comments/%s?%s' % (
                self.git_name, self.git_repository_blog, id_file, self.auth_))
        return del_comment_

    def data_issue_json(self):
        headers = {'Accept': 'application/vnd.github.squirrel-girl-preview'}
        return requests.get('https://api.github.com/repos/%s/%s/issues?%s'
                                % (self.git_name, self.git_repository_blog, self.auth_), headers=headers)

    def lock_issue(self, issue_id):
        return requests.put('https://api.github.com/repos/%s/%s/issues/%s/lock?%s'
                                % (self.git_name, self.git_repository_blog, issue_id, self.auth_))

    def unlock_issue(self, issue_id):
        return requests.delete('https://api.github.com/repos/%s/%s/issues/%s/lock?%s'
                                % (self.git_name, self.git_repository_blog, issue_id, self.auth_))

    def add_new_issue(self, id_file):
        text_issue = {'body': 'comments for post %s' % id_file, 'title': id_file}
        return requests.post('https://api.github.com/repos/%s/%s/issues?%s'
                                % (self.git_name, self.git_repository_blog, self.auth_), json=text_issue)

    def add_comment(self, issue_id, data_body):
        return requests.post('https://api.github.com/repos/%s/%s/issues/%s/comments?%s'
                                % (self.git_name, self.git_repository_blog, issue_id, self.auth_), json=data_body)

    def edit_comment(self, comment_id, data_body):
        return requests.patch('https://api.github.com/repos/%s/%s/issues/comments/%s?%s'
                                % (self.git_name, self.git_repository_blog, comment_id, self.auth_), json=data_body)

    def get_comment(self, number):
        return requests.get('https://api.github.com/repos/%s/%s/issues/%s/comments?%s'
                                % (self.git_name, self.git_repository_blog, number, self.auth_))

    def get_one_post(self, file_name, ref=None):
        if ref:
            return requests.get('https://api.github.com/repos/%s/%s/contents/posts/%s?%s&ref=post_branch'
                                % (self.git_name, self.git_repository_blog, file_name, self.auth_))
        return requests.get('https://api.github.com/repos/%s/%s/contents/posts/%s?%s'
                                % (self.git_name, self.git_repository_blog, file_name, self.auth_))

    def get_all_posts(self, ref=False):
        if ref:
            return requests.get('https://api.github.com/repos/%s/%s/contents/posts?%s&ref=post_branch'
                                % (self.git_name, self.git_repository_blog, self.auth_))
        return requests.get('https://api.github.com/repos/%s/%s/contents/posts?%s'
                                % (self.git_name, self.git_repository_blog, self.auth_))

    def del_one_post(self, sha, path, ref=False):
        if ref:
            self.put_dict_git['branch'] = 'post_branch'
        self.put_dict_git['sha'] = sha
        return requests.delete('https://api.github.com/repos/%s/%s/contents/%s?%s'
                                % (self.git_name, self.git_repository_blog, path, self.auth_), json=self.put_dict_git)

    def edit_post(self, changes, sha, id_file, ref=False):
        if ref:
            self.put_dict_git['branch'] = 'post_branch'
        file_data = encode_64(changes['text_full_md'])
        self.put_dict_git['sha'] = sha
        self.put_dict_git['content'] = file_data
        return requests.put('https://api.github.com/repos/%s/%s/contents/posts/%s?%s'
                                % (self.git_name, self.git_repository_blog, id_file, self.auth_), json=self.put_dict_git)

    def new_post(self, changes, ref=True, id_file=None):
        if ref:
            my_time = datetime.datetime.now()
            name_new_file = my_time.strftime('%Y-%m-%d-%I-%M-%p-')
            file_name = name_new_file + changes['filename']
            file_data = encode_64(changes['text_full_md'])
            self.put_dict_git['content'] = file_data
            self.put_dict_git['branch'] = 'post_branch'
        else:
            if id_file:
                file_name = id_file
                self.put_dict_git['content'] = changes
            else:
                my_time = datetime.datetime.now()
                name_new_file = my_time.strftime('%Y-%m-%d-%I-%M-%p-')
                file_name = name_new_file + changes['filename']
                file_data = encode_64(changes['text_full_md'])
                self.put_dict_git['content'] = file_data
        return requests.put('https://api.github.com/repos/%s/%s/contents/posts/%s?%s'
                                %(self.git_name, self.git_repository_blog, file_name, self.auth_), json=self.put_dict_git)

    def test_user_rights(self, test_user):
        headers = {'Accept': 'application/vnd.github.korra-preview'}
        return requests.get('https://api.github.com/repos/%s/%s/collaborators/%s/permission?%s'
                                % (self.git_name, self.git_repository_blog, test_user, self.auth_), headers=headers)

    def get_access_token(self, args):
        headers = {'Accept': 'application/json'}
        f = open('static/client_id2.txt')
        client_id2 = f.readline()
        f.close()
        return requests.post('https://github.com/login/oauth/access_token?%s&code=%s'
                             '&redirect_uri=http://acid.zzz.com.ua/%s/%s/page/1'
                                % (client_id2, args, self.git_name, self.git_repository_blog), headers=headers)

    def create_repo(self, name):
        name_repo = {'name': name, 'auto_init': True}
        return requests.post('https://api.github.com/user/repos?%s' % self.auth_, json=name_repo)

    def get_list_branches(self):
        return requests.get('https://api.github.com/repos/%s/%s/git/refs?%s'
                                % (self.git_name, self.git_repository_blog, self.auth_))

    def get_one_branch(self, name):
        return requests.get('https://api.github.com/repos/%s/%s/git/refs/heads/%s?%s'
                                % (self.git_name, self.git_repository_blog, name, self.auth_))

    def create_branch(self, sha):
        params = {"ref": "refs/heads/post_branch", "sha": sha}
        return requests.post('https://api.github.com/repos/%s/%s/git/refs?%s'
                                % (self.git_name, self.git_repository_blog, self.auth_), json=params)

    def del_deep_repo(self):
        return requests.delete('https://api.github.com/repos/%s/%s?%s'
                               % (self.git_name, self.git_repository_blog, self.auth_))

    def del_branch(self):
        requests.delete('https://api.github.com/repos/%s/%s/git/refs/heads/master?%s'
                        % (self.git_name, self.git_repository_blog, self.auth_))
        return requests.delete('https://api.github.com/repos/%s/%s/git/refs/heads/post_branch?%s'
                               % (self.git_name, self.git_repository_blog, self.auth_))

    def try_on_empty(self):
        return requests.get('https://api.github.com/repos/%s/%s/contents?%s'
                                % (self.git_name, self.git_repository_blog, self.auth_))

    def get_reaction(self, id_comment):
        headers = {'Accept': 'application/vnd.github.squirrel-girl-preview'}
        return requests.get('https://api.github.com/repos/%s/%s/issues/%s/reactions?%s'
                            % (self.git_name, self.git_repository_blog, id_comment, self.auth_), headers=headers)

    def create_reaction(self, id_comment, json_data):
        headers = {'Accept': 'application/vnd.github.squirrel-girl-preview'}
        return requests.post('https://api.github.com/repos/%s/%s/issues/%s/reactions?%s'
                            % (self.git_name, self.git_repository_blog, id_comment, self.auth_), json=json_data, headers=headers)


