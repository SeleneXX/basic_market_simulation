import peer
from RandomList import random_list



def run():
    # (address, connected_address, peer_id, request_items, hop_count)
    item_list = random_list(15, 0, 2)
    buyer = peer.Buyer(('127.0.0.1', 3005),[('127.0.0.1', 3000), ('127.0.0.1', 3004)], 4, item_list, 5)
    buyer.process()

if __name__ == '__main__':
    run()