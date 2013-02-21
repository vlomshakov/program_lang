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
			raise RunTimeError("[erorr][Interpretater] used undefined variable: "+name)




#postorder
class NodeIterator(object):
	def __init__(self, node):
		self.stack = [[node,False]]

	def __iter__(self):
		return self

	def next(self):
		if not self.stack:
			raise StopIteration
		
		node = self.stack[-1][0]
		visit = self.stack[-1][1]
		while node.getLeft() and not visit:
			self.stack[-1][1] = True
			if node.getMid(): self.stack.append([node.getMid(),False])
			if node.getRight():	self.stack.append([node.getRight(),False])
			self.stack.append([node.getLeft(),False])
			node = node.getLeft()
		
		return self.stack.pop()[0]
#-----------------------------------------------------------------------------------
class Node(object):
	_left = None;
	_right = None;
	_mid   = None;
	
	def getLeft(self): return self._left
	def getRight(self): return self._right
	def getMid(self): return self._mid

	def preVisit(self):
		raise NotImplementedError('Method Node.travels is pure virtual')

	def postVisit(self):
		raise NotImplementedError('Method Node.travels is pure virtual')

	def __iter__(self):
		return NodeIterator(self)
#-----------------------------------------------------------------------------------
class Expr(Node):
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
		Parent._left = left
		Parent._right = right
		self._op = op
	
	def evaluate(self):
		return int (eval(str(self.getLeft().evaluate()) + self._op + str(self.getRight().evaluate()) ) )

#-----------------------------------------------------------------------------------
class Stmt(Node):
	def interpret(self):
		raise NotImplementedError('Method Stmt.interpret is pure virtual')


class SkipStmt(Stmt):
	def interpret(self):
		pass
	
class AssignStmt(Stmt):
	def __init__(self, left, right):
		Parent._left = left
		Parent._right = right
	def interpret(self):
		Context().assigNewValue(self.getLeft().getName(), self.getRight().evaluate())

class ReadStmt(Stmt):
	def __init__(self, left):
		Parent._left = left
	def interpret(self):
		Context().assigNewValue(self.getLeft().getName(), Context().readInputStream())		
	
class WriteStmt(Stmt):
	def __init__(self, left):
		Parent._left = left
	def interpret(self):
		Context().writeOutputStream(self.getLeft().evaluate())

class SequenceStmt(Stmt):
	def __init__(self, left, right):
		Parent._left = left
		Parent._right = right
	def interpret(self):
		self.getLeft().interpret()
		self.getLeft().interpret()

class IfStmt(Stmt):
	def __init__(self, cond, stmt1, stmt2):
		Parent._left = cond
		Parent._mid = stmt1
		Parent._right = stmt2
	def interpret(self):
		cond = self.getLeft().evaluate()
		if cond == 0:
			self.getRight().interpret()
		else:
			self.getMid().interpret()

class WhileStmt(Stmt):
	def __init__(self, cond, stmt):
		Parent._left = cond
		Parent._right = stmt
	def interpret(self):
		cond = Holder()
		while cond.set(self.getLeft().evaluate()):
			self.getRight().interpret()
		









r = Node(Node(None,None), Node(Node(None,None),None))

for i in r:
	print i.val