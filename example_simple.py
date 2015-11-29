from token import *
from network import *
from logical_node import *
from role_criteria import *

##################################################################################
# Example code that roughly shows how the framework is to be used. Note: the
# relationship between the network and the logical nodes will likely change.
##################################################################################
class MyAwesomeRoleCriteria(RoleCriteria):
    def __init__(self, name, happy, excited):
        self.name = name
        self.happy = happy
        self.excited = excited

    def evaluate_against(self, node_parameters):
        return self.happy == node_parameters["happy"] and self.excited == node_parameters["excited"]

if __name__ == '__main__':

    # Clients will define their own RoleCriteria, which will expect
    # a certain set of parameters to evaluate on
    role_criteria_0 = MyAwesomeRoleCriteria("very sad", happy=False, excited=False)
    role_criteria_1 = MyAwesomeRoleCriteria("just content", happy=True, excited=False)
    role_criteria_2 = MyAwesomeRoleCriteria("freaking excited", happy=True, excited=True)
    role_criterias = [role_criteria_0, role_criteria_1, role_criteria_2]

    network = SimulatedNetwork(role_criterias)

    node_0 = LogicalNode(0, [1, 2], network, parameters={ "happy": True, "excited": True })
    node_1 = LogicalNode(1, [], network, parameters={ "happy": True, "excited": True })
    node_2 = LogicalNode(2, [3], network, parameters={ "happy": False, "excited": False })
    node_3 = LogicalNode(3, [], network, parameters={ "happy": True, "excited": False })
    nodes = [node_0, node_1, node_2, node_3]

    network.set_logical_nodes(nodes)

    token = node_0.begin_logical_assignment(role_criterias)

    if token:
        print "Error! Some roles couldn't be satisfied"
        for role_id in token.unassigned_roles:
            print "Role %d: %s" % (role_id, role_criterias[role_id].name)
    else:
        print "Success! All roles assigned!"
        for node in nodes:
            if node.assigned_role is not None:
                print "Node %d's role: %s" % (node.node_id, role_criterias[node.assigned_role].name)