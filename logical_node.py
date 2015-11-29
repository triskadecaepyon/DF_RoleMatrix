from token import *

class LogicalNode:
    def __init__(self, node_id, child_node_ids, network, parameters):
        self.node_id = node_id
        self.child_node_ids = child_node_ids
        self.network = network
        self.parameters = parameters
        self.satisfiable_roles = set()
        self.assignment_flexibility = None
        self.assigned_role = None

    def begin_logical_assignment(self, role_criterias):
        """
        Kicks off the logical assignment operation by broadcasting an "Evaluate Roles" message,
        creating a token, and then sending that token off to the first least flexibile node.
        """
        node_ids_ordered_by_flexibility = self.evaluate_roles_broadcast(role_criterias)
        role_ids = range(len(role_criterias))

        token = Token(role_ids, node_ids_ordered_by_flexibility)

        least_flexible_node_id = token.remove_least_flexible_node()
        return self.network.send_token(self.node_id, least_flexible_node_id, token)

    def evaluate_roles_broadcast(self, role_criterias):
        """
        Used by the root node in the broadcast spanning tree to sort
        the received assignement flexibilities
        """
        node_ids_ordered_by_flexibility = sorted(self.receive_evaluate_roles_message(role_criterias))

        return node_ids_ordered_by_flexibility

    def receive_evaluate_roles_message(self, role_criterias):
        """
        Processes an "Evaluate Roles" message by first forwarding the message to child nodes.
        In the meantime, the current node evaluates itself against the role criterias.
        Finally, the aggregated results are returned to the parent node.
        """
        assignment_flexibilities = []

        for child_node_id in self.child_node_ids:
            result = self.network.send_evaluate_roles_message(self.node_id, child_node_id, role_criterias)
            assignment_flexibilities.extend(result)

        self.assignment_flexibility = self.evaluate_against(role_criterias)
        if self.assignment_flexibility > 0:
            assignment_flexibilities.append((self.assignment_flexibility, self.node_id))

        return assignment_flexibilities

    def evaluate_against(self, role_criterias):
        """
        Simply loops through each role criteria and evaluates it using the current
        nodes parameters
        """

        for (role_id, role_criteria) in enumerate(role_criterias):
            if role_criteria.evaluate_against(self.parameters):
                self.satisfiable_roles.add(role_id)

        assignment_flexibility = len(self.satisfiable_roles)
        return assignment_flexibility

    def receive_token(self, src_node_id, token):
        self.choose_role_if_available(token)
        return self.forward_token(token)

    def choose_role_if_available(self, token):
        """
        Determines assignable roles and chooses one if available
        """

        assignable_roles = token.determine_assignable_roles(self.satisfiable_roles)
        if assignable_roles:
            self.assigned_role = assignable_roles.pop()
            token.record_assigned_role(self.assigned_role)

    def forward_token(self, token):
        """
        Determines if the token should be forwarded to the next least flexible node, if one exists
        """

        least_flexible_node_id = token.remove_least_flexible_node()

        if least_flexible_node_id is None or not token:
            # We are successful if token is empty of any unassigned roles.
            # We have failed if the token still has roles to assign.
            # Return the token so the client can inspect which roles are still unassigned.
            return token
        else:
            return self.network.send_token(self.node_id, least_flexible_node_id, token)
