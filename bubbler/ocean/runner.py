import pwd
import subprocess
import traceback
import os
import logging


class BubbleRunner(object):
    result: str = ""
    errors: str = ""
    stats: str = ""
    cwd: str = "/jail"

    def __init__(self, timeout: int = 7, bufsize: int = 1):
        self.bufsize = bufsize
        self.timeout = timeout

    @staticmethod
    def demote(user_uid, user_gid):

        def set_ids():
            os.setgid(user_gid)
            os.setuid(user_uid)

        return set_ids

    def run(self, code, inp: str = ""):
        try:
            args = ["python", "-c", code]
            username = "runner"
            pw_record = pwd.getpwnam(username)
            user_uid = pw_record.pw_uid
            user_gid = pw_record.pw_gid
            env = os.environ.copy()
            env.update({'HOME': self.cwd, 'LOGNAME': username, 'PWD': self.cwd, 'USER': username})
            proc = subprocess.Popen(
                args=args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.cwd,
                bufsize=self.bufsize,
                preexec_fn=BubbleRunner.demote(user_uid, user_gid),
                env=env
            )
            proc.stdin.write(inp)
            try:
                self.result, self.errors = proc.communicate(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                self.result, self.errors = "", "Dastur juda uzoq vaqt olganligi uchun to'xtatildi"
        except PermissionError:
            self.result, self.errors = "", "Ruxsat etilmagan buyruq ishlatildi"
        except:
            logging.error(traceback.format_exc())
            self.errors = "Kutilmagan xatolik"
        self.result = self.result or ""
        self.errors = self.errors or ""
        return self.result, self.errors, self.stats
