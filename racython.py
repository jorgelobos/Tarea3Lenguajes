"""
A RExp is one of:
    - Number
    - ['if0' RExp RExp RExp]
    - Variable
    - ['quote' SExp]
    - ['fun' Variable RExp]
    - ['cond' (list RExp Rexp) ...]
    - ['define' Variable RExp]
    - ['define-struct' Variable SExp]
    - ['require' String]
    - ['local' [ListOf RExp] REXp]
    - [RExp RExp ...]
A Number is one of:
    -[+ Parameters RExp]
    -[- Parameters RExp]
A Variable is a String id
A Value is one of:
    - SExp
    - Procedure
A Procedure is one of:
    - pythOP
    - closure
A pythOP is a pythOP(handler=[ListOf Value]->Value)
A closure is a closure([ListOf Variables], RExp, Env)
An environment is a dictionary mapping from a Variable to a Value
"""

import collections
from copy import deepcopy
import operator
import racket_functions
from sexpdata import loads
from nltk.tokenize import SExprTokenizer
from sys import setrecursionlimit
import sys

setrecursionlimit(1000000000)

pythOP = collections.namedtuple("pythOP", "handler")
closure = collections.namedtuple("closure", "params body env")

topLevelEnv = {"+": operator.add,
               "-": operator.sub,
               "/": operator.truediv,
               "*": operator.mul,
               "or": racket_functions.racket_or,
               "and": racket_functions.racket_and,
               "not": racket_functions.racket_not,
               "equal?": operator.eq,
               ">": operator.gt,
               "<": operator.lt,
               ">=": operator.ge,
               "<=": operator.le,
               "list": racket_functions.racket_list,
               "cons": racket_functions.racket_cons,
               "empty?": racket_functions.racket_empty_huh,
               "empty": [],
               "first": racket_functions.racket_first,
               "second": racket_functions.racket_second,
               "third": racket_functions.racket_third,
               "rest": racket_functions.racket_rest,
               "reverse": racket_functions.racket_reverse,
               "#true": True,
               "#false": False,
               "map": racket_functions.racket_map,
               "filter": racket_functions.racket_filter,
               "foldr": racket_functions.racket_foldr,
               "foldl": racket_functions.racket_foldl,
               "ormap": racket_functions.racket_ormap,
               "andmap": racket_functions.racket_andmap,
               "odd?": lambda x: x % 2 == 1,
               "even?": lambda x: x % 2 == 0,
               "check-expect": racket_functions.racket_checkExpect,
               "display": racket_functions.racket_display,
               "begin": racket_functions.racket_begin,
               "read": racket_functions.racket_read,
               "list->string": racket_functions.racket_listToString,
               "integer->char": racket_functions.racket_integerToChar,
               "error": racket_functions.racket_error,
               "explode": racket_functions.racket_explode,
               "build-list": racket_functions.racket_buildList,
               "length": racket_functions.racket_length,
               "list-ref": racket_functions.racket_listRef,
               "add1": racket_functions.racket_add1,
               "sub1": racket_functions.racket_sub1,
               "modulo": racket_functions.racket_modulo, }


class RacythonException(Exception):
    pass
class InternalRacythonException(Exception):
    pass
class check_expect_error(Exception):
    pass

def interp(rexp, env):
    """ Rexp Environment -> Value Environment
        Recursively evaluates the given Rexp in the given environment"""
    # If it is a number, then return that
    if isinstance(rexp, (int, float)):
        return rexp, env
    # If it is a string then it is either a variable or a string
    if isinstance(rexp, str):
        try:
            # If it is variable, return the value of the variable
            return env[rexp], env
        except KeyError as e:
            if rexp.find("\""):
                print("error: identificador libre!! "+rexp)
            else:
                print("error: identificador libre!! "+rexp[1:-1])
            sys.exit()
    # If it is if0, then use Python's if to determine which part to run
    if rexp[0] == 'if0':
        if interp(rexp[1], env)[0]:
            return interp(rexp[2], env)
        else:
            return interp(rexp[3], env)
    # If it is fun, create a closure with the parameters, body, and env
    if rexp[0] == 'fun':
        clausenv = deepcopy(env)
        return closure(rexp[1], rexp[2], clausenv), clausenv
    # If it is define or set, change the env then return none
    if rexp[0] == 'define' or rexp[0] == 'set':
        env[rexp[1]] = interp(rexp[2], env)[0]
        # define returns None
        return None, env
    # If it is with, create a new environment then execute it
    if rexp[0] == 'with':
        localDefines = rexp[1]
        lEnv = deepcopy(env)
        localDefines.insert(0,'define')
        interp(localDefines, lEnv)[0]
        return interp(rexp[2], lEnv)
    # If it is seqn, update the env with expr1 then eval expr2
    if rexp[0] == 'seqn':
        interp(rexp[1], env)[0]
        return interp(rexp[2], env)
    # If it is none of those, then it is a function application (aka (Rexp Rexp ...))
    else:
        # Get the function that is being called
        # deepcopy to ensure scoping rules work properly
        functionValue = interp(rexp[0], env)[0]
        # Eval each of the arguments to the function
        argsValue = [interp(a, env)[0] for a in rexp[1:]]
        # Apply the function to the arguments
        return apply(functionValue, argsValue, env=env)


