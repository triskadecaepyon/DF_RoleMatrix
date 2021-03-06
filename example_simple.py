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
        return int(self.happy == node_parameters["happy"] and self.excited == node_parameters["excited"])

# Clients will define their own RoleCriteria, which will expect
# a certain set of parameters to evaluate on
role_criterias = [
    MyAwesomeRoleCriteria("very sad", happy=False, excited=False),
    MyAwesomeRoleCriteria("just content", happy=True, excited=False),
    MyAwesomeRoleCriteria("freaking excited", happy=True, excited=True)
]

nodes = [
    LogicalNode(0, { "happy": True, "excited": True }, role_criterias),
    LogicalNode(1, { "happy": True, "excited": True }, role_criterias),
    LogicalNode(2, { "happy": False, "excited": False }, role_criterias),
    LogicalNode(3, { "happy": True, "excited": False }, role_criterias)
]

if __name__ == '__main__':

    network = SimulatedNetwork(nodes)

    token = nodes[0].begin_logical_assignment()

    if token:
        print "Error! Some roles couldn't be satisfied"
        for role_id in token.unassigned_roles:
            print "Role %d: %s" % (role_id, role_criterias[role_id].name)
    else:
        print "Success! All roles assigned!"
        for node in nodes:
            if node.assigned_role is not None:
                print "Node %d's role: %s" % (node.node_id, role_criterias[node.assigned_role].name)