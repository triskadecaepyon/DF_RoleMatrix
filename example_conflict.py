from token import *
from network import *
from logical_node import *
from role_criteria import *

'''
        node_0 evaluates rc0, rc1, and rc2, resulting in the following grade vector g1 = [1, 4, 0]
        node_1 evaluates rc0, rc1, and rc2, resulting in the following grade vector g2 = [0, 4, 8]
        node 2 evalutess rc0, rc1, and rc2, resulting in the following grade vector g3 = [3, 0, 0]
'''
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

if __name__ == '__main__':

    # Clients will define their own RoleCriteria, which will expect
    # a certain set of parameters to evaluate on
    role_criteria_0 = MockRoleCriteria("rc0", {0: 1, 1: 0, 2: 3})
    role_criteria_1 = MockRoleCriteria("rc1", {0: 4, 1: 4, 2: 0})
    role_criteria_2 = MockRoleCriteria("rc2", {0: 0, 1: 8, 2: 0})
    role_criterias = [role_criteria_0, role_criteria_1, role_criteria_2]

    network = SimulatedNetwork(role_criterias)

    node_0 = LogicalNode(0, [1, 2], network, parameters={ "node_id": 0 })
    node_1 = LogicalNode(1, [], network, parameters={ "node_id": 1 })
    node_2 = LogicalNode(2, [], network, parameters={ "node_id": 2 })
    nodes = [node_0, node_1, node_2]

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