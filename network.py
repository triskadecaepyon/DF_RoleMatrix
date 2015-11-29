from abc import ABCMeta, abstractmethod

class Network:
    __metaclass__ = ABCMeta

    @abstractmethod
    def send_evaluate_roles_message(self, src_node_id, dst_node_id, role_criterias):
        pass

    @abstractmethod
    def send_token(self, src_node, dst_node, token):
        pass

class SimulatedNetwork(Network):
    """
    Simplifies development. Should be swappable with a derived Network class that uses real connections
    """

    def __init__(self, role_criterias):
        self.role_criterias = role_criterias

    def set_logical_nodes(self, logical_nodes):
        self.logical_nodes = logical_nodes

    def send_evaluate_roles_message(self, src_node_id, dst_node_id, role_criterias):
        return self.logical_nodes[dst_node_id].receive_evaluate_roles_message(role_criterias)

    def send_token(self, src_node_id, dst_node_id, token):
        return self.logical_nodes[dst_node_id].receive_token(src_node_id, token)
