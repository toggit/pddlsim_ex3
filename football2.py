from pddlsim.local_simulator import LocalSimulator
from pddlsim.executors.executor import Executor
from PlanParser import PlanParser
from Plan import Plan
import sys

if len(sys.argv) != 4:
    sys.exit('Error: missing arguments!!!')

problem_path = sys.argv[3]
if sys.argv[1] == '-s':
    plan_path = "simple_football_plan.xml"
    domain_path = "simple_football_domain.pddl"
elif sys.argv[1] == '-e':
    plan_path = "extended_football_plan.xml"
    domain_path = "extended_football_domain.pddl"
else:
    sys.exit('Error: you must run with valid option -e or -s')

plan = PlanParser(plan_path).getPlan()


class SmartPlanner(Executor):
    """docstring for PlanDispatcher."""
    def __init__(self):
        super(SmartPlanner, self).__init__()
        self.N = int(sys.argv[2])
        self.option = sys.argv[1]
        self.old_state = []
        self.balls_pos = []
        self.agent_position = []
        self.current_state = []
        self.services = []
        self.goal_tile = (1, 5)
        self.last_leg_moved = None
        self.next_leg_to_moved = None
        self.lifted_leg = None
        self.P = plan
        self.b = self.P.nodes[0]
        self.S = []
        self.S.append(self.b)
        self.football_map = {'start_tile': (1, 0),
                             'g0': (0, 1), 'g1': (0, 2), 'g2': (0, 3), 'g3': (0, 4),
                             'c0': (1, 1), 'c1': (1, 2), 'c2': (1, 3), 'c3': (1, 4),
                             'd0': (2, 1), 'd1': (2, 2), 'd2': (2, 3), 'd3': (2, 4),
                             'goal_tile': (1, 5)}

    def initialize(self, services):
        self.services = services

    def next_action(self):

        self.old_state = self.current_state
        self.current_state = self.services.perception.get_state()
        count_ball_in_goal_tile = len([ball for ball in self.current_state['at-ball'] if ball[1] == 'goal_tile'])

        # if number of balls = 0 then we finish.
        if self.N == 0 or self.N - count_ball_in_goal_tile == 0:
            print "all ball in goal tile"
            return None

        while self.is_exists_hierarchical_children():
            valid_actions = self.get_all_valid_sequences_from_h()
            self.b = self.choose(valid_actions)
            self.S.append(self.b)

        action = self.S.pop()
        self.b = self.S[-1]

        return action

    def str_actions_2_tuples(self, str_actions):
        tupled_actions = []

        for action in str_actions:
            splitted_action = action[1:-1].split()
            tupled_actions.append(tuple(splitted_action))

        return tupled_actions

    def check_kick_condition(self):
        for ball in self.balls_pos:
            if self.get_manhattan_distance(self.football_map[self.agent_position], self.football_map[ball]) == 0:
                return True
        return False

    def get_best_move(self, valid_actions):

        shortest_distance = float("inf")
        best_move = None

        move_action_name = 'move'
        if self.option == '-e':
            move_action_name = "move-{0}-leg".format(self.get_leg_to_move_with())

        for action in valid_actions:

            if action[0] == move_action_name:

                ball = self.look_4_closest_ball()
                next_tile = action[2]

                distance = self.get_manhattan_distance(self.football_map[next_tile], self.football_map[ball])

                if distance < shortest_distance:
                    shortest_distance = distance
                    best_move = action

        return best_move

    def take_best_kick(self, valid_actions):

        shortest_distance = float("inf")
        best_kick = None
        kick_action_name = "kick-{0}".format(self.lifted_leg)

        # Get all the valid kicks.
        for action in valid_actions:

            condition = (action[0] == "kick")
            if self.option == '-e':
                condition = (action[0].startswith(kick_action_name))

            if condition:
                ball_pos = action[3]

                distance = self.get_manhattan_distance(self.football_map[ball_pos], self.goal_tile)

                if distance < shortest_distance:
                    shortest_distance = distance
                    best_kick = action

        return best_kick

    def is_exists_hierarchical_children(self):
        if isinstance(self.b, Plan.Node) and self.b.hierarchicalChildren:
            for n in self.b.hierarchicalChildren:
                if n in self.P.nodes:
                    return True
        return False

    def get_all_valid_sequences_from_h(self):

        all_valid_actions = self.str_actions_2_tuples(self.services.valid_actions.get())
        all_valid_actions_in_behaviors = []

        for n in self.b.hierarchicalChildren:
            if n in self.P.nodes:
                for action in all_valid_actions:
                    if action[0].startswith(n.action) or action[0].startswith("lift"):
                        all_valid_actions_in_behaviors.append(action)

        return all_valid_actions_in_behaviors

    def look_4_closest_ball(self):

        shortest_distance = float("inf")
        closest_ball = None

        for ball in self.balls_pos:

            distance = self.get_manhattan_distance(self.football_map[self.agent_position], self.football_map[ball])

            if distance < shortest_distance:
                shortest_distance = distance
                closest_ball = ball

        return closest_ball

    def get_manhattan_distance(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def simple_choose(self, valid_actions):

        if self.check_kick_condition():

            action = self.take_best_kick(valid_actions)

        else:
            action = self.get_best_move(valid_actions)

        str_action = "({0})".format(" ".join(action))

        return str_action

    def get_leg_to_move_with(self):

        if self.next_leg_to_moved == "left":
            return "right"
        else:
            return "left"

    def get_lift_action(self, leg_to_lift, valid_actions):

        lift_action_name = "lift-{0}".format(leg_to_lift)

        for action in valid_actions:
            if action[0] == lift_action_name:
                return action

        return None

    def choose(self, valid_actions):

        if len(valid_actions) == 0:
            return None

        self.agent_position = self.current_state["at-robby"].pop()[0]
        balls_not_in_goal_tile = zip(*[ball for ball in self.current_state['at-ball'] if ball[1] != 'goal_tile'])
        self.balls_pos = balls_not_in_goal_tile[1] if balls_not_in_goal_tile else None

        if not self.balls_pos:
            return None

        if self.option == "-s":
            return self.simple_choose(valid_actions)
        elif self.option == "-e":
            return self.extended_choose(valid_actions)
        else:
            return None

    def extended_choose(self, valid_actions):

        if self.check_kick_condition():

            if self.lifted_leg is None:
                leg_to_lift = "right" if self.last_leg_moved == "left" else "left"
                action = self.get_lift_action(leg_to_lift, valid_actions)
                self.lifted_leg = leg_to_lift
            else:
                action = self.take_best_kick(valid_actions)
                self.last_leg_moved = self.lifted_leg
                self.lifted_leg = None
        else:
            action = self.get_best_move(valid_actions)
            self.last_leg_moved = self.get_leg_to_move_with()

        str_action = "({0})".format(" ".join(action))
        return str_action


print LocalSimulator().run(domain_path, problem_path, SmartPlanner())
