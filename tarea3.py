import racython
import sys


def parser(string):
    """ Rexp Environment -> Value Environment
            Recursively evaluates the given Rexp in the given environment"""
    return racython.parser(string)


def interp(expr, env=racython.getEnv()):
    return racython.interp(expr, env)


def run(string):
    return str(racython.run(string))


if __name__ == '__main__':
    print(run(sys.argv[1]))
