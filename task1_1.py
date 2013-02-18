#!/usr/bin/env python
#coding=utf-8
import sys
import re



#--------------------------------------------------------------------------
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


class Table(object):
  """
    A symbol table is singleton. This class keeps value of marks.
  """
  __metaclass__ = SingletonMeta
  
  mark_table = {}
  def add_symbol(self, name, value):
    self.mark_table[name] = value
  def get_value(self, name):
    try:
      val = self.mark_table[name]
    except KeyError:
      raise RunTimeError("[erorr][StackMachine] used undefined mark")
    return val

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
    
#---------------------------------------------------------------------------

# OP_CODE
C,L,S,R,W,B,J,JT,JF,E = range(10)
#PLUS,MINUS,MUL,MOD,DIV,EQ,NEQ,\
#LESS,GR,LE,GE,OR,AND 



class Parser(object):
  """
  Commands Parser
  """
  program = []
  
  def __init__(self, in_s):
    self.in_stream = in_s;
    self.regexp_C  = re.compile(r'^\s*C\s*(\d+)\s*$')
    self.regexp_L  = re.compile(r'^\s*L\s*([a-zA-Z_]+\w*)\s*$')
    self.regexp_S  = re.compile(r'^\s*S\s*([a-zA-Z_]+\w*)\s*$')
    self.regexp_R  = re.compile(r'^\s*R\s*$')
    self.regexp_W  = re.compile(r'^\s*W\s*$')
    self.regexp_B  = re.compile(r'^\s*B\s*([\+\-\*\/\%\>\<]|or|and|\!\=|\=\=|\>\=|\<\=)\s*$')
    self.regexp_JT = re.compile(r'^\s*JT\s*\$(\w+)\s*$')
    self.regexp_JF = re.compile(r'^\s*JF\s*\$(\w+)\s*$')
    self.regexp_J  = re.compile(r'^\s*J\s*\$(\w+)\s*$')
    self.regexp_E  = re.compile(r'^\s*E\s*$')
    self.regexp_MARK = re.compile(r'^\s*\$(\w*):(.*)$')
    self.regexp_SKIP = re.compile(r'^\s+$')
    

  def _get_line(self):
    return self.in_stream.readline()

  def get_cmd(self, str):
    m = Holder()
    if not str:
      raise StopIteration()

    if m.set(self.regexp_C.match(str)) :
      return [C, m.get().group(1)]
    elif m.set(self.regexp_L.match(str)) :
      return [L, m.get().group(1)]
    elif m.set(self.regexp_S.match(str)) :
      return [S, m.get().group(1)]
    elif m.set(self.regexp_R.match(str)) :
      return [R]
    elif m.set(self.regexp_W.match(str)) :
      return [W]
    elif m.set(self.regexp_B.match(str)) :
      return [B, m.get().group(1)]
    elif m.set(self.regexp_JT.match(str) ):
      return [JT, m.get().group(1)]
    elif m.set(self.regexp_JF.match(str) ):
      return [JF, m.get().group(1)]
    # JT, JF has  increasing prefix longer than J
    elif m.set(self.regexp_J.match(str)) :
      return [J, m.get().group(1)]
    elif m.set(self.regexp_E.match(str)) :
      return [E]
    elif m.set(self.regexp_SKIP.match(str)):
      return self.get_cmd(self._get_line())
    elif m.set(self.regexp_MARK.match(str)):
      Table().add_symbol(m.get().group(1), len(self.program))
# print m.get().group(1), m.get().group(2)
      return self.get_cmd(m.get().group(2)+"\n")
    else:
      raise SyntaxError_("[error][Parser]not recognize the command:\n"+str);

  def __iter__(self):
    return self

  def next(self):
    str = self._get_line()
    return self.get_cmd(str)
  
  def compile(self):
    for i in self:
      self.program.append(i)
    return self.program


class StackMachine(object):
  """
  Stack machine implementation run mainloop of interpreter.
  """
  def print_state(self, var, stack):
    print "State of variables:"
    for vname, value in var.iteritems():
      print vname,"=",value

    print "\nState of stack:"
    for i in reversed(stack):
      print i,'->',
    print "null"

  def run(self, program):
    var = {}
    stack = []
    pc = 0 #counter of instruction

    try:
      while True:
        op = program[pc][0]
        if len(program[pc]) == 2:
          arg = program[pc][1]

        if op == C: stack.append(int(arg)); pc += 1
        elif op == L: stack.append(var[arg]); pc += 1 
        elif op == S: var[arg] = stack.pop(); pc += 1
        elif op == R: stack.append( int( raw_input())); pc += 1
        elif op == W: print stack.pop(); pc += 1
        #hack - using eval
        elif op == B: 
          r = str(stack.pop())
          l = str(stack.pop())
          stack.append(int( eval(l + arg + r)) ); 
          pc += 1 
        elif op == J: 
          if arg.isdigit(): pc = int(arg) - 1
          else: pc = Table().get_value(arg)
        elif op == JT:
          if stack.pop():
            if arg.isdigit(): pc = int(arg) - 1
            else: pc = Table().get_value(arg)
          else:
            pc += 1 
        elif op == JF:
          if not stack.pop():
            if arg.isdigit(): pc = int(arg) - 1
            else: pc = Table().get_value(arg)
          else:
            pc += 1
        elif op == E: break

    except KeyError:
      raise RunTimeError("[erorr][StackMachine][#instr:"+str(pc+1)+"]used uninitialized variable")
    except IndexError:
      raise RunTimeError("[erorr][StackMachine][#instr:"+str(pc+1)+"]illegal argument of jump instruction or stack underflow")

    # print "Execution finished."
    # print "Ending state of machine:"
    # self.print_state(var,stack)
    





if len(sys.argv) != 2:
  print "no input file"
  sys.exit(1)

f = None
try:  
  f = open(sys.argv[1],"r")
  parser = Parser(f)
  program = parser.compile()
# print program
# print Table().mark_table
  StackMachine().run(program)
except IOError as e:
  print "I/O error({0}): {1}".format(e.errno, e.strerror)
except SyntaxError_ as e:
  print e
except RunTimeError as e:
  print e
finally:
  if f:
    f.close()





