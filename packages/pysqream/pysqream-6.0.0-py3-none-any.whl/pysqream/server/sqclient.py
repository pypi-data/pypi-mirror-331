import json
from threading import Lock
from struct import pack, unpack
from pysqream.globals import PROTOCOL_VERSION, SUPPORTED_PROTOCOLS, clean_sqream_errors, CAN_SUPPORT_PARAMETERS, DEFAULT_CHUNKSIZE
from pysqream.logger import printdbg, log_and_raise
from pysqream.ping import _start_ping_loop, _end_ping_loop, PingLoop
from pysqream.server.sqsocket import SQSocket


class SQClient:
    def __init__(self, socket: SQSocket):
        self.socket: SQSocket = socket
        self.ping_loop: PingLoop = _start_ping_loop(self, self.socket)

    def receive(self, byte_num, timeout=None):
        """
        Read a specific amount of bytes from a given socket
        """

        data = bytearray(byte_num)
        view = memoryview(data)
        total = 0

        if timeout:
            self.socket.s.settimeout(timeout)

        while view:
            # Get whatever the socket gives and put it inside the bytearray
            received = self.socket.s.recv_into(view)
            if received == 0:
                log_and_raise(ConnectionRefusedError, f'SQreamd connection interrupted - 0 returned by socket')
            view = view[received:]
            total += received

        if timeout:
            self.socket.s.settimeout(None)

        return data

    def get_response(self, is_text_msg=True):
        """
        Get answer JSON string from SQream after sending a relevant message
        """

        lock = Lock()

        # Getting 10-byte response header back
        with lock:
            header = self.receive(10)
        server_protocol = header[0]
        if server_protocol not in SUPPORTED_PROTOCOLS:
            log_and_raise(Exception,
                          f'Protocol mismatch, client version - {PROTOCOL_VERSION}, server version - {server_protocol}')
        # bytes_or_text =  header[1]
        message_len = unpack('q', header[2:10])[0]

        with lock:
            receive = self.receive(message_len).decode(
                'utf8') if is_text_msg else self.receive(message_len)

        return receive

    # Non socket aux. functionality
    def generate_message_header(self, data_length, is_text_msg=True, protocol_version=PROTOCOL_VERSION):
        """
        Generate SQream's 10 byte header prepended to any message
        """

        return pack('bb', protocol_version, 1 if is_text_msg else 2) + pack(
            'q', data_length)

    def validate_response(self, response, expected):

        if expected not in response:
            # Color first line of SQream error (before the haskell thingy starts) in Red
            response = '\033[31m' + (response.split('\\n')[0] if clean_sqream_errors else response) + '\033[0m'
            log_and_raise(Exception, f'\nexpected response {expected} but got:\n\n {response}')

    def send_string(self, json_cmd, get_response=True, is_text_msg=True, sock=None):
        """
        Encode a JSON string and send to SQream. Optionally get response
        """

        # Generating the message header, and sending both over the socket
        printdbg(f'string sent: {json_cmd}')
        self.socket.send(self.generate_message_header(len(json_cmd)) + json_cmd.encode('utf8'))

        if get_response:
            return self.get_response(is_text_msg)

    def get_statement_id(self):
        return json.loads(self.send_string('{"getStatementId" : "getStatementId"}'))["statementId"]

    def prepare_statement(self, statement: str):
        stmt_json = json.dumps({"prepareStatement": statement,
                                "chunkSize": DEFAULT_CHUNKSIZE,
                                "canSupportParams": CAN_SUPPORT_PARAMETERS})
        res = self.send_string(stmt_json)
        self.validate_response(res, "statementPrepared")

        return json.loads(res)

    def execute_statement(self):
        self.validate_response(self.send_string('{"execute" : "execute"}'), 'executed')

    def reconnect(self, statement_id: int, connection_id: int, database: str, service: str, username: str, password: str, listener_id: int, ip: str, port: int):
        self.socket.reconnect(ip=ip, port=port)
        # Send reconnect and reconstruct messages
        reconnect_str = (f'{{"service": "{service}", '
                         f'"reconnectDatabase":"{database}", '
                         f'"connectionId":{connection_id}, '
                         f'"listenerId":{listener_id}, '
                         f'"username":"{username}", '
                         f'"password":"{password}"}}')
        self.send_string(reconnect_str)
        # Since summer 2024 sqreamd worker could be configured with non-gpu (cpu) instance
        # it raises exception here like `The query requires a GPU-Worker. Ensure the SQream Service has GPU . . .`
        # This exception should be validated here. Otherwise, it will be validated at the next call which provides
        # Unexpected behavior
        self.validate_response(self.send_string(f'{{"reconstructStatement": {statement_id}}}'), "statementReconstructed")

    def get_query_type_in(self):
        """
        Sends queryType in message
        """

        return json.loads(self.send_string('{"queryTypeIn": "queryTypeIn"}')).get('queryType', [])

    def get_query_type_out(self):
        """
        Sends queryType out message
        """

        return json.loads(self.send_string('{"queryTypeOut" : "queryTypeOut"}')).get('queryTypeNamed', [])

    def put(self, capacity: int):
        self.send_string(f'{{"put":{capacity}}}', False)

    def send_data(self, capacity: int, packed_cols: [], byte_count: int):
        """
        Perform parameterized query - "put" json, header and binary packed columns.
        Note: Stop and start ping is must between sending message to the server, this is part of the protocol.
        """

        # Sending put message
        _end_ping_loop(self.ping_loop)
        self.send_string(f'{{"put":{capacity}}}', False)
        self.ping_loop = _start_ping_loop(self, self.socket)

        # Sending binary header message
        _end_ping_loop(self.ping_loop)
        self.socket.send((self.generate_message_header(byte_count, False)))
        self.ping_loop = _start_ping_loop(self, self.socket)

        # Sending packed data (binary buffer)
        _end_ping_loop(self.ping_loop)
        for packed_col in packed_cols:
            printdbg("Packed data sent:", packed_col)
            self.socket.send(packed_col)

        self.validate_response(self.get_response(), '{"putted":"putted"}')
        self.ping_loop = _start_ping_loop(self, self.socket)

    def fetch(self):
        res = self.send_string('{"fetch" : "fetch"}')
        self.validate_response(res, "colSzs")
        return json.loads(res)

    def connect_to_socket(self, username: str, password: str, database: str, service: str):
        res = self.send_string(f'{{"username":"{username}", "password":"{password}", "connectDatabase":"{database}", "service":"{service}"}}')
        res = json.loads(res)

        try:
            connection_id = res['connectionId']
            version = None

            if 'version' in res:
                version = res['version']

            return connection_id, version
        except KeyError:
            raise KeyError(f"Error connecting to database: {res['error']}")

    def close_statement(self):
        self.validate_response(self.send_string('{"closeStatement": "closeStatement"}'), '{"statementClosed":"statementClosed"}')

    def close_connection(self):
        self.validate_response(self.send_string('{"closeConnection": "closeConnection"}'), '{"connectionClosed":"connectionClosed"}')
        self.disconnect_socket()

    def disconnect_socket(self):
        self.socket.close()
        _end_ping_loop(self.ping_loop)
