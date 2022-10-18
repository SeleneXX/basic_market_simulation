import peer

def run():
    seller = peer.Seller(('10.0.0.133', 3000),[('10.0.0.133', 3002)], 1, 1, 2)
    seller.process()

if __name__ == '__main__':
    run()






