from role_criteria import *
from logical_node import *
from network import *
import rpyc
import threading
import time
import csv

class MockRoleCriteria(RoleCriteria):
    def __init__(self, name, node_grade_map):
        self.name = name
        self.node_grade_map = node_grade_map

    def evaluate_against(self, node_parameters):
        return self.node_grade_map[node_parameters["node_id"]]

def run_metrics(nodes, role_criterias, scenario, output):
    network = SimulatedNetwork(nodes)

    start_time = time.clock()
    token = nodes[0].begin_logical_assignment()
    elapsed_time = time.clock() - start_time

    if token:
        print "Error! Some roles couldn't be satisfied"
        for role_id in token.unassigned_roles:
            print "Role %d: %s" % (role_id, role_criterias[role_id].name)
    else:
        print "Success! All roles assigned!"
        #for node in nodes:
        #    if node.assigned_role is not None:
        #        print "Node %d's role: %s" % (node.node_id, role_criterias[node.assigned_role].name)

    print
    print "Metrics:"
    print
    print "Nodes: %d" % len(nodes)
    print "Role criterias: %d" % len(role_criterias)
    print "Scenario: %s" % scenario
    print "Elapsed time: %f" % elapsed_time
    print "Bytes transferred: %d" % network.get_bytes_sent()

    output.writerow(
        {
            "num_nodes_and_roles": len(nodes),
            "scenario": scenario,
            "elapsed_time": elapsed_time,
            "bytes_transferred": network.get_bytes_sent()
        })


with open('metrics_smart.csv', 'wb') as output_csv:
    fieldnames = ["num_nodes_and_roles", "scenario", "elapsed_time", "bytes_transferred"]
    output = csv.DictWriter(output_csv, fieldnames=fieldnames)
    output.writeheader()

    for num_nodes in range(1, 15):
        role_criterias = \
            [MockRoleCriteria("role_%d" % i, dict(zip(range(num_nodes), [1 if (num_nodes - j) > i else 0 for j in range(num_nodes)])))
                for i in range(num_nodes)]

        nodes = [LogicalNode(i, { "node_id": i }, role_criterias) for i in range(num_nodes)]
        run_metrics(nodes, role_criterias, "worst_case", output)

    for num_nodes in range(10, 101, 10):
        role_criterias = \
            [MockRoleCriteria("role_%d" % i, dict(zip(range(num_nodes), [1 if j == i else 0 for j in range(num_nodes)])))
                for i in range(num_nodes)]

        nodes = [LogicalNode(i, { "node_id": i }, role_criterias) for i in range(num_nodes)]
        run_metrics(nodes, role_criterias, "best_case", output)

