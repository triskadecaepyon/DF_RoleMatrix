from collections import deque

class Token:

    def __init__(self, role_ids, node_ids_ordered_by_flexibility):
        self.unassigned_roles = set(role_ids)
        self.node_ids_ordered_by_flexibility = deque(node_ids_ordered_by_flexibility)

    def determine_assignable_roles(self, satisfiable_roles):
        """
        Based on a node's satisfiable roles and the currently unassigned
        roles, determine all assignable roles for that node
        """
        return satisfiable_roles.intersection(self.unassigned_roles)

    def record_assigned_role(self, role_id):
        """
        Called by a logical node once the node has chosen a role
        """
        self.unassigned_roles.remove(role_id)

    def remove_least_flexible_node(self):
        """
        Attempts to retrieve the next node with the least flexibility, if it exists.
        """
        try:
            return self.node_ids_ordered_by_flexibility.popleft()[1]
        except IndexError:
            return None

    def __nonzero__(self):
        """
        Example usage:

        if (token):
            # Failure: we still have roles!
        else:
            # Success: all roles assigned!
        """

        return len(self.unassigned_roles) > 0
