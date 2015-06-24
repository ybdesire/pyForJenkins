#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
import subprocess

class TestMongoBackup(unittest.TestCase):
    def test_default_cmd(self):
        time_now = datetime.now().strftime('%H:%M')#24 hours format
        cmd_temp = 'python mysql_backup.py 3306 127.0.0.1 root 123 db1 c:\mysql-backup -t {0} -m test'.format(time_now)
        cmd_expect = 'mysqldump -P3306 -uroot -p123 db1 > {0}'.format(''.join(['c:\mysql-backup', '_', datetime.now().strftime('%Y-%m-%d_%H-%M'), '\\', 'db1.sql']))
        cmd_out_buffer = subprocess.check_output(cmd_temp).decode('utf-8')
        cmd_out = cmd_out_buffer.split('TEST_CMD')[1].split('\n')[0].strip()
        self.assertEqual(cmd_expect, cmd_out)
        

if __name__ == '__main__':
    unittest.main()
    