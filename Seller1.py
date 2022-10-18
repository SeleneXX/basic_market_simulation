import peer
import multiprocessing
seller = peer.Seller(('10.0.0.133', 3000),[('10.0.0.133', 3002)], 1, 1, 2)

t1 = multiprocessing.Process(target=seller.process())

t1.start()
