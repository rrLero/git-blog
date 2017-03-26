import requests


class GitAccess:
    def __init__(self, git_name, git_repository_blog, access_token=None):
        self.git_name = git_name
        self.git_repository_blog = git_repository_blog
        self.access_token = access_token
        if self.access_token:
            self.auth_ = 'access_token=%s' % self.access_token
        else:
            self.auth_ = 'client_id=fcdfab5425d0d398e2e0&client_secret=355b83ee2e195275e33a4d2e113a085f6eaea0a2'
        self.data_issues = requests.get('https://api.github.com/repos/%s/%s/issues?%s' % (
            self.git_name, self.git_repository_blog, self.auth_))

    def lock_status_comment(self, id_file=None):
        if len(self.data_issues.json()) > 0:
            for issue in self.data_issues.json():
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
        comments = self.data_issues
        comments_dict = {}
        if comments.status_code == 200 and len(comments.json()) != 0:
            for i in range(len(comments.json())):
                comment = requests.get(
                    'https://api.github.com/repos/%s/%s/issues/%s/comments?%s' % (
                        self.git_name, self.git_repository_blog, comments.json()[i]['number'], self.auth_))
                all_com = []
                for one_comment in comment.json():
                    com = {'user': one_comment['user']['login'], 'created_at': one_comment['created_at'],
                           'body': one_comment['body'], 'avatar_url': one_comment['user']['avatar_url'],
                           'id': one_comment['id']}
                    all_com.append(com)
                comments_dict[comments.json()[i]['title']] = all_com
        return comments_dict

    def del_comment(self, id_file):
        del_comment = requests.delete(
            'https://api.github.com/repos/%s/%s/issues/comments/%s?access_token=%s' % (
                self.git_name, self.git_repository_blog, id_file, self.auth_))
        return '', del_comment.status_code

    def data_issue_json(self):
        return self.data_issues.json()
