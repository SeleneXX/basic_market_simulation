import socket


def reply(fields):
    # request_category|product_id|path|hop_count|seller_address(for reply message)
    # path = 'ip1-port1,ip2-port2,ip3-port3,ip4-port4...'
    path = fields[2].split(',')
    if len(path) == 1 and path[0] == '':
        return
    next_address, next_port = path.pop().split('-')
    fields[2] = ','.join(path)
    data = '|'.join(fields)
    print('send data:', data)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((next_address, int(next_port)))
    client.send(data.encode('utf-8'))
    client.close()


def lookup(peer, fields):
    # request_category|product_id|path|hop_count
    fields[3] = f'{int(fields[3]) - 1}'
    # path = 'ip1-port1,ip2-port2,ip3-port3,ip4-port4...'
    fields[2] = f'{fields[2]},{peer.address[0]}-{peer.address[1]}'
    data = '|'.join(fields)
    print('send data:', data)
    for next_address in peer.connected_address:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(next_address)
        client.send(data.encode('utf-8'))
        client.close()


class Seller(object):

    def __init__(self, address, connected_address, peer_id, product_id, num_items):
        # address = (IP, port)
        self.address = address
        self.connected_address = connected_address
        self.peer_id = peer_id
        self.product_id = product_id
        self.num_items = num_items
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(address)
        self.server.listen(5)

    def process(self):
        while True:
            conn, _ = self.server.accept()
            request = conn.recv(1024)
            data = request.decode('utf-8')
            # data: request_category|product_id|path|hop_count|(seller address)|(remaining_items)
            print('receive data:', data)
            fields = data.split('|')
            # 0: lookup request, 1: reply request ,2: buy request
            if fields[0] == '0':
                # match product
                if int(fields[1]) == self.product_id:
                    # change the request category
                    fields[0] = '1'
                    # append seller's address
                    fields.append(f'{self.address[0]}-{self.address[1]}')
                    # append seller's remaining amount of items
                    fields.append(self.num_items)
                    reply(fields)
                # not match, propagate
                elif int(fields[3]) > 1:
                    self.lookup(self, fields)
            elif fields[0] == '1':
                reply(fields)
            elif fields[0] == '2':
                # process buy request concurrently
                self.num_items -= 1
                pass
            conn.close()


def buy(fields):
    # request_category|product_id|path|hop_count|seller_address(for reply message)
    fields[0] = '2'
    seller_address, seller_port = fields[-1].split('-')
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((seller_address, int(seller_port)))

    pass


class Buyer(object):

    def __init__(self, address, connected_address, peer_id, request_items, hop_count):
        # address = (IP, port)
        self.address = address
        self.connected_address = connected_address
        self.peer_id = peer_id
        self.request_items = request_items
        self.hop_count = hop_count
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(address)
        self.server.listen(5)

    def process(self):
        # send all requests
        dic = self.init_lookup()
        # request_category|product_id|path|hop_count|seller_address(for reply message)
        while True:
            conn, _ = self.server.accept()
            request = conn.recv(1024)
            data = request.decode('utf-8')
            fields = data.split('|')
            if fields[0] == '0':
                if int(fields[3]) > 1:
                    lookup(self, fields)
            elif fields[0] == '1':
                if fields[2] != '':
                    reply(fields)
                else:
                    buy(fields)
        pass

    def init_lookup(self):
        # request_category|product_id|path|hop_count|seller_address(for reply message)
        dic = {}
        for product_id in self.request_items:
            # 0|product_id|address-port|hop_count
            if product_id in dic:
                dic[product_id] += 1
            else:
                dic[product_id] = 0
            request = f'0|{product_id}|{self.address[0]}-{self.address[1]}|{self.hop_count}'
            for next_address in self.connected_address:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(next_address)
                client.send(request.encode('utf-8'))
                client.close()
        return dic
