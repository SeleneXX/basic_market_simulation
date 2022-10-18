import peer
import multiprocessing

buyer = peer.Buyer(('10.0.0.133', 3001),[('10.0.0.133', 3002)], '2', [1], 5)

t2 = multiprocessing.Process(target=buyer.process())

t2.start()