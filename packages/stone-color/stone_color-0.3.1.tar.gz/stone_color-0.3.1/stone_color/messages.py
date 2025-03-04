from sys import stdout, stderr
import re

from . import color

colors = color.DefaultColors

_alert = colors.highred + "[!]" + colors.reset
_warn = colors.highyellow + "[@]" + colors.reset
_info = colors.cyan + "[i]" + colors.reset 
_success = colors.green + "[+]" + colors.reset
_error = colors.red + "[-]" + colors.reset 

ansi_style = {
    "bold": "\033[1m",
    "italic": "\033[3m",
    "underline": "\033[4m",
    "blink": "\033[5m",
    "rapidblink": "\033[6m",
    "strike": "\033[9m",
    "invert": "\033[7m",
    "reset": "\033[0m"
}

auto_reset = False

def alertf(*objs, end="\n", sep=" ", file=stderr, flush=False):
    printf(_alert, *objs, end=end, sep=sep, file=file, flush=flush)

def warnf(*objs, end="\n", start="", sep=" ", file=stderr, flush=False):
    printf(start + _warn, *objs, end=end, sep=sep, file=file, flush=flush)

def infof(*objs, end="\n", start="", sep=" ", file=stderr, flush=False):
    printf(start + _info, *objs, end=end, sep=sep, file=file, flush=flush)

def successf(*objs, end="\n", start="", sep=" ", file=stderr, flush=False):
    printf(start + _success, *objs, end=end, sep=sep, file=file, flush=flush)

def errorf(*objs, end="\n", start="", sep=" ", file=stderr, flush=False):
    printf(start + _error, *objs, end=end, sep=sep, file=file, flush=flush)

def printf(*objs, end="\n", sep=" ", file=stdout, flush=False):
    __text = sep.join(map(str, objs)) + end

    __text = formatf(__text)

    if auto_reset:
        __text += "\033[0m"

    file.write(__text) 

    if flush:
        file.flush()

def formatf(*objs, sep=" ") -> str:
    __text = sep.join(map(str, objs))

    def color_replace(match):
        hex = match.group(1)

        if hex in ansi_style.keys():
            return ansi_style[hex]
        else:
            return color.chex(hex)

    __text = re.sub(r"\{#([^}]+)\}", color_replace, __text)

    return __text
