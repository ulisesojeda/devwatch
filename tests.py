import unittest
from threading import Thread
import os
import time

from devwatch.devwatch import main, handler


class TestArgs(unittest.TestCase):
    """Args tests"""

    def setUp(self):
        os.system('touch foo.txt')

    def modify_file(self):
        os.system('echo LINE >> ./foo.txt')

    def test_args(self):
        t1 = Thread(target=main, args=("", 'foo.txt', 'cat @ > boo.txt'))
        t1.start()

        time.sleep(1)

        t2 = Thread(target=self.modify_file, args=())
        t2.start()

        time.sleep(1)

        t3 = Thread(target=handler, args=(None, None))
        t3.start()

        with open('boo.txt', 'r') as f:
            self.assertEqual(f.read(), 'LINE\n')

    def tearDown(self):
        os.system('rm foo.txt boo.txt')
