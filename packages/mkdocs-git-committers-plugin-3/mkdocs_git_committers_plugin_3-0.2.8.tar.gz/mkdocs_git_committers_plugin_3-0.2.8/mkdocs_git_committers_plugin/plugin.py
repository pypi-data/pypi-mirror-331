import logging
import os
import subprocess
import sys

from pprint import pprint
from timeit import default_timer as timer
from datetime import datetime, timedelta

from mkdocs import utils as mkdocs_utils
from mkdocs.config import config_options, Config
from mkdocs.plugins import BasePlugin

from github import Github
from github import Auth

LOG = logging.getLogger("mkdocs.plugins." + __name__)

class GitCommittersPlugin(BasePlugin):

    config_scheme = (
        ('enterprise_hostname', config_options.Type(str, default='')),
        ('repository', config_options.Type(str, default='')),
        ('branch', config_options.Type(str, default='master')),
        ('docs_path', config_options.Type(str, default='docs/')),
        ('token', config_options.Type(str, default='')),
        ('ignored_files', config_options.Type(list, default=[])),
    )

    def __init__(self):
        self.enabled = False
        self.total_time = 0
        self.branch = 'master'

    def on_config(self, config):
        if 'MKDOCS_GIT_COMMITTERS_APIKEY' in os.environ:
            self.config['token'] = os.environ['MKDOCS_GIT_COMMITTERS_APIKEY']
        if self.config['token'] and self.config['token'] != '':
            LOG.info("git-committers plugin ENABLED")
            self.enabled = True
            auth = Auth.Token(self.config['token'])
            if self.config['enterprise_hostname'] and self.config['enterprise_hostname'] != '':
                self.github = Github( base_url="https://" + self.config['enterprise_hostname'] + "/api/v3", auth=auth )
            else:
                self.github = Github( auth=auth )
            self.repo = self.github.get_repo( self.config['repository'] )
            self.branch = self.config['branch']
        else:
            LOG.warning("git-committers plugin DISABLED: no git token provided")
        return config

    def get_last_commit(self, path):
        since = datetime.now() - timedelta(days=1)
        commits = self.repo.get_commits(path=path, sha=self.branch)
        if commits.totalCount > 0:
            return commits[0]
        else:
            return None

    def get_committers(self, path):
        if any(path.endswith(ignored_file) for ignored_file in self.config['ignored_files']):

            LOG.info(f"Skipping ignored path: {path}")
            return []
        unique_committers = []


        result = subprocess.check_output(['git', 'log', '--follow', '--format=%aN <%aE>', '--', path], text=True)
        names = set(line.split('<')[0].rstrip() for line in result.strip().splitlines())
        for name in names:
            committer_info = self.get_user_info_by_name(name)
            if committer_info and all(committer['avatar'] != committer_info['avatar'] for committer in unique_committers):
                unique_committers.append(committer_info)
        result = [committer for committer in unique_committers if committer and committer["name"] is not None]
        if result is not None:
            names = ', '.join([e['name'] for e in result])
        else:
            names = ""

        LOG.info(f"Looked up contributors for path: {path}   -   {names}")
        return result

    def get_user_info_by_name(self, name):
        users = self.github.search_users(name+" in:users")
        for user in users:
            return self.construct_committer_info(user)
        return None

    def construct_committer_info(self, user):
        return {
            "name": user.name,
            "login": user.name,
            "url": user.html_url,
            "avatar": user.avatar_url,
            "last_commit": self.get_last_commit(user.login),
            "repos": user.html_url
        }

    def get_last_commit(self, login):
        commits = self.repo.get_commits(author=login)
        last_commit = None
        if commits.totalCount > 0:
            last_commit = commits[0].html_url
        return last_commit

    def get_github_user(self, username):
        user = self.github.get_user( username )
        contrib = {
            "name": user.name,
            "login": user.login,
            "url": f"https://{self.config['enterprise_hostname'] or 'github.com'}/{user.login}",
            "avatar": user.avatar_url,
            "last_commit": user.avatar_url,
            "repos": f"https://{self.config['enterprise_hostname'] or 'github.com'}/{user.login}"
            }
        return contrib

    def on_page_context(self, context, page, config, nav):
        context['committers'] = []
        if not self.enabled:
            return context
        start = timer()
        git_path = self.config['docs_path'] + page.file.src_path
        committers = self.get_committers(git_path)
        if committers is not None:
            names = ', '.join([e['name'] for e in committers])
        else:
            names=""

        if 'contributors' in page.meta:
            users = page.meta['contributors'].split(',')
            seen = False
            for u in users:
                for item in committers:
                    if item['login'] == u:
                        seen = True
                if seen:
                    continue
                try:
                    c = self.get_github_user( u )
                    committers.append( c )
                except:
                    LOG.warning("could not find github user %s",u)

        if committers:
            context['committers'] = committers

        context['last_commit'] = self.get_last_commit(git_path)
        end = timer()
        self.total_time += (end - start)

        return context

