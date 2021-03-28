import subprocess
import traceback


class BubbleRunner(object):
    result: str = ""
    errors: str = ""
    stats: str = ""
    cwd: str = "code"

    def __init__(self, timeout: int = 5):
        self.bufsize = 127
        self.timeout = timeout

    def run(self, code, inp: str = ""):
        try:
            args = ["python", "-c", code]
            proc = subprocess.Popen(
                args=args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.cwd,
                bufsize=self.bufsize,
            )
            for line in inp.splitlines():
                proc.stdin.write(line)
            try:
                self.result, self.errors = proc.communicate(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                self.result, self.errors = "", "Dastur juda uzoq vaqt olganligi uchun to'xtatildi"
        except:
            print(traceback.format_exc())
            self.errors = "Kutilmagan xatolik"
        self.result = self.result or ""
        self.errors = self.errors or ""
        return self.result, self.errors, self.stats
