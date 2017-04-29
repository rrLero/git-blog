# FrontEnd
### The short list of platform's capabilities:
* creation / deleting blogs
* creation / editing/ deleting posts (accessible two branches)
* turn on / turn off comments
* add / edit / delete comments

#### Collective blog use
#### To use blog more than one person you need:
* in own repo enter settings `Settings`
* choose ` Collaborators`
* in the field enter name of user, whom you granted access
* press the button`Add collaborator`

### Possible problems
#### Problems updating blog
Propably you are working with blog out of platform.
To work blog correctly all changes should be done by platform interface.
If you have reasons not to use interface of platform, then you need:
* set up webhook:
  * in your repo enter settings
  * choose menu add Webhooks
  * in field Payload url insert http://gitblog.pythonanywhere.com/git_username/git_repo_name/api/web_hook, where git_username  is the name of your account GitHub, and git_repo_name is repo name
  * in content type choose application/json
  * Just the push event and Active should be marked
  * final stage - Add Webhook
* or update blog by button Update

#### impossible to add comments
In forked repo there is no opportunity to add comments. 
You should use your own repo

# BACKEND
In this moment backend situated on http://gitblog.pythonanywhere.com - thisis the begining of all requests to api.

git_name - name of GitHub User

git_repository_blog - name of the repo of this user

id_file - unique name of file/post which creates by our programm 

id_comment - unique id comment, getting from GitHub Api by our programm

access_token - special key token by authorazation  on our platform

# Basic Requests
**1. Request to recieve posts**

> *`/<gitname>/<gitrepositoryblog>/api/get`, method=GET- will output json with dict of posts, better send request with token in arguments but will outpost anyway**.*

**2. Request to receive one post**

> *`/<git_name>/<git_repository_blog>/api/get/id/<id>` method=GET, where id - individual number of post, getting from request №1. will output json with data from this post, or {'message': 'no such post'} if id not the same*
> 
> *also posiible to get data of post by the name of GitHub file with ext or title from first request, request in such caseа `/<git_name>/<git_repository_blog>/api/get/<title>` метод=GET*

**3. Request to update blog (reads all data from repo)**

> *`/<git_name>/<git_repository_blog>/api/update или web_hook` method=GET. Before update all data is getting from file saved localy, which was read first time when blog was opened. I recomend to update all time when any changes were made in blog, and make settings on webhook on github*

**4. Request to get all users who use platform**

> *`/api/blog_list`method=GET. will output json with all users in Name and Rep*
 
**5. Request on authorizathion on GitHub**

> *`/<git_name>/<git_repository_blog>/api/oauth?code=code`method=GET. in request required code in arguments received from GitHub in authorization. Will output access_token GitHub user
 
**6.Request to try users rights to repo (is this user collaborator of repo) **
> *`/api/repo_master/<git_name>/<git_repository_blog>/<test_user>?access_token=access_token`method=GET. in request access token required in arguments without token will not work. Will output {'access': True} or {'access': False}
 
**7. Request to get dict of all comments to all posts in one specific user's blog**
> *`/<git_name>/<git_repository_blog>/api/get_comments`method=GET. better send authorized request in arguments, but works anyway, will output json with comments dict 
 
**8. Request to get comments to specific post of user's blog**
> *`/<git_name>/<git_repository_blog>/api/get_comments/<id_file>`method=GET. better send authorized request in arguments, but works anyway, will output json with list of comments to this post, id_file - the same that the name of the file in folder /posts.
 
**9. Request to delete one comment**
> *`/<git_name>/<git_repository_blog>/api/get_comments/<id_comment>?access_token=access_token`method=DELETE in request access token required in arguments without token will not work. id_comment - gettinf from 8 request - delete comment by it id

**10. Request to add one comment**
> *`/<git_name>/<git_repository_blog>/api/get_comments?access_token=access_token`method=POST only authorized.  need  outcome with  json  {'body': 'text_of_new_comment'}, will output json with new comment (hit data, it id, date, author)
 
**11. Request to edit specific comment**
> *`/<git_name>/<git_repository_blog>/api/get_comments/<id_comment>?access_token=access_token`method=PUT only authorized request. need to outcome json with {'body': 'new_text_of_old_comment'}, will output status of request (success or not)
 
**12. Request to open/close comments to specific post**
> *`/<git_name>/<git_repository_blog>/api/lock_comments/<id_file>?access_token=access_token`метод=GET/DELETE запрос только аворизированный. Открывает/закрывает возможность оставлять комментарии. id_file получаем изи запроса 2 - оно же имя файла в папке /posts.
 
 **13. Request to get comment's status (opened/closed)**
> *`/<git_name>/<git_repository_blog>/api/lock_status/<id_comment>` method=GET not authorized request. Will output {'status': False} or {'status':  True}
 
 **14. Request to delete user's blog**
> *`/<git_name>/<git_repository_blog>/api/del_repo?access_token=access_token` method=DELETE request only authorized  Deleting all files from folder posts specific repo
 
 **15. Request to get list of posts sorted by tags**
> *`/<git_name>/<git_repository_blog>/api/get/tags/<tag>` method=GET better send authorized request in arguments, but works anyway. Will pull out the same list like in first paragraph, but sorted by tag.
 
 **16. Request to get list of posts in branch post_branch**
> *`/<git_name>/<git_repository_blog>/api/get_branch_posts` method=GET  better send authorized request in arguments, but works anyway. Will will output list of posts from branch post_branch
 
 **17. Request to get one post by id_file inside branch post_branch**
> *`/<git_name>/<git_repository_blog>/api/branch/remove/<id_file>` method=GET better send authorized request in arguments, but works anyway.  Will output one post by it id
 
 **18. Request to delete one post by id_file in branch post_branch**
> *`/<git_name>/<git_repository_blog>/api/branch/remove/<id_file>` method=DELETE better send authorized request in arguments, but works anyway.  Will output status of request operation by deletin file in branch 
 
 **19. Request to edit one post by id_file in branch post_branch**
> *`/<git_name>/<git_repository_blog>/api/branch/remove/<id_file>` method=POST only authorized request also need  json with data consisting 'text_full_md' where changed post's data in. Will output status of operation by editing of file in branch 
 
 **20. Request to move one post by id_file in branch post_branch to branch master**
> *`/<git_name>/<git_repository_blog>/api/branch/remove/<id_file>` method=PUT only authorized request.  Will output status of request operation by moving file from branch to master.
