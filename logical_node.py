from token import *

class LogicalNode:
    def __init__(self, node_id, child_node_ids, network, parameters):
        self.node_id = node_id
        self.child_node_ids = child_node_ids
        self.network = network
        self.parameters = parameters
        self.satisfiable_roles = set()
        self.assigned_role = None

    def begin_logical_assignment(self, role_criterias):
        """
        Kicks off the logical assignment operation by broadcasting an "Evaluate Roles" message,
        creating a token, and then sending that token off to the first least flexible node.
        """
        nodes_ids_ordered_by_assignment_index = self.evaluate_roles_broadcast(role_criterias)
        role_ids = range(len(role_criterias))

        token = Token(role_ids, nodes_ids_ordered_by_assignment_index)

        next_node_id = token.next_node()
        return self.network.send_token(self.node_id, next_node_id, token)

    def evaluate_roles_broadcast(self, role_criterias):
        """
        Used by the root node in the broadcast spanning tree to sort
        the received assignment indexes
        """
        nodes_ids_ordered_by_assignment_index = sorted(self.receive_evaluate_roles_message(role_criterias))

        return nodes_ids_ordered_by_assignment_index

    def receive_evaluate_roles_message(self, role_criterias):
        """
        Processes an "Evaluate Roles" message by first forwarding the message to child nodes.
        In the meantime, the current node evaluates itself against the role criterias.
        Finally, the aggregated results are returned to the parent node.
        """
        assignment_indexes = []

        for child_node_id in self.child_node_ids:
            result = self.network.send_evaluate_roles_message(self.node_id, child_node_id, role_criterias)
            assignment_indexes.extend(result)

        assignment_index = self.evaluate_against(role_criterias)
        if assignment_index:
            assignment_indexes.append(assignment_index)

        return assignment_indexes

    def evaluate_against(self, role_criterias):
        """
        Simply loops through each role criteria and evaluates it using the current
        nodes parameters
        """

        self.overall_grade = 0

        for (role_id, role_criteria) in enumerate(role_criterias):
            grade = role_criteria.evaluate_against(self.parameters)
            if grade > 0:
                self.overall_grade += grade
                self.satisfiable_roles.add((role_id, grade))

        return self.compute_assignment_index()


    def compute_assignment_index(self):
        assignment_flexibility = len(self.satisfiable_roles)
        if assignment_flexibility:
            assignment_priority = 1.0 / self.overall_grade
            return (assignment_flexibility, assignment_priority, self.node_id)
        else:
            return None

    def receive_token(self, src_node_id, token):
        self.choose_role_if_available(token)
        return self.forward_token(token)

    def choose_role_if_available(self, token):
        """
        Determines assignable roles and chooses one if available
        """
        assignable_roles = \
            token.determine_assignable_roles(set(map(lambda satisfiable_role: satisfiable_role[0], self.satisfiable_roles)))

        if assignable_roles:
            self.assigned_role = assignable_roles.pop()
            token.record_assigned_role(self.assigned_role)

            updated_assignment_indexes = []
            for assignment_index in token.assignment_indexes:
                updated_assignment_index = \
                    self.network.update_assignment_index(self.node_id, assignment_index[2], self.assigned_role)
                if updated_assignment_index:
                    updated_assignment_indexes.append(updated_assignment_index)

            token.assignment_indexes = deque(sorted(updated_assignment_indexes))

    def update_assignment_index(self, assigned_role):
        found_role = None

        for satisfiable_role in self.satisfiable_roles:
            if satisfiable_role[0] == assigned_role:
                found_role = satisfiable_role
                break


        if found_role:
            self.satisfiable_roles.remove(found_role)
            self.overall_grade -= found_role[1]

        return self.compute_assignment_index()

    def forward_token(self, token):
        """
        Determines if the token should be forwarded to the next least flexible node, if one exists
        """

        next_node_id = token.next_node()

        if next_node_id is None or not token:
            # We are successful if token is empty of any unassigned roles.
            # We have failed if the token still has roles to assign.
            # Return the token so the client can inspect which roles are still unassigned.
            return token
        else:
            return self.network.send_token(self.node_id, next_node_id, token)
