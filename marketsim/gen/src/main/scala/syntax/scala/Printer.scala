package syntax.scala

import Types._

class Printer() extends PrettyPrinter.Base {

    def apply(x : Type) = x match {
        case _ : `Float` => "Float"
        case _ : Unit => "()"
        case Tuple(lst) => pars(lst.mkString(","))
        case Function(args, ret) => s"$args => $ret"
    }

    def pars(s : Any, condition : Boolean = true) =
        if (condition) "(" + s + ")" else s.toString

    def apply(e : AST.BooleanExpr) = e match {
        case AST.Or(x, y) => x + " or " + y
        case AST.And(x, y) =>
            def wrap(z : AST.BooleanExpr) = pars(z, z.isInstanceOf[AST.Or])
            wrap(x) + " and " + wrap(y)
        case AST.Not(x) =>
            def wrap(z : AST.BooleanExpr) = pars(z, !z.isInstanceOf[AST.Condition])
            "not " + wrap(x)
        case AST.Condition(c, x, y) => x.toString + c + y
    }

    def apply(c : AST.CondSymbol) = c match {
        case AST.Less() => "<"
        case AST.LessEqual() => "<="
        case AST.Greater() => ">"
        case AST.GreaterEqual() => ">="
        case AST.Equal() => "="
        case AST.NotEqual() => "<>"
    }

    def priority(e : AST.Expr) = e match {
        case _ : AST.Const => 0
        case _ : AST.Var => 0
        case _ : AST.Neg => 0
        case _ : AST.FunCall => 0
        case AST.BinOp(AST.Mul(), _, _) => 1
        case AST.BinOp(AST.Div(), _, _) => 1
        case AST.BinOp(AST.Add(), _, _) => 2
        case AST.BinOp(AST.Sub(), _, _) => 2
        case _ : AST.IfThenElse => 3
    }

    def need_brackets(x : AST.Expr, e : AST.Expr, rhs : Boolean = false) =
        priority(x) > priority(e) || priority(x) == priority(e) && rhs

    def wrap(x : AST.Expr, e : AST.Expr, rhs : Boolean = false) =
        pars(x, need_brackets(x, e, rhs))

    def apply(e : AST.Expr) = e match {
        case AST.BinOp(symbol, x, y) => wrap(x, e) + symbol + wrap(y, e, rhs = true)
        case AST.Neg(x) => "-" + wrap(x, e)
        case AST.IfThenElse(cond, x, y) => s"if $cond then ${wrap(x,e)} else ${wrap(y,e)}"
        case AST.FunCall(name, args) => name + pars(args.mkString(","))
        case AST.Const(x) => x.toString
        case AST.Var(s) => s
    }

    def apply(s : AST.BinOpSymbol) = s match {
        case AST.Add() => "+"
        case AST.Sub() => "-"
        case AST.Mul() => "*"
        case AST.Div() => "/"
    }

}