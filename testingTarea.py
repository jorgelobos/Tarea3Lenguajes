import unittest

from racython import run, stripSemiColonComments, stripComments, stripMLComments, interp, topLevelEnv, \
    closure, apply
import racython
import tarea3


class TestInterpreterInternals(unittest.TestCase):
    def test_parser(self):
        self.assertEqual(tarea3.parser("(\"Hello World!\")"), ["\"Hello World!\""])
        self.assertEqual(tarea3.parser("(5)"), [5])
        self.assertEqual(tarea3.parser("(5.0)"), [5.0])
        self.assertEqual(tarea3.parser("(\"5\" \"Hello World!\")"), [5, "\"Hello World!\""])
        self.assertEqual(tarea3.parser("((fun (x) (func (+ 1 1) 5)) 2)"),
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
        self.assertEqual(tarea3.interp(5, topLevelEnv)[0], 5)  # integers
        self.assertEqual(tarea3.interp(5.0, topLevelEnv)[0], 5.0)  # floats
        self.assertEqual(tarea3.interp("#true", topLevelEnv)[0], True)  # Booleans work via looking them up in the env
        self.assertEqual(tarea3.interp(["if0", ["equal?", 1, 1],
                                        ["+", 1, 1],
                                        ["-", 1, 1]],
                                       topLevelEnv)[0],
                         2)
        self.assertEqual(tarea3.interp(["if0", ["equal?", 1, 2],
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
        self.assertEqual(tarea3.run("(+ 1 1)"), "2")
        self.assertEqual(tarea3.run("(- 3 2)"), "1")
        self.assertEqual(tarea3.run("(add1 5)"), "6")
        self.assertEqual(tarea3.run("(sub1 5)"), "4")
        self.assertEqual(tarea3.run("(modulo 11 2)"), "1")
        self.assertEqual(tarea3.run("(equal? 1 2)"), "False")
        self.assertEqual(tarea3.run("(equal? 1 1)"), "True")
        self.assertEqual(tarea3.run("(equal? (list 1 2) (list 1 2 3))"), "False")
        self.assertEqual(tarea3.run("(equal? (list 1 2) (list 1 2))"), "True")
        self.assertEqual(tarea3.run("(>= 3 2)"), "True")
        self.assertEqual(tarea3.run("(>= 3 3)"), "True")
        self.assertEqual(tarea3.run("(>= 3 4)"), "False")
        self.assertEqual(tarea3.run("(> 3 2)"), "True")
        self.assertEqual(tarea3.run("(< 3 3)"), "False")
        self.assertEqual(tarea3.run("(<= 3 3)"), "True")

    def test_fun(self):
        self.assertEqual(tarea3.run("(((fun (x) x) (fun (x) (+ x 5))) 3)"), "8")
        self.assertEqual(run("""((fun (abs) (list (abs (- 5 7))
                                                         (abs (- 7 5))))
                                     (fun (x) (if0 ( < x 0) (- 0 x) x)))"""), [2, 2])

    def test_if0(self):
        self.assertEqual(tarea3.run("(if0 (> 5 0) 5 6)"), "5")
        self.assertEqual(tarea3.run("(if0 (< 5 0) 5 6)"), "6")
        self.assertEqual(tarea3.run("(if0 (if0 0 2 (+ 0 0)) (+ (if0 1 450 900) 23) (+ 6 9))"), "15")

    def test_logic(self):
        self.assertEqual(tarea3.run("#true"), "True")
        self.assertEqual(tarea3.run("#false"), "False")
        self.assertEqual(tarea3.run("(not #true)"), "False")
        self.assertEqual(tarea3.run("(not #false)"), "True")
        self.assertEqual(tarea3.run("(and #true #true #true)"), "True")
        self.assertEqual(tarea3.run("(or #true #true #true)"), "True")
        self.assertEqual(tarea3.run("(and #true #false #true)"), "False")
        self.assertEqual(tarea3.run("(or #true #false #true)"), "True")
        self.assertEqual(tarea3.run("(or #false #false #false)"), "False")

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
        self.assertEqual(run("(build-list 5 (fun (x) x))"), [0, 1, 2, 3, 4])
        self.assertEqual(run("(build-list 5 (fun (x) (* 2 x)))"), [0, 2, 4, 6, 8])

    def test_begin(self):
        self.assertEqual(run("(begin (+ 1 1))"), 2)
        self.assertEqual(run("(begin (* 2 2) (+ 1 1))"), 2)
        self.assertEqual(run("(begin (* 3 3) (/ 2 2) (+ 1 1))"), 2)

    def test_with(self):
        self.assertEqual(tarea3.run("(with (f (fun (y) (+ x y))) (+ 2 3))"), "5")
        self.assertEqual(tarea3.run("(with (x 3) (with (f (fun (y) (+ x y))) (with (x 5) (f 4))))"), "7")

    def test_seqn_set(self):
        self.assertEqual(tarea3.run("(with (x 3) (+ (seqn (set x 5) x) x))"), "10")
        self.assertEqual(tarea3.run("(with (x 3) (with (f (fun (y) (- x y))) (seqn (set x 15) (f 10))))"), "-7")
        self.assertEqual(tarea3.run("(with (x 3) (seqn (set x 15) (with (f (fun (y) (- x y))) (f 10))))"), "5")

    def test_error(self):
        self.assertRaises(KeyError, tarea3.run, "(with (f (fun (y) (+ x y))) (f 3))")

    def test_error2(self):
        self.assertRaises(KeyError, tarea3.run, "(with (y (+ 30 y)) (+ x (- y 40)))")


if __name__ == '__main__':
    unittest.main(verbosity=2)
