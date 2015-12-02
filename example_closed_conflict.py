from token import *
from network import *
from logical_node import *
from role_criteria import *

##################################################################################
# Example code that roughly shows how the framework is to be used. Note: the
# relationship between the network and the logical nodes will likely change.
##################################################################################
class MockRoleCriteria(RoleCriteria):
    def __init__(self, name, node_grade_map):
        self.name = name
        self.node_grade_map = node_grade_map

    def evaluate_against(self, node_parameters):
        return self.node_grade_map[node_parameters["node_id"]]

# Clients will define their own RoleCriteria, which will expect
# a certain set of parameters to evaluate on
role_criterias = [
    MockRoleCriteria("rc0", {0: 1, 1: 0, 2: 3}),
    MockRoleCriteria("rc1", {0: 4, 1: 4, 2: 0}),
    MockRoleCriteria("rc2", {0: 0, 1: 8, 2: 0})
]

nodes = [
    LogicalNode(0, { "node_id": 0 }, role_criterias),
    LogicalNode(1, { "node_id": 1 }, role_criterias),
    LogicalNode(2, { "node_id": 2 }, role_criterias)
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