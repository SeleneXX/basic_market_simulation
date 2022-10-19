import peer

def run():
    # (address, connected_address, peer_id, product_id, num_items)
    seller = peer.Seller(('127.0.0.1', 3002),[('127.0.0.1', 3001), ('127.0.0.1', 3003)], 6, 1, 150)
    seller.process()

if __name__ == '__main__':
    run()