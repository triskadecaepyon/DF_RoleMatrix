from token import *
from network import *
from logical_node import *
from role_criteria import *

import sys

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

node_ip_addresses = [
    ("localhost", 5005),
    ("localhost", 5006),
    ("localhost", 5007)
]

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "USAGE: python example_live_network.py command NODE_ID"
        exit(1)

    command = sys.argv[1].lower()
    node_id = int(sys.argv[2])

    if command == "start_node":
        node = nodes[node_id]
        network = LiveNetwork(node, node_ip_addresses)
        network.start_server()

    elif command == "begin_algorithm":

        client = LiveNetwork.create_client(node_ip_addresses[node_id])
        token = client.begin_logical_assignment()

        if token:
            print "Error! Some roles couldn't be satisfied"
            for role_id in token.unassigned_roles:
                print "Role %d: %s" % (role_id, role_criterias[role_id].name)
        else:
            print "Success! All roles assigned!"
            for node_ip_address in node_ip_addresses:
                node = LiveNetwork.create_client(node_ip_address)
                if node.assigned_role is not None:
                    print "Node %d's role: %s" % (node.node_id, role_criterias[node.assigned_role].name)
    else:
        print "Unrecognized command: %s" % command