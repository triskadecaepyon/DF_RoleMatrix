from abc import ABCMeta, abstractmethod

class RoleCriteria:
    __metaclass__ = ABCMeta

    @abstractmethod
    def evaluate_against(self, node_parameters):
        """
        This method provides clients with the full flexibility to determinine whether
        a role is satisfiable by a node's parameters. A typical implementation
        would consist of iterating over each criterion in the role's criteria and
        computing a boolean value using the appropriate parameter(s). If all criterion
        compute to True, then the role is satisfiable by the node.

        This method should return True if the node_parameters satisfy the role's criteria.
        Returns False otherwise.
        """
        pass
