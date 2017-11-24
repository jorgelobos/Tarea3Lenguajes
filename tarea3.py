import racython
import sys


def parser(string):
    return racython.parser(string)


def interp(expr):
    return racython.interp(expr, racython.getEnv())


def run(string):
    return str(racython.run(string))


if __name__ == '__main__':
    print(run(sys.argv[1]))
