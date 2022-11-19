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
            print(f'Fetching updates for : {os.path.basename(path[:-1]):19} Diff : {self.repo.git.pull("origin", "main")}')
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
            print(f'Adding untracked file : {file} {os.path.basename(self.path[:-1])}\n')
            self.repo.git.add(file)
            has_changes = True

        if self.repo.is_dirty():
            for file in self.repo.git.diff(None, name_only=True).splitLines():
                if file == "":
                    continue

                print(f'Adding modified file : {file} {os.path.basename(self.path[:-1])}\n')
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

    def main():
        process = configparser.ConfigParser()
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        process.read(os.path.join(__location__, 'repos.ini'))
        queues = []
        num_processes = 0

        for i, name in enumerate(process):
            if name == 'DEFAULT':
                continue
            iq = mp.Queue()
            oq = mp.Queue()
            queues.append((oq, iq))
            mp.Process(target=Scram.remote, args=(oq, iq, process.get(name, 'repo'), process.get(name, 'path'))).start()
            num_processes += 1

        done = 0
        waiting_input = 0
        keep = []

        while done + waiting_input < num_processes:
            for iq, oq in queues:
                if not oq.empty():
                    req = oq.get()
                    if 'INPUT' in req:
                        waiting_input += 1
                        keep.append((req, iq))
                    elif 'DONE' in req:
                        done += 1
                    else:
                        print(req)

        done = 0

        # keep inputs until all processes are done
        for req, iq in keep:
            res = input(req.split(":")[1])
            iq.put(res)

        while done < waiting_input:
            for iq, oq in queues:
                if not oq.empty():
                    req = oq.get()
                    if 'DONE' in req:
                        done += 1
                    else:
                        print(req)

        print('\nCompleted all updates')

if __name__ == "__main__":
    Scram.main()

