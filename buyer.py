import random
import socket
import time
import multiprocessing
class Buyer(object):
    def __init__(self, Host, Port, connected_port, product_ID):
        self.Host = Host
        self.Port = Port
        self.address = (self.Host, self.Port)
        self.connect = connected_port
        self.product_ID = str(product_ID)

        self.lookupList = []
        self.replyList = []
        self.availableList = []

        #self.sem = threading.Semaphore(len(self.connect))

        self.tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(self.address)
        self.tcpSerSock.bind(self.address)
        self.tcpSerSock.listen(5)

    def lookup(self):
        while True:
            print('lookup')
            time.sleep(2)
            if self.lookupList:
                data = self.lookupList.pop()
                forward, buyer, product_name, hopcount, path = data
                print('Look up for the seller:', buyer, product_name, hopcount)
                if int(hopcount) > 0:
                    hopcount = int(hopcount) - 1
                    path = path.split(',')
                    last_port = int(path[-1])
                    newpath = path.append(str(self.Port))
                    newpath = ','.join(newpath)
                    for i in self.connect:
                        if i != last_port:
                            new_socket = socket.socket()
                            new_socket.connect((self.Host, i))
                            new_data = '|'.join([forward, buyer, product_name, str(hopcount), newpath])
                            new_socket.send(new_data.encode('utf-8'))
                            new_socket.close()

    def reply(self):
        while True:
            print('reply')
            time.sleep(2)
            if self.replyList:
                data = self.replyList.pop()
                backward, seller_ID, path = data
                print('Find the seller, tracing back to:', seller_ID)
                if path:
                    path = path.split(',')
                    port = int(path.pop())
                    path = ','.join(path)
                    new_socket = socket.socket()
                    new_socket.connect((self.Host, port))
                    new_data = '|'.join([backward, seller_ID, path])
                    new_socket.send(new_data.encode('utf-8'))
                    new_socket.close()
                else:
                    print('Find a seller!')
                    self.availableList.append(seller_ID)

    def buy(self):
        while True:
            print('buy')
            time.sleep(5)
            if self.availableList:
                destiny = random.choice(self.availableList)
                new_socket = socket.socket()
                new_socket.connect((self.Host, int(destiny)))
                data = '|'.join([self.product_ID])
                new_socket.send(data.encode('utf-8'))
                reply = new_socket.recv(1024)
                print(reply.decode('utf-8'))
            else:
                print('Can not find the seller.')


    def server(self):
        while True:
            print('server')
            cli, _ = self.tcpSerSock.accept()
            data = cli.recv(4096)
            data = data.decode('utf-8')
            data = data.split('|')
            if data[0] == '1':
                print('Receive a looking up request.')
                self.lookupList.append(data)
            else:
                print('Receive a replying request.')
                self.replyList.append(data)


if __name__ == '__main__':
    buyer = Buyer('10.0.0.133', 8888, [3002, 3003], 0)
    t1 = multiprocessing.Process(target=buyer.server())
    t2 = multiprocessing.Process(target=buyer.lookup())
    t3 = multiprocessing.Process(target=buyer.reply())
    t1.start()
    t2.start()
    t3.start()







