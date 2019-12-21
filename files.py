# Files.py - a little workaround for specific cases with files.
# As our full database to store books, IDs, comments and whatever Hops needs built upon text-based files,
# we should avoid some I/O errors
# Below class handles some errors automatically
# Actually it doesn't raise error while opening new file if required directory is a non-existing one
# Instead, it just creates that necessary directory

import os
import errno
from globals import dev, should_log, bot


def log(*data):
    if should_log:
        bot.send_message(dev, ', '.join([str(x) for x in data]), parse_mode='html')


class File:
    @staticmethod
    def open(*args, **kwargs):
        if args[1] in ['w', 'wb', 'a', 'ab'] and not os.path.exists(os.path.dirname(args[0])):
            try:
                os.makedirs(os.path.dirname(args[0]))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    log(str(exc))
                    raise
        return open(*args, **kwargs)
