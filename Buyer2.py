import peer
import multiprocessing

buyer = peer.Buyer(('10.0.0.133', 3002),[('10.0.0.133', 3000), ('10.0.0.133', 3001)], '2', [1], 5)

t3 = multiprocessing.Process(target=buyer.process())

t3.start()