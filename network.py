import rpyc
from rpyc.utils.server import ThreadedServer
import socket
import threading
import sys

class Network:

    def __init__(self):
        self.bytes_sent = 0

    def get_num_nodes(self):
        return len(self.logical_nodes)

    def send_evaluate_roles_message(self, src_node_id, dst_node_id):
        async_send_evaluate_roles_message = \
            self.async(self.logical_nodes[dst_node_id].receive_evaluate_roles_message)
        return async_send_evaluate_roles_message()

    def send_token(self, src_node_id, dst_node_id, token):
        self.bytes_sent += sys.getsizeof(token)

        return self.logical_nodes[dst_node_id].receive_token(src_node_id, token)

    def send_update_assignment_index_message(self, src_node_id, dst_node_id, assigned_role):
        self.bytes_sent += sys.getsizeof(assigned_role)
        async_send_update_assignment_index_message = \
            self.async(self.logical_nodes[dst_node_id].receive_update_assignment_index_message)

        return async_send_update_assignment_index_message(assigned_role)

    def start_server(self):
        self.server.start()

    def stop_server(self):
        self.server.close()

    def get_bytes_sent(self):
        return self.bytes_sent

def create_logical_node_service(logical_node):

    class LogicalNodeService(rpyc.Service):

        def exposed_begin_logical_assignment(self):
            return logical_node.begin_logical_assignment()

        def exposed_receive_evaluate_roles_message(self):
            return logical_node.receive_evaluate_roles_message()

        def exposed_receive_token(self, src_node_id, token):
            return logical_node.receive_token(src_node_id, token)

        def exposed_receive_update_assignment_index_message(self, assigned_role):
            return logical_node.receive_update_assignment_index_message(assigned_role)

        # override rpyc's security
        def _rpyc_getattr(self, name):
            return getattr(logical_node, name)

    return LogicalNodeService


class LiveNetwork(Network):

    class Client:

        def __init__(self, node_ip_address):
            self.conn = None
            self.node_ip_address = node_ip_address

        def __getattr__(self, name):
            if not self.conn:
                self.conn = rpyc.connect(self.node_ip_address[0], self.node_ip_address[1], config = {"allow_all_attrs": True})
            return self.conn.root.__getattr__(name)

    def __init__(self, server_node, node_ip_addresses):
        Network.__init__(self)

        self.async = rpyc.async
        self.logical_nodes = []
        for (node_id, node_ip_address) in enumerate(node_ip_addresses):
            if node_id != server_node.node_id:
                self.logical_nodes.append(LiveNetwork.Client(node_ip_address))
            else:
                server_node.set_network(self)
                self.logical_nodes.append(server_node)
                logical_node_service = create_logical_node_service(server_node)
                self.server = ThreadedServer(
                    logical_node_service,
                    hostname=node_ip_addresses[server_node.node_id][0],
                    port=node_ip_addresses[server_node.node_id][1],
                    protocol_config={"allow_all_attrs": True})

class SimulatedNetwork(Network):
    """
    Simplifies development. Should be swappable with a derived Network class that uses real connections
    """


    class Future:
        """
        Simulates the rpyc async interface
        Heavily adapted from http://code.activestate.com/recipes/84317-easy-threading-with-futures/
        """

        def __init__(self, func):
            self.func = func
            self._reset()
            self.still_computing = threading.Condition()   # Notify on this Condition when result is ready

        def _reset(self):
            self.done = False
            self.value = None
            self.exception = None

        def __call__(self, *args):
            self._reset()
            computation = threading.Thread(target=self._compute, args=args)
            computation.start()
            return self

        def wait(self):
            self.still_computing.acquire()
            while not self.done:
                self.still_computing.wait()
            self.still_computing.release()

        def _compute(self, *arg, **kwargs):
            self.still_computing.acquire()
            try:
                self.value = self.func(*arg, **kwargs)
            except Exception as e:
                self.exception = e
            self.done = True
            self.still_computing.notify()
            self.still_computing.release()

    def __init__(self, logical_nodes):
        Network.__init__(self)

        self.async = SimulatedNetwork.Future
        self.logical_nodes = logical_nodes
        for logical_node in logical_nodes:
            logical_node.set_network(self)
