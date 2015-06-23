#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
import subprocess

class TestMongoBackup(unittest.TestCase):
    timeNow = datetime.now().strftime('%H:%M')#24 hours format
    cmdTemp = 'python mongo_backup.py  1.1.1.1 8080 d:\mongo-db-backup -t {0} -m test'.format(timeNow)
    cmdExpect = 'mongodump --host 1.1.1.1 --port 8080 --out {0}'.format(''.join(['d:\mongo-db-backup', '_', datetime.now().strftime('%Y-%m-%d_%H-%M')]))
    cmdOutBuffer = subprocess.check_output(cmdTemp).decode('utf-8')
    cmdOut = cmdOutBuffer.split('TEST_CMD')[1].split('\n')[0].strip()
    
    def test_default_cmd(self):
        self.assertEqual(self.cmdExpect, self.cmdOut)

if __name__ == '__main__':
    unittest.main()
    