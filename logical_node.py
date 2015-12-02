from logical_token import Token
import rpyc

FLEXIBILITY_ELEMENT = 0
PRIORITY_ELEMENT = 1
NODE_ID_ELEMENT = 2

class LogicalNode:
    def __init__(self, node_id, parameters, role_criterias, child_node_ids = []):
        self.node_id = node_id
        self.parameters = parameters
        self.role_criterias = role_criterias
        self.child_node_ids = child_node_ids
        self.satisfiable_roles = set()
        self.assigned_role = None
        self.network = None

    def set_network(self, network):
        self.network = network

    def begin_logical_assignment(self):
        """
        Kicks off the logical assignment operation by broadcasting an "Evaluate Roles" message,
        creating a token, and then sending that token off to the first least flexible node.
        """
        if self.child_node_ids:
            child_node_ids = self.child_node_ids
        else:
            child_node_ids = range(self.network.get_num_nodes())
            child_node_ids.remove(self.node_id)

        assignment_indexes = self.evaluate_roles_broadcast(child_node_ids)

        assignment_path = self.create_assigment_path(assignment_indexes)
        role_ids = range(len(self.role_criterias))

        token = Token(role_ids, assignment_path)

        next_node_id = token.next_node()
        return self.network.send_token(self.node_id, next_node_id, token)

    def create_assigment_path(self, assignment_indexes):
        return map(lambda assignment_index: assignment_index[NODE_ID_ELEMENT], sorted(assignment_indexes))

    def evaluate_roles_broadcast(self, child_node_ids):
        """
        Used by the root node in the broadcast spanning tree to sort
        the received assignment indexes
        """
        assignment_indexes = []

        async_results = []
        for child_node_id in child_node_ids:
            result = self.network.send_evaluate_roles_message(self.node_id, child_node_id)
            async_results.append(result)

        assignment_index = self.evaluate_roles()
        if assignment_index[FLEXIBILITY_ELEMENT] > 0:
            assignment_indexes.append(assignment_index)

        for result in async_results:
            result.wait()
            assignment_indexes.extend(result.value)

        return assignment_indexes

    def receive_evaluate_roles_message(self):
        """
        Processes an "Evaluate Roles" message by first forwarding the message to child nodes.
        In the meantime, the current node evaluates itself against the role criterias.
        Finally, the aggregated results are returned to the parent node.
        """
        return self.evaluate_roles_broadcast(self.child_node_ids)

    def evaluate_roles(self):
        """
        Simply loops through each role criteria and evaluates it using the current
        nodes parameters
        """

        self.overall_grade = 0

        for (role_id, role_criteria) in enumerate(self.role_criterias):
            grade = role_criteria.evaluate_against(self.parameters)
            if grade > 0:
                self.overall_grade += grade
                self.satisfiable_roles.add((role_id, grade))

        return self.compute_assignment_index(self.overall_grade)

    def compute_assignment_index(self, overall_grade):
        assignment_flexibility = len(self.satisfiable_roles)
        if assignment_flexibility > 0:
            assignment_priority = 1.0 / overall_grade
        else:
            assignment_priority = float('inf')

        return (assignment_flexibility, assignment_priority, self.node_id)

    def receive_token(self, src_node_id, token_attr_dict):
        token = Token.from_dict(token_attr_dict) # this is necessary because RPC serializes objects to raw dicts

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

            async_results = []
            for node_id in token.assignment_path:
                result = \
                    self.network.send_update_assignment_index_message(self.node_id, node_id, self.assigned_role)
                async_results.append(result)

            updated_assignment_indexes = []
            for result in async_results:
                result.wait()
                updated_assignment_index = result.value
                if updated_assignment_index[FLEXIBILITY_ELEMENT] > 0:
                    updated_assignment_indexes.append(updated_assignment_index)

            token.assignment_path = self.create_assigment_path(updated_assignment_indexes)

    def receive_update_assignment_index_message(self, assigned_role):
        found_role = None

        for satisfiable_role in self.satisfiable_roles:
            if satisfiable_role[0] == assigned_role:
                found_role = satisfiable_role
                break

        if found_role:
            self.satisfiable_roles.remove(found_role)
            self.overall_grade -= found_role[1]

        return self.compute_assignment_index(self.overall_grade)

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
