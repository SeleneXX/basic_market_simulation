import peer

def run():
    buyer = peer.Buyer(('10.0.0.133', 3001),[('10.0.0.133', 3002)], '2', [1], 5)
    buyer.process()

if __name__ == '__main__':
    run()
