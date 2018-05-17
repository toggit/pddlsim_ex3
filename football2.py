from pddlsim.local_simulator import LocalSimulator
from pddlsim.executors.executor import Executor
import pddlsim.planner as planner
from PlanParser import PlanParser
import sys

if len(sys.argv) != 4:
    sys.exit('Error: missing arguments!!!')

problem_path = sys.argv[3]
if sys.argv[1] == '-s':
    plan_path = "simple_football_plan.xml"
    domain_path = "simple_football_domain.pddl"
if sys.argv[1] == '-e':
    plan_path = "extended_football_plan.xml"
    domain_path = "extended_football_domain.pddl"
else:
    sys.exit('Error: you must run with valid option -e or -s')


class SmartPlanner(Executor):
    """docstring for PlanDispatcher."""
    def __init__(self):
        super(SmartPlanner, self).__init__()
        self.services = []
        self.N = int(sys.argv[2])
        self.plan = PlanParser(plan_path).getPlan()
        self.flag = sys.argv[1]
        self.is_action_was_a_goal = False
        self.last_leg_moved = None
        self.last_lifted_leg = None
        self.S = []
        self.b = self.P.nodes[0]
        self.S.append(self.b)
        self.football_staduim = {'start_tile': {'x': 1, 'y': 0},
                                 'g0': {'x': 0, 'y': 1}, 'g1': {'x': 0, 'y': 2},
                                 'g2': {'x': 0, 'y': 3}, 'g3': {'x': 0, 'y': 4},
                                 'c0': {'x': 1, 'y': 1}, 'c1': {'x': 1, 'y': 2},
                                 'c2': {'x': 1, 'y': 3}, 'c3': {'x': 1, 'y': 4},
                                 'd0': {'x': 2, 'y': 1}, 'd1': {'x': 2, 'y': 2},
                                 'd2': {'x': 2, 'y': 3}, 'd3': {'x': 2, 'y': 4},
                                 'goal_tile': {'x': 1, 'y': 5}}

    def initialize(self, services):
        self.services = services

    def next_action(self):
        if self.is_action_was_a_goal:
            self.N -= 1
            self.is_action_was_a_goal = False

        if self.N == 0:
            return None

        self.bis()
        action2run = self.S.pop()
        self.b = self.S[-1]
        return action2run

    def bis(self):
        """
        run the BIS algorithm.
        :return: None
        """

        while self.b.hierarchicalChildren and self.b.hierarchicalChildren in self.P.nodes:
            all_sequences_from_H = self._get_all_sequences_in_H()
            all_valid_sequences_from_H = self._get_all_valid_sequences_in_H(all_sequences_from_H)
            self.b = self._choose(all_valid_sequences_from_H)
            self.S.append(self.b)

        return 0

    
    
print LocalSimulator().run(domain_path, problem_path, SmartPlanner())