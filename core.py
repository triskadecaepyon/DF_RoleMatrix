from abc import ABCMeta


class Token:

    def __init__(self, role_assigment_flexibilities):
        self.role_assigment_flexibilities = role_assigment_flexibilities
        self.assigned_roles = [False] * len(satisfiable_roles)

    def determine_assignable_roles(self, satisfiable_roles):
        """
        Based on a node's satisfiable roles and the currently assigned
        roles, determine all assignable roles for that node
        """
        return [satisfiable_role and not assigned_role
                for (satisfiable_role, assigned_role) in zip(satisfiable_roles, self.assigned_roles)]

    def mark_role_assigned_to_node(self, role_id, node_id):
        self.assigned_roles[role_id] = True
        self.role_assigment_flexibilities[node_id] = None

    def determine_next_most_flexibile_node(self):
        for (node_id, role_assignment_flexibility) in enumerate(self.role_assigment_flexibilities):
            if role_assignment_flexibility is not None:
                return node_id
        return None

    def all_roles_assigned(self):
        return all(self.assigned_roles)


class Network:
    """
    This class is intended to define the interface to the Network. Initially,
    we will use a SimulatedNetwork in order to simplify development of the algorithm.
    However, once the algorithm works, we should be able to swap out the SimulatedNetwork for a
    real network class and hopefully get a distributed implementation for (almost) free.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def evaluate_roles_broadcast(self):
        pass

    @abstractmethod
    def send_token(self, src_node, dst_node, token):
        pass

class SimulatedNetwork(Network):

    def __init__(self, role_criterias):
        self.role_criterias = role_criterias

    def set_logical_nodes(self, logical_nodes):
        self.logical_nodes = logical_nodes

    def evaluate_roles_broadcast(self):
        role_assignment_flexibilities = \
            [logical_node.evaluate_against(self.role_criterias) for logical_node in self.logical_nodes]

        return role_assignment_flexibilities

    def send_token(self, src_node_id, dst_node_id, token):
        self.logical_nodes[dst_node_id].receive_token(src_node_id, token)


class RoleCriteria:
    __metaclass__ = ABCMeta

    @abstractmethod
    def evaluate_against(self, node_parameters):
        """
        This method provides clients with full flexibility for determinining whether
        a role is satisfiable given a node's parameters. A typical implementation
        would consist of iterating over each criterion in the role's criteria and
        computing a boolean value using the appropriate parameter(s). If all criterion
        compute to True, then the role is satisfiable by the node
        """
        pass


class LogicalNode:
    def __init__(self, node_id, child_node_ids, network, parameters):
        self.node_id = node_id
        self.child_node_ids = child_node_ids
        self.network = network
        self.parameters = parameters
        self.satisfiable_roles = []
        self.assignment_flexibility = None
        self.assigned_role = None

    def evaluate_against(self, role_criterias):
        for role_criteria in role_criterias:
            self.satisfiable_roles.append(role_criteria.evaluate_against(parameters))

        self.assignment_flexibility = sum(self.satisfiable_roles)
        return self.assignment_flexibility

    def receive_token(self, token):
        if self.choose_role(token):
            # @TODO: determine how we should deal with/propagate the unassignability of roles.
            # I'm thinking we should return tuples that store rich information about
            # why we were unable to assign all roles. For example, all roles might not be
            # assignable because either a node can't be assigned any role, or
            # because there are no nodes left in the system to assign roles to.
            # There might be other reasons as well
            return False
        else:
            return self.forward_token(token)

    def choose_role(self, token):
        assignable_roles = token.determine_assignable_roles(self.satisfiable_roles)

        for (assignable_role_id, assignable_role) in enumerate(assignable_roles):
            if assignable_role:
                token.mark_role_assigned_to_node(assignable_role_id, self.node_id)
                self.assigned_role = assignable_role
                return True

        # No assignable roles!
        return False

    def forward_token(self, token):
        if token.all_roles_assigned():
            # Success! We have satisfied all roles.
            return True

        next_most_flexible_node_id = token.determine_next_most_flexibile_node()
        if next_most_flexible_node_id is not None:
            return self.network.send_token(next_most_flexible_node_id, token)
        else:
            # Failure! There are no more nodes, and we still have roles to assign
            return False




##################################################################################
# Example code that roughly shows how the framework is to be used. Note: the
# relationship between the network and the logical nodes will likely change.
##################################################################################

if __name__ == "__main__":

# Clients will define their own RoleCriteria, which will expect
# a certain set of parameters to evaluate on
class MyAwesomeRoleCriteria(RoleCriteria):
    def __init__(self, name, happy, excited):
        self.name = name
        self.happy = happy
        self.excited = excited

    def evaluate_against(self, node_parameters):
        return self.happy == node_parameters["happy"] and self.excited == node_parameters["excited"]


role_criteria_1 = MyAwesomeRoleCriteria("very sad", happy=False, excited=False)
role_criteria_2 = MyAwesomeRoleCriteria("just content", happy=True, excited=False)
role_criteria_3 = MyAwesomeRoleCriteria("freaking excited", happy=False, excited=False)

role_criterias = [role_criteria_1, role_criteria_2, role_criteria_3]

network = SimulatedNetwork(role_criterias)

my_first_node = LogicalNode(0, [1, 2], network, parameters={ "happy": True, "excited": True })
my_second_node = LogicalNode(1, None, network, parameters={ "happy": True, "excited": False })
my_third_node = LogicalNode(2, None, network, parameters={ "happy": False, "excited": False })

network.set_logical_nodes([my_first_node, my_second_node, my_third_node])

role_assignment_flexibilities = network.evaluate_roles_broadcast()
token = Token(role_assigment_flexibilities)

assignment_result = my_first_node.receive_token(token)
if assignment_result:
    print "Success! All roles assigned!"
    print "my_first_node's role: %s" % role_criterias[my_first_node.assigned_role].name
    print "my_second_node's role: %s" % role_criterias[my_second_node.assigned_role].name
    print "my_third_node's role: %s" % role_criterias[my_third_node.assigned_role].name
else:
    print "Error! Some role couldn't be satisfied"