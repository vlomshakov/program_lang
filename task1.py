#!/usr/bin/env python
#coding=utf-8
import sys
import re

C,L,S,R,W,B,J,JT,JF,E = range(10)
#PLUS,MINUS,MUL,MOD,DIV,EQ,NEQ,\
#LESS,GR,LE,GE,OR,AND 

class Holder(object):
  def set(self, value):
    self.value = value
    return value
  def get(self):
    return self.value


class SyntaxError_(Exception):
  def __init__(self, msg):
    self.msg = msg
  def __str__(self):
    return self.msg

#Commands Parser
class Parser(object):

  def __init__(self, in_s):
    self.in_stream = in_s;
    self.regexp_C  = re.compile(r'^\s*C(\d+)\s*$')
    self.regexp_L  = re.compile(r'^\s*L([a-zA-KM-Z_]+\w*)\s*$')
    self.regexp_S  = re.compile(r'^\s*S([a-zA-KM-Z_]+\w*)\s*$')
    self.regexp_R  = re.compile(r'^\s*R\s*$')
    self.regexp_W  = re.compile(r'^\s*W\s*$')
    self.regexp_B  = re.compile(r'^\s*B([\+\-\*\/\%\>\<]|\|\||\&\&|\!\=|\=\=|\>\=|\<\=)\s*$')
    self.regexp_J  = re.compile(r'^\s*J(\d+)\s*$')
    self.regexp_JT = re.compile(r'^\s*JT(\d+)\s*$')
    self.regexp_JF = re.compile(r'^\s*JF(\d+)\s*$')
    self.regexp_E  = re.compile(r'^\s*E\s*$')
    self.regexp_SKIP = re.compile(r'^\s+$')
    

  def _get_line(self):
    return self.in_stream.readline()

  def get_cmd(self):
    m = Holder()
    str = self._get_line()
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
    elif m.set(self.regexp_J.match(str)) :
      return [J, m.get().group(1)]
    elif m.set(self.regexp_JT.match(str) ):
      return [JT, m.get().group(1)]
    elif m.set(self.regexp_JF.match(str) ):
      return [JF, m.get().group(1)]
    elif m.set(self.regexp_E.match(str)) :
      return [E]
    elif m.set(self.regexp_SKIP.match(str)) :
      return self.get_cmd()
    else:
      raise SyntaxError_('[error][Parser]not recognize the command:\n'+str);

  def __iter__(self):
    return self

  def next(self):
    return self.get_cmd()
   

class RunTimeError(Exception):
  def __init__(self, msg):
    self.msg = msg
  def __str__(self):
    return self.msg
    

class StackMachine(object):

  def print_state(self, var, stack):
    print "State of variables:"
    for vname, value in var.iteritems():
      print vname,"=",value

    print "State of stack:"
    for i in reversed(stack):
      print i

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
        elif op == B: stack.append(int( eval(str(stack.pop()) + arg + str(stack.pop()) )) ); pc += 1 
        elif op == J: pc = int(arg)-1
        elif op == JT:
          if not stack.pop():
            pc = int(arg)-1 
          else:
            pc += 1 
        elif op == JF:
          if stack.pop():
            pc = int(arg)-1
          else:
            pc += 1
        elif op == E: break

    except KeyError:
      raise RunTimeError("[erorr][StackMachine][#instr:"+str(pc+1)+"]used uninitialized variable")
    except IndexError:
      raise RunTimeError("[erorr][StackMachine][#instr:"+str(pc+1)+"]illegal argument of jump instruction or stack underflow")

    print "Execution finished"
    print "Ending state of machine:"
    self.print_state(var,stack)
    





if len(sys.argv) != 2:
  print "no input file"
  sys.exit(1)

f = None
try:  
  f = open(sys.argv[1],"r")
  parser = Parser(f)
  program = []
  for i in parser:
    program.append(i)

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





