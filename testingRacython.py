import unittest

from racython import run, stripSemiColonComments, stripComments, stripMLComments, interp, topLevelEnv, \
    closure, apply
import racython


class TestInterpreterInternals(unittest.TestCase):
    def test_parser(self):
        self.assertEqual(racython.parser("(\"Hello World!\")"), ["\"Hello World!\""])
        self.assertEqual(racython.parser("(5)"), [5])
        self.assertEqual(racython.parser("(5.0)"), [5.0])
        self.assertEqual(racython.parser("(\"5\" \"Hello World!\")"), [5, "\"Hello World!\""])
        self.assertEqual(racython.parser("((fun (x) (func (+ 1 1) 5)) 2)"),
                         [['fun', ['x'], ['func', ['+', 1, 1], 5]], 2])

    def test_parseAtom(self):
        self.assertEqual(racython.parseAtom("5"), 5)
        self.assertEqual(racython.parseAtom("5.0"), 5.0)
        self.assertEqual(racython.parseAtom("Hello World!"), "\"Hello World!\"")

    def test_stripComments(self):
        self.assertEqual(stripSemiColonComments("before;comment", False), ("before", False))
        self.assertEqual(stripSemiColonComments("\"inString;stillInString\";comment", False),
                         ("\"inString;stillInString\"", False))
        self.assertEqual(stripSemiColonComments("test;;test", False), ("test", False))
        self.assertEqual(
            stripComments(["test;test", "\"test;test\";comment", "\"testMultiLine;part", "part2;part3\";comment"]),
            ["test", "\"test;test\"", "\"testMultiLine;part", "part2;part3\""])
        self.assertEqual(stripMLComments("(define #|test|# a 5)", False), ("(define  a 5)", False))
        self.assertEqual(stripMLComments("(define test|# a 5)", True), (" a 5)", False))
        self.assertEqual(stripComments(["(define a 5) #| firstComment", "restComment |# (define b 4)"]),
                         (["(define a 5) ", " (define b 4)"]))

    def test_interp(self):
        self.assertEqual(interp(5, topLevelEnv)[0], 5)  # integers
        self.assertEqual(interp(5.0, topLevelEnv)[0], 5.0)  # floats
        self.assertEqual(interp("\"Hello World\"", topLevelEnv)[0], "Hello World")  # strings
        self.assertEqual(interp("#true", topLevelEnv)[0], True)  # Booleans work via looking them up in the env
        self.assertEqual(interp(["quote", 1, 2, 3], topLevelEnv)[0], [1, 2, 3])  # quote works with numbers
        self.assertEqual(interp(["quote", "a", "b", "c"], topLevelEnv)[0], ["a", "b", "c"])  # and with strings/symbols
        self.assertEqual(interp(["if0", ["equal?", 1, 1],
                                 ["+", 1, 1],
                                 ["-", 1, 1]],
                                topLevelEnv)[0],
                         2)
        self.assertEqual(interp(["if0", ["equal?", 1, 2],
                                 ["+", 1, 1],
                                 ["-", 1, 1]],
                                topLevelEnv)[0],
                         0)
        self.assertEqual(isinstance(interp(["fun", ["x"], ["+", 1, "x"]], topLevelEnv)[0], closure), True)

    def test_apply(self):
        def add(x, y):
            return x + y

        self.assertEqual(apply(add, [1, 2])[0], 3)
        addclosure = interp(["fun", ["x", "y"], ["+", "x", "y"]], topLevelEnv)[0]
        self.assertEqual(apply(addclosure, [1, 2])[0], 3)


class TestRacketInterpreter(unittest.TestCase):
    def test_basics(self):
        self.assertEqual(run("(+ 1 1)"), 2)
        self.assertEqual(run("(- 3 2)"), 1)
        self.assertEqual(run("(add1 5)"), 6)
        self.assertEqual(run("(sub1 5)"), 4)
        self.assertEqual(run("(modulo 11 2)"), 1)
        self.assertEqual(run("(equal? 1 2)"), False)
        self.assertEqual(run("(equal? 1 1)"), True)
        self.assertEqual(run("(equal? (list 1 2) (list 1 2 3))"), False)
        self.assertEqual(run("(equal? (list 1 2) (list 1 2))"), True)
        self.assertEqual(run("(>= 3 2)"), True)
        self.assertEqual(run("(>= 3 3)"), True)
        self.assertEqual(run("(>= 3 4)"), False)
        self.assertEqual(run("(> 3 2)"), True)
        self.assertEqual(run("(< 3 3)"), False)
        self.assertEqual(run("(<= 3 3)"), True)

    def test_fun(self):
        self.assertEqual(run("""((fun (abs) (list (abs (- 5 7))
                                                         (abs (- 7 5))))
                                     (fun (x) (if0 ( < x 0) (- 0 x) x)))"""), [2, 2])

    def test_if0(self):
        self.assertEqual(run("(if0 (> 5 0) 5 6)"), 5)
        self.assertEqual(run("(if0 (< 5 0) 5 6)"), 6)

    def test_logic(self):
        self.assertEqual(run("#true"), True)
        self.assertEqual(run("#false"), False)
        self.assertEqual(run("(not #true)"), False)
        self.assertEqual(run("(not #false)"), True)
        self.assertEqual(run("(and #true #true #true)"), True)
        self.assertEqual(run("(or #true #true #true)"), True)
        self.assertEqual(run("(and #true #false #true)"), False)
        self.assertEqual(run("(or #true #false #true)"), True)
        self.assertEqual(run("(or #false #false #false)"), False)

    def test_list_functions(self):
        self.assertEqual(run("(list 1 2 3 4)"), [1, 2, 3, 4])
        self.assertEqual(run("(cons 0 (list 1 2 3 4))"), [0, 1, 2, 3, 4])
        self.assertEqual(run("(empty? empty)"), True)
        self.assertEqual(run("(empty? (cons 0 empty))"), False)
        self.assertEqual(run("(rest (list 1 2 3 4))"), [2, 3, 4])
        self.assertEqual(run("(first (list 1 2 3 4))"), 1)
        self.assertEqual(run("(second (list 1 2 3 4))"), 2)
        self.assertEqual(run("(third (list 1 2 3 4))"), 3)
        self.assertEqual(run("(reverse (list 1 2 3))"), [3, 2, 1])
        self.assertEqual(run("(explode \"abcde\")"), ["a", "b", "c", "d", "e"])
        self.assertEqual(run("(list-ref (list \"a\" \"b\" \"c\") 1)"), "b")
        self.assertEqual(run("(build-list 5 (fun (x) x))"), [0, 1, 2, 3, 4])
        self.assertEqual(run("(build-list 5 (fun (x) (* 2 x)))"), [0, 2, 4, 6, 8])

    def test_begin(self):
        self.assertEqual(run("(begin (+ 1 1))"), 2)
        self.assertEqual(run("(begin (* 2 2) (+ 1 1))"), 2)
        self.assertEqual(run("(begin (* 3 3) (/ 2 2) (+ 1 1))"), 2)

    def test_quote(self):
        self.assertEqual(run("(quote 1 2 3)"), [1, 2, 3])
        self.assertEqual(run("(quote 1 2 3 a)"), [1, 2, 3, "a"])
        self.assertEqual(run("(quote (quote 1 2 3))"), [["quote", 1, 2, 3]])


if __name__ == '__main__':
    unittest.main()
