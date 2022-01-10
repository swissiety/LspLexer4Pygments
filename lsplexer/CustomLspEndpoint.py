import threading

from pylspclient import LspEndpoint

#  /dev/null instead of print
def nowhere(self, **param):
    pass

class CustomLspEndpoint(LspEndpoint):
    def __init__(self, json_rpc_endpoint, default_callback=nowhere):
        super().__init__(json_rpc_endpoint, default_callback)

    def run(self):
        while not self.shutdown_flag:
            jsonrpc_message = self.json_rpc_endpoint.recv_response()

            if jsonrpc_message is None:
                print("server quit")
                self.stop();
                break

            #print("recieved message:", jsonrpc_message)
            if "result" in jsonrpc_message or "error" in jsonrpc_message:
                self.handle_result(jsonrpc_message)
            elif "method" in jsonrpc_message:
                if jsonrpc_message["method"] in self.callbacks:
                    self.callbacks[jsonrpc_message["method"]](jsonrpc_message)
                else:
                    self.default_callback(jsonrpc_message)
            else:
                print("unknown jsonrpc message")



    def stop(self):
        self.shutdown_flag = True
        # cleanup conditions that are waiting for a response
        for id in self.event_dict:
            self.response_dict[id] = None
            cond = self.event_dict[id]
            cond.acquire()
            cond.notify()
            cond.release()

        self.event_dict = {}


    def call_method(self, method_name, **kwargs):
        current_id = self.next_id
        self.next_id += 1
        cond = threading.Condition()
        self.event_dict[current_id] = cond
        cond.acquire()
        self.send_message(method_name, kwargs, current_id)
        cond.wait()
        cond.release()
        self.event_dict.pop(current_id)
        response = self.response_dict.pop(current_id)

        # error handling
        if response is None:
            raise Exception('Request aborted')

        if 'error' in response:
            raise Exception( 'Error Response: '+ response["error"]["message"])

        return response["result"]
