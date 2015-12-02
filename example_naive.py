from role_criteria import *
from logical_node import *
from naive_centralized_algorithm import *

class MockRoleCriteria(RoleCriteria):
    def __init__(self, name, node_grade_map):
        self.name = name
        self.node_grade_map = node_grade_map

    def evaluate_against(self, node_parameters):
        return self.node_grade_map[node_parameters["node_id"]]

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

role_assignment_service = RoleAssignmentService(role_criterias)

for node in nodes:
    role_assignment_service.evaluate_node(node)

unassigned_roles = role_assignment_service.compute_role_assignment()
if not unassigned_roles:
    print "Success! All roles assigned"
    for node in nodes:
        node_id = node.node_id
        role_id = role_assignment_service.get_role_assignment(node_id)
        print "Node %d's role: %s" % (node_id, role_criterias[role_id].name)
else:
    print "Error! Some roles couldn't be satisfied"
    for role_id in unassigned_roles:
        print "Role %d: %s" % (role_id, role_criterias[role_id].name)
