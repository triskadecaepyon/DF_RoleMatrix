import sys

class RoleAssignmentService():

    def __init__(self, role_criterias):
        self.role_criterias = role_criterias
        self.bytes_received = 0
        self.bytes_sent = 0

        self.role_satisfaction_map = {}
        self.role_assignment_map = {}
        self.unassigned_roles = None

    def get_bytes_sent(self):
        return self.bytes_sent

    def get_bytes_received(self):
        return self.bytes_received

    def evaluate_node(self, node):
        self.bytes_received += sys.getsizeof(node.parameters)
        self.bytes_received += sys.getsizeof(node.node_id)

        self.role_satisfaction_map[node.node_id] = \
            set([role_id for (role_id, role_criteria) in \
                enumerate(self.role_criterias) if role_criteria.evaluate_against(node.parameters) > 0])

    def _compute_role_assignment(self, node_id, unassigned_roles):
        if not unassigned_roles:
            self.unassigned_roles = None
            return True

        if node_id >= len(self.role_satisfaction_map):
            self.unassigned_roles = set(unassigned_roles)
            return False

        assignable_roles = self.role_satisfaction_map[node_id].intersection(unassigned_roles)
        if assignable_roles:
            for role_id in assignable_roles:
                unassigned_roles.remove(role_id)

                if self._compute_role_assignment(node_id + 1, unassigned_roles):
                    self.role_assignment_map[node_id] = role_id
                    return True

                unassigned_roles.add(role_id)

            return False

        elif self._compute_role_assignment(node_id + 1, unassigned_roles):
            return True

        else:
            return False

    def compute_role_assignment(self):
        unassigned_roles = set(range(len(self.role_criterias)))
        self._compute_role_assignment(0, unassigned_roles)

        self.bytes_sent += sys.getsizeof(unassigned_roles)

        return self.unassigned_roles

    def get_role_assignment(self, node_id):
        self.bytes_received += sys.getsizeof(node_id)

        role_assignment = self.role_assignment_map[node_id]

        self.bytes_sent += sys.getsizeof(role_assignment)

        return role_assignment

