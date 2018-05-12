import random
from pddlsim.local_simulator import LocalSimulator
from  PlanParser import PlanParser
#from pddlsim.successors.tracked_successor import TrackedSuccessor
import pddlsim.planner as planner
from pddlsim.executors.executor import Executor

print "start program"


plan_path = "simple_football_plan.xml"
plan = PlanParser(plan_path).getPlan()
print plan

class PlanDispatcher(Executor):
	"""docstring for PlanDispatcher."""
	def __init__(self):
		super(PlanDispatcher, self).__init__()
		self.steps = []

	def initialize(self,services):
		self.steps = planner.make_plan(services.pddl.domain_path, services.pddl.problem_path)

	def next_action(self):
		if len(self.steps)>0:
			return self.steps.pop(0).lower()
		return None


domain_path = "simple_football_domain.pddl"
problem_path = "simple_football_problem.pddl"
print LocalSimulator().run(domain_path, problem_path, PlanDispatcher())