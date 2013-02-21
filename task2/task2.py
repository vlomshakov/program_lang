#!/usr/bin/env python
#coding=utf-8

import sys


# helper classes
class Holder(object):
	def set(self, value):
		self.value = value
		return value
	def get(self):
		return self.value

class SingletonMeta(type):
	def __init__(cls, name, bases, dict):
		super(SingletonMeta, cls).__init__(name, bases, dict)
		cls.instance = None
	def __call__(self,*args,**kw):
		if self.instance is None:
			self.instance = super(SingletonMeta, self).__call__(*args, **kw)
		return self.instance
#---------------------------------------------------------------------------
class SyntaxError_(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg


class RunTimeError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg


class Context(object):
	"""
	A context is singleton. This class keeps state of computation system.
	"""
	__metaclass__ = SingletonMeta

	_vars = {}
	def readInputStream(self):
		return int(raw_input(""))

	def writeOutputStream(self,value):
		print value

	def assigNewValue(self, name, value):
		self._vars[name] = value

	def getValue(self, name):
		try:
			return self._vars[name]
		except KeyError:
			raise RunTimeError("[error][interpreterLangL] used undefined variable: "+name)


#-----------------------------------------------------------------------------------
class Expr(object):
	def evaluate(self):
		raise NotImplementedError('Method Expr.evaluate is pure virtual')


class Variable(Expr):
	def __init__(self, name):
		self._name = name

	def getName(self): return self._name
	
	def evaluate(self):	return Context().getValue(self._name)

class Number(Expr):
	def __init__(self, value):
		self._value = value

	def evaluate(self):
		return self._value


class BinOperator(Expr):
	def __init__(self, left, right, op):
		self._left = left
		self._right = right
		self._op = op
	
	def evaluate(self):
		return int (eval(str(self._left.evaluate()) + self._op + str(self._right.evaluate()) ) )

#-----------------------------------------------------------------------------------
class Stmt(object):
	def interpret(self):
		raise NotImplementedError('Method Stmt.interpret is pure virtual')


class SkipStmt(Stmt):
	def interpret(self):
		pass
	
class AssignStmt(Stmt):
	def __init__(self, var, expr):
		self._var = var
		self._expr = expr
	def interpret(self):
		Context().assigNewValue(self._var.getName(), self._expr.evaluate())

	
class ReadStmt(Stmt):
	def __init__(self, var):
		self._var = var
	def interpret(self):
		Context().assigNewValue(self._var.getName(), Context().readInputStream())

	
class WriteStmt(Stmt):
	def __init__(self, expr):
		self._expr = expr
	def interpret(self):
		Context().writeOutputStream(self._expr.evaluate())

	
class SequenceStmt(Stmt):
	def __init__(self, stmt1, stmt2):
		self._stmt1 = stmt1
		self._stmt2 = stmt2
	def interpret(self):
		self._stmt1.interpret()
		self._stmt2.interpret()

	
class IfStmt(Stmt):
	def __init__(self, expr, stmt1, stmt2):
		self._expr = expr
		self._stmt1 = stmt1
		self._stmt2 = stmt2
	def interpret(self):
		cond = self._expr.evaluate()
		if cond != 0:
			self._stmt1.interpret()
		else:
			self._stmt2.interpret()

	
class WhileStmt(Stmt):
	def __init__(self, expr, stmt):
		self._expr = expr
		self._stmt = stmt
	def interpret(self):
		cond = Holder()
		while cond.set(self._expr.evaluate()):
			self._stmt.interpret()
#---------------------------------------------------------------------------

class InterpreterLangL(object):
	"""
Interpreter language "L" implemented based semantic rule "big step"
	"""
	def __init__(self, instream):
		self._in = instream
		self._scopeInterp = True

	def _get_line(self):
		return self._in.readline().strip()

	def interpretTree(self):
		"""
Visits postorder of tree during reading file and interprets just in time.
Statement shrink after interpreting.
		"""
		symbol = self._get_line()
		node = None
		if not symbol:
			return

		if symbol == '!':
			node = Number(int(self._get_line()))
		elif symbol == 'x':
			node = Variable(self._get_line())
		elif symbol == '@':
			op = self._get_line()
			expr1 = self.interpretTree()
			expr2 = self.interpretTree()
			node = BinOperator(expr1, expr2, op)
		elif symbol == 's':
			node = SkipStmt()
		elif symbol == '=':
			var = Variable(self._get_line()) 
			expr = self.interpretTree()
			node = AssignStmt(var, expr)
		elif symbol == 'w':
			expr = self.interpretTree()
			node = WriteStmt(expr)
		elif symbol == 'r':
			var = Variable(self._get_line())
			node = ReadStmt(var)
		elif symbol == ';':
			stmt1 = self.interpretTree()
			stmt2 = self.interpretTree()	
			node = SequenceStmt(stmt1, stmt2)
		elif symbol == 'i':
			outScopeInterp = self._scopeInterp
			self._scopeInterp = False
			expr  = self.interpretTree()
			stmt1 = self.interpretTree()
			stmt2 = self.interpretTree()
			self._scopeInterp = outScopeInterp
			node = IfStmt(expr, stmt1, stmt2)
		elif symbol == 'l':
			outScopeInterp = self._scopeInterp
			self._scopeInterp = False
			expr  = self.interpretTree()
			stmt = self.interpretTree()
			self._scopeInterp = outScopeInterp
			node = WhileStmt(expr, stmt)
		else:
			raise SyntaxError_("[error][interpreterLangL]not recognize the symbol:\n"+repr(symbol))

		if isinstance(node, Stmt) and self._scopeInterp and \
		not isinstance(node, SequenceStmt):
			node.interpret()

# shrink tree after interpreting
		if isinstance(node, Stmt) and self._scopeInterp:
			return SkipStmt()
		else: 
			return node
		
			
		
		
		




if len(sys.argv) != 2:
	print "no input file"
	sys.exit(1)

f = None
try:
	f = open(sys.argv[1],"r")
	InterpreterLangL(f).interpretTree()
except IOError as e:
	print "I/O error({0}): {1}".format(e.errno, e.strerror)
except SyntaxError_ as e:
	print e
except RunTimeError as e:
	print e
finally:
	if f: f.close()


