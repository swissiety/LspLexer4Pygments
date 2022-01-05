import threading

from pylspclient import LspEndpoint


class CustomLspEndpoint(LspEndpoint):

    def stop(self):
        super().stop()
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
        self.event_dict.pop(current_id)
        cond.release()

        response = self.response_dict.pop(current_id)

        # error handling
        if response is None:
            raise Exception('Request aborted')

        if 'error' in response:
            raise Exception( 'Error Response: '+ response["error"]["message"])

        return response["result"]
