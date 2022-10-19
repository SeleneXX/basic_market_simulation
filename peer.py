import socket, time, random, datetime
import threading

sem = threading.Semaphore(20)
lock = threading.Lock()


def reply(fields):
    # request_category|product_id|path|hop_count|seller_address(for reply message)
    # path = 'ip1-port1,ip2-port2,ip3-port3,ip4-port4...'
    path = fields[2].split(',')
    if len(path) == 1 and path[0] == '':
        return
    next_address, next_port = path.pop().split('-')
    fields[2] = ','.join(path)
    data = '|'.join(fields)
    # print('send data:', data)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((next_address, int(next_port)))
    client.send(data.encode('utf-8'))
    client.close()


def lookup(peer, fields):
    # request_category|product_id|path|hop_count
    fields[3] = f'{int(fields[3]) - 1}'
    # path = 'ip1-port1,ip2-port2,ip3-port3,ip4-port4...'
    path = fields[2].split(',')
    last_addr = path[-1]
    fields[2] = f'{fields[2]},{peer.address[0]}-{peer.address[1]}'
    data = '|'.join(fields)
    for next_address in peer.connected_address:
        rand = random.randint(0,1)
        if f'{next_address[0]}-{next_address[1]}' == last_addr and rand == 0:
            continue

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(next_address)
        # print('send data:', data)
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
        self.origin_num = num_items
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(address)
        self.server.listen(1000)

    def process(self):
        print('Start Seller:', self.peer_id)
        while True:
            with sem:
                time.sleep(0.1)
                conn, _ = self.server.accept()
                request = conn.recv(1024)
                data = request.decode('utf-8')
                # data: request_category|product_id|path|hop_count|(seller address)|(remaining_items)|(peer_id)
                # print('receive data:', data)
                fields = data.split('|')
                # 0: lookup request, 1: reply request ,2: buy request
                if fields[0] == '0':
                    # conn.send('Next peer receiving!'.encode('utf-8'))
                    # match product
                    request_product = fields[1].split('-')
                    if int(request_product[0]) == self.product_id:
                        # change the request category
                        fields[0] = '1'
                        # append seller's address
                        fields.append(f'{self.address[0]}-{self.address[1]}')
                        fields.append(str(self.peer_id))
                        # append seller's remaining amount of items
                        # fields.append(self.num_items)
                        reply(fields)
                    # not match, propagate
                    elif int(fields[3]) > 1:
                        lookup(self, fields)
                elif fields[0] == '1':
                    reply(fields)
                elif fields[0] == '2':
                    # process buy request concurrently
                    lock.acquire()
                    product_id,_ = fields[1].split('-')
                    print("Product ID:", int(product_id), self.product_id)
                    if int(product_id) == self.product_id:
                        self.num_items -= 1
                        print(self.peer_id, '|| remains', self.num_items, 'items in stock.')
                        if self.num_items == 0:
                            self.num_items = self.origin_num
                            self.product_id = random.randint(0,2)
                            print(self.peer_id, "|| change the selling product ID", self.product_id)
                        conn.send('Successfully buying'.encode('utf-8'))
                    else:
                        conn.send('Failure.'.encode('utf-8'))
                    lock.release()
                conn.close()


def buy(fields):
    # request_category|product_id|path|hop_count|seller_address(for reply message)
    fields[0] = '2'
    seller_address, seller_port = fields[-2].split('-')
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((seller_address, int(seller_port)))
    data = '|'.join(fields)
    client.send(data.encode('utf-8'))
    status = client.recv(1024)
    status = status.decode('utf-8')
    client.close()
    return -1 if status == 'Failure.' else time.time()


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
        self.server.listen(1000)
        self.success = [0] * len(request_items)
        self.request_buffer = [''] * len(request_items)
        self.request_times = [-1] * len(self.request_items)
        self.reply_times = [-1] * len(self.request_items)

    def process(self):
        # send all requests
        print('Start Buyer:', self.peer_id)
        time.sleep(5)
        self.init_lookup()
        print(1)
        # request_category|product_id|path|hop_count|seller_address(for reply message)
        while True:
            with sem:
                time.sleep(0.1)
                conn, _ = self.server.accept()
                request = conn.recv(1024)
                data = request.decode('utf-8')
                fields = data.split('|')
                if fields[0] == '0':
                    # conn.send('Next peer receiving!'.encode('utf-8'))
                    if int(fields[3]) > 1:
                        lookup(self, fields)
                elif fields[0] == '1':
                    if fields[2] != '':
                        reply(fields)
                    else:
                        pro_id, index = fields[1].split('-')
                        index = int(index)
                        if not self.success[index]:
                            print(self.peer_id, '|| Find the buyer', fields[-1])
                            print(self.peer_id, '|| Now buying...')
                            self.reply_times[index] = buy(fields)
                            if self.reply_times[index] == -1:
                                print(self.peer_id, '|| Purchase failed. Try again.')
                                lock.acquire()
                                self.reply_times[index] = -1
                                self.request_times[index] = time.time()
                                for next_address in self.connected_address:
                                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    client.connect(next_address)
                                    client.send(self.request_buffer[index].encode('utf-8'))
                                    client.close()
                                lock.release()
                            else:
                                Output = open(f'output{self.peer_id}.txt', mode='a')
                                now = datetime.datetime.now()
                                Output.write(f'{now.strftime("%Y-%m-%d %H:%M:%S")}, {self.peer_id} purchase product{pro_id} from {fields[-1]}!\n')
                                Output.close()
                                self.success[index] = 1
                                # File = open(f'result{self.peer_id}.txt', mode='a')
                                # File.write(f'{index}\t{self.reply_times[index]-self.request_times[index]}\n')
                                # File.close()
                                print(self.peer_id, '|| Request time:', self.reply_times[index]-self.request_times[index])
                conn.close()

    def init_lookup(self):
        # request_category|product_id|path|hop_count|seller_address(for reply message)
        for i, product_id in enumerate(self.request_items):
            print("Seaching for:", product_id)
            # 0|product_id|address-port|hop_count
            request = f'0|{product_id}-{i}|{self.address[0]}-{self.address[1]}|{self.hop_count}'
            self.request_times[i] = time.time()
            for next_address in self.connected_address:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(next_address)
                client.send(request.encode('utf-8'))
                # receive = client.recv(1024)
                # receive = receive.decode('utf-8')
                # print(receive)
                client.close()
            self.request_buffer[i] = request
