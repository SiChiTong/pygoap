# -*- coding: utf-8 -*-

"""
Copyright 2010, Leif Theden

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

ACTIONSTATE_NOT_STARTED = 0
ACTIONSTATE_FINISHED    = 1
ACTIONSTATE_RUNNING     = 2
ACTIONSTATE_PAUSED      = 3

"""
this class was orginally one, but to cut on memory usage, I have
split the action class into two parts based on usage:

* planning
* doing stuff in an environment

there is still a tight coupling between the two, but this will save
memory in this way:
when the game is processing a lot of actions, according to the
environments que, each will have to be instanced, but, this isn't good,
since the planning portion can have high memory requirements

this way, there only needs to be one instance of the planning action node.

"""

__version__ = ".003"

class ActionNodeBase(object):
	"""
	action:
		has a prereuisite
		has a effect
		has a reference to a class to "do" the action

		once completed, then clean the memory (blackboard needs to be cleaned)

	this is like a singleton class, to cut down on memory usage

	TODO:
		use XML to store the action's data.
		these actions will "eval" statements.
		names are matched as locals inside the bb passed
	"""

	def __init__(self, name, p=None, e=None):
		self.name = name
		self.prereqs = []
		self.effects = []

		self.start_func = None

		try:
			self.effects.extend(e)
		except:
			self.effects.append(e)

		try:
			self.prereqs.extend(p)
		except:
			self.prereqs.append(p)

	def set_action_class(self, klass):
		self.action_class = klass

	def valid(self, bb):
		"""Given the bb, can we run this action?"""
		raise NotImplementedError

	# this is run when the action is succesful
	# do something on the blackboard (varies by subclass)
	def touch(self, bb):
		raise NotImplementedError

	def __repr__(self):
		return "<Action=\"%s\">" % self.name

class SimpleActionNode(ActionNodeBase):
	def valid(self, bb):
		for p in self.prereqs:
			if p.valid(bb) == False:
				return False

		return True

	def touch(self, bb):
		[e.touch(bb) for e in self.effects]

class CallableAction(object):
	# when instanced, should be added to a que that will process
	# not to be confused with a "SimplAction" which is used for
	# planning.  Can be subclassed, etc.
	# instead of duplicating the validator class, just have a
	# reference to it to do that stuff
	# also, emulate valid and touch
	
	def __init__(self, caller, validator):
		self.caller = caller
		self.validator = validator
		self.state = ACTIONSTATE_NOT_STARTED

	def touch(self):
		self.validator.touch(self.caller.blackboard)
		
	def valid(self):
		return self.validator.valid(self.caller.blackboard)

	def start(self):
		self.state = ACTIONSTATE_RUNNING
		print "starting:", self.__class__.__name__, self.caller

	def update(self):
		raise NotImplementedError

	def finish(self):
		self.state = ACTIONSTATE_FINISHED

class CalledOnceAction(CallableAction):
	"""
	Is finished imediatly when started.
	"""
	def start(self):
		self.state = ACTIONSTATE_FINISHED
		print "doing:", self.__class__.__name__, self.caller

	def update(self):
		pass

	def finish(self):
		pass
	
class PausableAction(CallableAction):
	def pause(self):
		self.state = ACTIONSTATE_PAUSED