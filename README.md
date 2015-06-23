# pyForJenkins
The py scripts for Jenkins CI processing.

Environment: Windows + Python 2.7(3.x cannot support Jenkins module ~April-2015)
-----------

Steps to use py to control Jenkins
----------------------------------

1.	Install py setuptools: https://pypi.python.org/pypi/setuptools#windows-simplified
	just download setuptools-15.2.zip (md5), and run ez_setup.py.
2. 	Add environment variable PATH to C:\Python27\Scripts.
3. 	Install Jenkins module by pip: https://python-jenkins.readthedocs.org/en/latest/install.html
4. 	Now the py module can be import by "import jenkins".
5. 	Refer to each py file for examples to manipulate Jenkins CI by py.

test.py
-------
The "Hello world" demo for jenkins module usage.

p4_job_cfg.py
-------------
The example to modify job configuration p4 scm parameters(p4User/p4Passwd/p4Port/projectPath) by cmd line.
run it at cmd: p4_job_cfg.py http://test-ci.eng.citrite.net:8080 bin 123 jobname biny p4password 401.citrite.net:1111 1

add_new_tool_job.py
-------------
Add a new series jobs example by job configuration template.

DB_BACKUP/Mongo
---------------
Mongo DB daily backup script for python 3.4.3.
> - setup.py. setup script for py2exe, cmd as 'py setup.py py2exe'
> - src/mongo_backup.py. mongo db backup script. cmd as 'python mongo_backup.py  1.1.1.1 8080 d:\mongo-db-backup -t 9:00'
> - src/test_mongo_backup.py. test script for mongo_backup.py.
