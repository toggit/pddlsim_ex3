import sys
import os
from pddlsim.local_simulator import LocalSimulator
from PlanParser import PlanParser
import pddlsim.planner as planner
from pddlsim.executors.executor import Executor

print "start program"

if len(sys.argv) == 4:
    try:
        N = int(sys.argv[2])
    except ValueError:
        sys.exit('Error: except N to be a number, but N = ' + sys.argv[2])
    problem_path = sys.argv[3]
    if not os.path.exists(problem_path):
        sys.exit('problem_file path does not exist: ' + problem_path)
    if sys.argv[1] == '-s':
        plan_path = "simple_football_plan.xml"
        domain_path = "simple_football_domain.pddl"
    if sys.argv[1] == '-e':
        plan_path = "extended_football_plan.xml"
        domain_path = "extended_football_domain.pddl"
else:
    error_msg = 'Error: missing arguments expected 3 arguments, but got ', (len(sys.argv)-1)
    sys.exit(error_msg)

plan = PlanParser(plan_path).getPlan()
print plan
plan.printPlan()
plan.toDotFile("planxml.txt")

class PlanDispatcher(Executor):
    """docstring for PlanDispatcher."""
    def __init__(self):
        super(PlanDispatcher, self).__init__()
        self.steps = [] 

    def initialize(self,services):
        self.services = services
        self.steps = planner.make_plan(services.pddl.domain_path, services.pddl.problem_path)

    def next_action(self):
        print self.services.perception.get_state()
        if len(self.steps)>0:
            return self.steps.pop(0).lower()
        return None

    def bis(self):
        execution_stack = 0
        
        return 0
    
    
print LocalSimulator().run(domain_path, problem_path, PlanDispatcher())