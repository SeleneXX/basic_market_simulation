import peer
from RandomList import random_list



def run():
    # (address, connected_address, peer_id, product_id, num_items)
    seller = peer.Seller(('127.0.0.1', 3004),[('127.0.0.1', 3003), ('127.0.0.1', 3005)], 5, 2, 150)
    seller.process()

if __name__ == '__main__':
    run()