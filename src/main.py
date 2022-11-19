import os, time, sys
import multiprocessing as mp
import configparser

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

        os.environ["GIT_SSH"] = user["ssh"]

        if os.path.isdir(path):
            self.repo = Repo(path)
            print(
                colored(f"Fetching updates for : ", "green"),
                colored(
                    f'{os.path.basename(path[:-1]):19} Diff : {self.repo.git.pull("origin", "master")}',
                    "yellow\n",
                ),
            )
        else:
            os.makedirs(path)
            self.repo = Repo.clone_from(repo, path, env={"GIT_SSH": user["ssh"]})
            self.repo.config_writer().set_value("user", "name", user["name"]).release()
            self.repo.config_writer().set_value(
                "user", "email", user["email"]
            ).release()

    def commit(self, branch: str = "main", message: str = "Auto commit"):
        has_changes = False
        for file in self.repo.untracked_files:
            print(
                colored(f"Adding untracked file : ", "blue"),
                colored(f"{file} {os.path.basename(self.path[:-1]):19}", "yellow\n"),
            )
            self.repo.git.add(file)
            has_changes = True

        if self.repo.is_dirty():
            for file in self.repo.git.diff(None, name_only=True).splitLines():
                if file == "":
                    continue

                print(
                    colored(f"Adding modified file : ", "blue"),
                    colored(f"{file} {os.path.basename(self.path[:-1])}", "yellow\n"),
                )
                self.repo.git.add(file)
                has_changes = True

        return has_changes

    def remote(output_queue, input_queue, remote_repo, path_repo):
        user = configparser.ConfigParser()
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))
        )
        user.read(os.path.join(__location__, "user.ini"))
        repository = Scram(
            repo=remote_repo, user=dict(user.items("user_id")), path=path_repo
        )

        if repository.commit() is True:
            output_queue.put(colored(f'\nCommiting changes to', 'red'), colored(f'{os.path.basename(path_repo[:-1])} = ', 'green'))
            result = input_queue.get()
            repository.repo.git.commit('-m', result)
            repository.repo.git.push('origin', 'main')
        output_queue.put(colored('Done', 'green'))

    def main(args):
        process = configparser.ConfigParser()
