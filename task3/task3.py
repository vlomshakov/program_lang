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

	_this = Label(TypeLabel.No)
	_next = Label(TypeLabel.Maybe, 0)
	_last = 0

	def getNext(self): return self._next
	def setNext(self, label): self._next = label

	def getThis(self): return self._this
	def setThis(self, label): self._this = label 

	def getLast(self): return self._last
	def setLast(self, value): self._last = value

	@staticmethod
	def first(label,program):
		if label == TypeLabel.Yes:
			program[0] = "$" + str(label.getNum()) + ": " + program[0]
			return program
		elif label == TypeLabel.No:
			return program
		raise Exception("failure -- first was called for Maybe")

	@staticmethod
	def last(label,program):
		if label == TypeLabel.Yes:
			program.append("J $" + str(label.getNum())
			return program
		elif label == TypeLabel.Maybe:
			return program
		raise Exception("failure -- first was called for No")

	@staticmethod
	def frame(f,l,program):
		return Context.last(l,Context.first(f,program))


#-----------------------------------------------------------------------------------
class TypeLabel:
	Yes = 0
	Maybe = 1
	No = 2

class Label(object):
	def __init__(self,typeLabel):
		self._type = typeLabel;
		self._number = None

	def __init__(self,typeLabel,number):
		self._type = typeLabel
		self._number = number

	def getNum(self) :
		if _type != TypeLabel.No:
			return _number
		raise Exception("failure -- gets number for No")

	def __eq__(self,other): return self._type == other

	def __ne__(self,other): return self._type != other		

	def force(self):
		if self._type == TypeLabel.Maybe:
			self._type = TypeLabel.Yes
		elif self._type == TypeLabel.No:
			raise Exception("failure -- force No")



#-----------------------------------------------------------------------------------
class Instruction:
	LOAD   = "L "
	STORE  = "S "
	CREATE = "C "
	BINOP  = "B "
	WRITE  = "W"
	READ   = "R"


class Expr(object):
	def gen(self):
		raise NotImplementedError('Method Expr.gen is pure virtual')


class Variable(Expr):
	def __init__(self, name):
		self._name = name

	def getName(self): return self._name
	
	def gen(self):	
		return Context.first(Context().getThis(), [Instruction.LOAD + self._name])

class Number(Expr):
	def __init__(self, value):
		self._value = value

	def gen(self):
		return Context.first(Context().getThis(), [Instruction.CREATE + self._value])


class BinOperator(Expr):
	def __init__(self, left, right, op):
		self._left = left
		self._right = right
		self._op = op
	
	def gen(self):
		A = self._left.gen()
		Context().setThis(Label(TypeLabel.No))
		B = self._right.gen()

		return (A + B).append(Instruction.BINOP + self._op)

#-----------------------------------------------------------------------------------
class Stmt(object):
	def gen(self):
		raise NotImplementedError('Method Stmt.gen is pure virtual')


class SkipStmt(Stmt):
	def gen(self):
		pass
	
class AssignStmt(Stmt):
	def __init__(self, var, expr):
		self._var = var
		self._expr = expr
	def gen(self):
		E = self._expr.gen()
		E.append(Instruction.STORE + self._var.getName())
		return Context.last(Context().getNext(), E )
		

	
class ReadStmt(Stmt):
	def __init__(self, var):
		self._var = var
	def gen(self):
		P = [Instruction.READ, Instruction.STORE + self._var.getName()]
		return Context.frame(Context().getThis(), Context().getNext(), I)

	
class WriteStmt(Stmt):
	def __init__(self, expr):
		self._expr = expr
	def gen(self):
		E = self._expr.gen()
		E.append(Instruction.WRITE)
		return Context.last(Context().getNext(), E)

	
class SequenceStmt(Stmt):
	def __init__(self, stmt1, stmt2):
		self._stmt1 = stmt1
		self._stmt2 = stmt2
	def gen(self):
		self._stmt1.gen()
		self._stmt2.gen()

	
class IfStmt(Stmt):
	def __init__(self, expr, stmt1, stmt2):
		self._expr = expr
		self._stmt1 = stmt1
		self._stmt2 = stmt2
	def gen(self):
		E = self._expr.gen()
		Context().setThis(Label(TypeLabel.No))
		Context.force(Context().getNext())
		last1 = Context().getLast() + 1
		Context().setLast(last1)
		S2 = self._stmt2.gen()
		Context().setThis(Label(TypeLabel.Yes, last1))
		


	
class WhileStmt(Stmt):
	def __init__(self, expr, stmt):
		self._expr = expr
		self._stmt = stmt
	def gen(self):
		cond = Holder()
		while cond.set(self._expr.gen()):
			self._stmt.gen()
#---------------------------------------------------------------------------

class CompilerLangL(object):
	"""
Interpreter language "L" implemented based semantic rule "big step"
	"""
	def __init__(self, instream):
		self._in = instream
		self._scopeInterp = True

	def _get_line(self):
		return self._in.readline().strip()

	def buildTree(self):
		"""
Visits postorder of tree during reading file and build tree in memory
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
			expr1 = self.buildTree()
			expr2 = self.buildTree()
			node = BinOperator(expr1, expr2, op)
		elif symbol == 's':
			node = SkipStmt()
		elif symbol == '=':
			var = Variable(self._get_line()) 
			expr = self.buildTree()
			node = AssignStmt(var, expr)
		elif symbol == 'w':
			expr = self.buildTree()
			node = WriteStmt(expr)
		elif symbol == 'r':
			var = Variable(self._get_line())
			node = ReadStmt(var)
		elif symbol == ';':
			stmt1 = self.buildTree()
			stmt2 = self.buildTree()	
			node = SequenceStmt(stmt1, stmt2)
		elif symbol == 'i':
				
			expr  = self.buildTree()
			stmt1 = self.buildTree()
			stmt2 = self.buildTree()
			
			node = IfStmt(expr, stmt1, stmt2)
		elif symbol == 'l':
			
			expr  = self.buildTree()
			stmt = self.buildTree()
			
			node = WhileStmt(expr, stmt)
		else:
			raise SyntaxError_("[error][CompilerLangL]not recognize the symbol:\n"+repr(symbol))

			return node
		
			
		
		
		




if len(sys.argv) != 2:
	print "no input file"
	sys.exit(1)

f = None
try:
	f = open(sys.argv[1],"r")
	CompilerLangL(f).buildTree()
except IOError as e:
	print "I/O error({0}): {1}".format(e.errno, e.strerror)
except SyntaxError_ as e:
	print e
except RunTimeError as e:
	print e
finally:
	if f: f.close()


