from abc import ABCMeta, abstractmethod

class RoleCriteria:
    __metaclass__ = ABCMeta

    @abstractmethod
    def evaluate_against(self, node_parameters):
        """
        This method provides clients with the full flexibility to grade how well
        a role is satisfied by a node's parameters. A typical implementation
        would consist of iterating over each criterion in the role's criteria and
        computing a grade using the appropriate node parameter(s).

        This method should return a value indicating the overall grade. A non-zero value
        indicates the degree to which the node satisfies this role. A value of zero indicates
        that this node does not satisfy the role at all. The inverse of the grade will be used
        as part of the node's priority, which will be used to determine which node, among a set
        of nodes with the same flexibility, should choose a role first. The grade itself will be
        used by a node to choose the best role among the roles that it satisfies.

        Example:
        assume role criterias rc0, rc1, and rc2 are all available roles

        node_0 evaluates rc0, rc1, and rc2, resulting in the following grade vector g1 = [1, 4, 0]
        node_1 evaluates rc0, rc1, and rc2, resulting in the following grade vector g2 = [0, 4, 8]
        node_2 evalutess rc0, rc1, and rc2, resulting in the following grade vector g3 = [3, 0, 0]

        node_0 and node_1 both satisfy 2 roles, so they have the same assignment flexibility
        of 2. However, node_1 has a higher priority than node_0 because 1 / sum(g2) < 1 / sum(g1).
        Thus, node_1 gets first priority to choose a role that it satisfies from the set of
        available roles. node_1 ends up choosing rc2 (element 2 in g2) because it had the highest
        grade for node_1.
        """
        pass