def apply(function, args, env=topLevelEnv):
    """ RExp [ListOf Rexp] Environment -> Value
        Applies the given function to the given args"""
    # If it is a closure, then it is a user defined function. Thus, eval it in a new environment containing
    # the parameters to the function.
    if type(function) is closure:
        fParams = function.params
        fBody = function.body
        # deepcopy to ensure scoping rules work properly
        fullEnv = deepcopy(function.env)
        for param, arg in zip(fParams, args):
            fullEnv[param] = arg
        return interp(fBody, fullEnv)
    # If it is a PythOp, just apply the function
    else:
        return function(*args), env


def parseAtom(strRexp):
    """ String -> Value
        Parses the string into either a int or a float if possible, otherwise returns the string"""
    try:
        return int(strRexp)
    except:
        try:
            return float(strRexp)
        except:
            if strRexp == "#true" or strRexp == "#false":
                return strRexp
            else:
                return "\"" + strRexp + "\""


def parser(strRexpr):
    """ String -> RExpr
        Parse a RExpr from the result of splitting a string representation of a racket program
        on the '(', ')', and ' ' characters. """

    def reformat(sexpr):
        """ RExpr -> RExpr
            Replaces all symbol objects with strings and all bracket objects with lists"""
        if "sexpdata.Bracket" in str(type(sexpr)):
            return reformat(sexpr.value())
        elif type(sexpr) is not list:
            if "sexpdata.Symbol" in str(type(sexpr)):
                return sexpr.value()
            elif "sexpdata.Quoted" in str(type(sexpr)):
                return parseAtom(sexpr.value().value())
            else:
                return parseAtom(sexpr)
        return [reformat(term) for term in sexpr]

    if "(" not in strRexpr or ")" not in strRexpr:
        return parseAtom(strRexpr)
    sexpr = loads(strRexpr)
    return reformat(sexpr)


def run(strRexp, env=topLevelEnv, returnEnv=False):
    """ String -> Value
        Executes the given single function call racket program"""
    strRexp = strRexp
    rexp = parser(strRexp)
    if returnEnv:
        return interp(rexp, env)
    else:
        return interp(rexp, env)[0]


def runFile(file):
    """ String -> Value
        Runs he given multi function call racket program. """
    file = '\n'.join(stripComments(file.splitlines()))
    rexpList = SExprTokenizer().tokenize(file)
    output = []
    env = topLevelEnv
    for rexp in rexpList:
        out, env = run(rexp, env=env, returnEnv=True)
        output.append(out)
        print(output[-1])
    return output


def stripComments(listOfLines):
    """ [ListOf String] -> [ListOf String]
        Strips all comments from a given list of lines"""
    stripped = []
    inStr = False
    inMLComment = False
    for line in listOfLines:
        line, inStr, = stripSemiColonComments(line, inStr)
        line, inMLComment = stripMLComments(line, inMLComment)
        stripped.append(line)
    return stripped


def stripMLComments(line, currentlyInMLComment):
    """ String -> String
        Strips multiline comments from a given line"""
    charBuffer = []
    inMLComment = currentlyInMLComment
    skipNext = False
    for index, char in enumerate(line):
        if char == "#" and line[index + 1] == "|":
            inMLComment = True
        if not inMLComment and not skipNext:
            charBuffer.append(char)
        if skipNext:
            skipNext = False
        if char == "|" and line[index + 1] == "#":
            inMLComment = False
            skipNext = True
    return ''.join(charBuffer), inMLComment


def stripSemiColonComments(line, currentlyInStr):
    """ String -> String
        Strips semicolon based comments from a given line"""
    charBuffer = []
    inStr = currentlyInStr
    for char in line:
        if char == "\"":
            inStr = not inStr
        if char != ";" or inStr:
            charBuffer.append(char)
        if char == ";" and not inStr:
            break
    return ''.join(charBuffer), inStr


def getEnv():
    return topLevelEnv


if __name__ == "__main__":
    while True:
        interp(input("> "))
