import os, time, sys
import multiprocessing as mp

from git import Repo
from colorama import just_fix_windows_console
from termcolor import colored


class Scram(object):
    def __init__(self, repo: str, user: dict, path: str = ""):
        repo = repo.strip()
        self.path = os.path.join(os.getcwd(), path.strip())
        _ = {"ssh": "", "name": "nobody", "email": "nobody@mail.com"}
        _.update(user)
        user = _

        if not os.path.isfile(user["ssh"]):
            raise Exception(
                f'Missing SSH key file: {user["ssh"]}\n'
                "Please generate a new SSH key and add it to your GitHub account.\n"
                "https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent"
            )

        os.environ['GIT_SSH'] = user["ssh"]

        if os.path.isdir(path):
            self.repo = Repo(path)
            print(colored(f'Fetching updates for : ', 'green'), colored(f'{os.path.basename(path[:-1]):19} Diff : {self.repo.git.pull("origin", "master")}', 'yellow\n'))
        else:
            os.makedirs(path)
            self.repo = Repo.clone_from(repo, path, env={'GIT_SSH': user["ssh"]})
            self.repo.config_writer().set_value('user', 'name', user["name"]).release()
            self.repo.config_writer().set_value('user', 'email', user["email"]).release()
