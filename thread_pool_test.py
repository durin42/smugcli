import thread_pool
import unittest
from six.moves import queue

class TestThreadPool(unittest.TestCase):

  def _producer_thread(self, results):
    for i in range(10):
      results.put(i)

  def _consumer_thread(self, results):
    for i in range(10):
      self.assertEqual(results.get(), i)

  def testContextManager(self):
    results = queue.Queue(maxsize=1)
    with thread_pool.ThreadPool(2) as pool:
      pool.add(self._producer_thread, results)
      pool.add(self._consumer_thread, results)

  def testJoin(self):
    results = queue.Queue(maxsize=1)
    pool = thread_pool.ThreadPool(2)
    pool.add(self._producer_thread, results)
    pool.add(self._consumer_thread, results)
    pool.join()
