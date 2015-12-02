class Token:

    def __init__(self, role_ids, assignment_path):
        self.unassigned_roles = role_ids
        self.assignment_path = assignment_path

    @staticmethod
    def from_dict(attr_dict):
        return Token(attr_dict["unassigned_roles"], attr_dict["assignment_path"])

    def determine_assignable_roles(self, satisfiable_roles):
        """
        Based on a node's satisfiable roles and the currently unassigned
        roles, determine all assignable roles for that node
        """
        return satisfiable_roles.intersection(set(self.unassigned_roles))

    def record_assigned_role(self, role_id):
        """
        Called by a logical node once the node has chosen a role
        """
        self.unassigned_roles.remove(role_id)

    def next_node(self):
        """
        Attempts to retrieve the next node with the smallest assignment index, if it exists.
        """
        try:
            return self.assignment_path.pop(0)
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

    def __getitem__(self, item):
        return self.__dict__[item]
