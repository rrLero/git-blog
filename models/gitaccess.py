import requests
import datetime
import base64


class GitAccess:
    def __init__(self, git_name, git_repository_blog, access_token=None):
        self.git_name = git_name
        self.git_repository_blog = git_repository_blog
        self.access_token = access_token
        self.put_dict_git = {
            "message": "my commit message",
            "author": {
                "name": self.git_name,
                "email": "%s@emailemail.com" % self.git_repository_blog
            },
        }
        if self.access_token:
            self.auth_ = 'access_token=%s' % self.access_token
        else:
            self.auth_ = 'client_id=fcdfab5425d0d398e2e0&client_secret=355b83ee2e195275e33a4d2e113a085f6eaea0a2'

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
        return comments_dict

    def del_comment(self, id_file):
        del_comment_ = requests.delete(
            'https://api.github.com/repos/%s/%s/issues/comments/%s?%s' % (
                self.git_name, self.git_repository_blog, id_file, self.auth_))
        return del_comment_

    def data_issue_json(self):
        return requests.get('https://api.github.com/repos/%s/%s/issues?%s'
                                % (self.git_name, self.git_repository_blog, self.auth_))

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

    def edit_post(self, changes, sha, id_file):
        file_data = changes['text_full_md']
        file_data = file_data.encode()
        file_data = base64.encodebytes(file_data)
        file_data = file_data.decode()
        self.put_dict_git['sha'] = sha
        self.put_dict_git['content'] = file_data
        return requests.put('https://api.github.com/repos/%s/%s/contents/posts/%s?%s'
                                % (self.git_name, self.git_repository_blog, id_file, self.auth_), json=self.put_dict_git)

    def new_post(self, changes, ref=True, id_file=None):
        if ref:
            my_time = datetime.datetime.now()
            name_new_file = my_time.strftime('%Y-%m-%d-%I-%M-%p-')
            file_data = changes['text_full_md']
            file_name = name_new_file + changes['filename']
            file_data = file_data.encode()
            file_data = base64.encodebytes(file_data)
            file_data = file_data.decode()
            self.put_dict_git['content'] = file_data
            self.put_dict_git['branch'] = 'post_branch'
        else:
            if id_file:
                file_name = id_file
                self.put_dict_git['content'] = changes
        return requests.put('https://api.github.com/repos/%s/%s/contents/posts/%s?%s'
                                %(self.git_name, self.git_repository_blog, file_name, self.auth_), json=self.put_dict_git)

    def test_user_rights(self, test_user):
        headers = {'Accept': 'application/vnd.github.korra-preview'}
        return requests.get('https://api.github.com/repos/%s/%s/collaborators/%s/permission?%s'
                                % (self.git_name, self.git_repository_blog, test_user, self.auth_), headers=headers)

    def get_access_token(self, args):
        headers = {'Accept': 'application/json'}
        return requests.post('https://github.com/login/oauth/access_token?client_id=48f5b894f42ae1f869d2'
                                     '&client_secret=e289a8e72533f127ba873f0dec05908e6846866b&code=%s&'
                                     '&redirect_uri=http://acid.zzz.com.ua/%s/%s/page/1'
                                % (args, self.git_name, self.git_repository_blog), headers=headers)

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
        # requests.delete('https://api.github.com/repos/%s/%s/git/refs/heads/master?%s'
        #                 % (self.git_name, self.git_repository_blog, self.auth_))
        return requests.delete('https://api.github.com/repos/%s/%s/git/refs/heads/post_branch?%s'
                               % (self.git_name, self.git_repository_blog, self.auth_))
