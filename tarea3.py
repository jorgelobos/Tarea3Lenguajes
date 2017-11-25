import racython
import sys


def parser(string):
    """ String -> RExpr
        Parse a RExpr from the result of splitting a string representation of a racket program
        on the '(', ')', and ' ' characters. """
    return racython.parser(string)


def interp(expr, env=racython.getEnv()):
    """ Rexp Environment -> Value Environment
        Recursively evaluates the given Rexp in the given environment"""
    return racython.interp(expr, env)


def run(string):
    """ String -> String
            Executes the given single function call racket program"""
    return str(racython.run(string))


if __name__ == '__main__':
    print(run(sys.argv[1]))
