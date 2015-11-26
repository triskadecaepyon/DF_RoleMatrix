from abc import ABCMeta, abstractmethod
from collections import deque


class Token:

    def __init__(self, number_of_roles, node_ids_ordered_by_flexibility):
        self.number_of_roles = number_of_roles
        self.node_ids_ordered_by_flexibility = deque(node_ids_ordered_by_flexibility)
        self.assigned_roles = set()

    def determine_assignable_roles(self, satisfiable_roles):
        """
        Based on a node's satisfiable roles and the currently assigned
        roles, determine all assignable roles for that node
        """
        return satisfiable_roles.difference(self.assigned_roles)

    def record_assigned_role(self, role_id):
        self.assigned_roles.add(role_id)

    def remove_least_flexible_node(self):
        try:
            return self.node_ids_ordered_by_flexibility.popleft()
        except IndexError:
            return None

    def all_roles_assigned(self):
        return self.number_of_roles == len(self.assigned_roles)


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
        satisfying_nodes = \
            [logical_node for logical_node in self.logical_nodes if logical_node.evaluate_against(self.role_criterias)]

        node_ids_ordered_by_flexibility = \
            map(lambda node: node.node_id, sorted(satisfying_nodes, key=lambda node: node.assignment_flexibility))

        return node_ids_ordered_by_flexibility

    def send_token(self, src_node_id, dst_node_id, token):
        return self.logical_nodes[dst_node_id].receive_token(src_node_id, token)


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
    def __init__(self, node_id, network, parameters):
        self.node_id = node_id
        # @TODO: This field is necessary for keeping track of the network's spanning tree. It
        # will be used to compute the node assignment flexibilities using a network broadcast
        self.child_node_ids = None
        self.network = network
        self.parameters = parameters
        self.satisfiable_roles = set()
        self.assignment_flexibility = None
        self.assigned_role = None

    def evaluate_against(self, role_criterias):
        for (role_id, role_criteria) in enumerate(role_criterias):
            if role_criteria.evaluate_against(self.parameters):
                self.satisfiable_roles.add(role_id)

        self.assignment_flexibility = len(self.satisfiable_roles)
        return self.assignment_flexibility

    def begin_logical_assignment(self, token):
        least_flexible_node_id = token.remove_least_flexible_node()
        return network.send_token(-1, least_flexible_node_id, token)

    def receive_token(self, src_node_id, token):
        self.choose_role_if_available(token)
        return self.forward_token(token)

    def choose_role_if_available(self, token):
        assignable_roles = token.determine_assignable_roles(self.satisfiable_roles)
        if assignable_roles:
            self.assigned_role = assignable_roles.pop()
            token.record_assigned_role(self.assigned_role)

    def forward_token(self, token):
        if token.all_roles_assigned():
            # Success! We have satisfied all roles.
            return True

        least_flexible_node_id = token.remove_least_flexible_node()
        if least_flexible_node_id is not None:
            return self.network.send_token(self.node_id, least_flexible_node_id, token)
        else:
            # Failure! There are no more nodes, and we still have roles to assign
            # @TODO: determine how we should deal with/propagate the unassignability of roles.
            # I'm thinking we should return tuples that store rich information about
            # why we were unable to assign all roles. For example, all roles might not be
            # assignable because either a node can't be assigned any role, or
            # because there are no nodes left in the system to assign roles to.
            # There might be other reasons as well
            return False




##################################################################################
# Example code that roughly shows how the framework is to be used. Note: the
# relationship between the network and the logical nodes will likely change.
##################################################################################

if __name__ == '__main__':

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
    role_criteria_3 = MyAwesomeRoleCriteria("freaking excited", happy=True, excited=True)
    role_criterias = [role_criteria_1, role_criteria_2, role_criteria_3]

    network = SimulatedNetwork(role_criterias)

    node_1 = LogicalNode(0, network, parameters={ "happy": True, "excited": True })
    node_2 = LogicalNode(1, network, parameters={ "happy": True, "excited": True })
    node_3 = LogicalNode(2, network, parameters={ "happy": False, "excited": False })
    node_4 = LogicalNode(3, network, parameters={ "happy": True, "excited": False })
    nodes = [node_1, node_2, node_3, node_4]

    network.set_logical_nodes(nodes)

    node_ids_ordered_by_flexibility = network.evaluate_roles_broadcast()
    token = Token(len(role_criterias), node_ids_ordered_by_flexibility)

    assignment_result = node_1.begin_logical_assignment(token)

    if assignment_result:
        print "Success! All roles assigned!"
        for node in nodes:
            if node.assigned_role is not None:
                print "Node %d's role: %s" % (node.node_id, role_criterias[node.assigned_role].name)
    else:
        print "Error! Some role couldn't be satisfied"