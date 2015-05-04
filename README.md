# pyForJenkins
The py scripts for Jenkins CI processing.

Environment: Windows + Python 2.7(3.x cannot support Jenkins module ~April-2015)
---------------------------------------------------

Steps to use py to control Jenkins
----------------------------------

1.	Install py setuptools: https://pypi.python.org/pypi/setuptools#windows-simplified
	just download setuptools-15.2.zip (md5), and run ez_setup.py.
2. 	Add environment variable PATH to C:\Python27\Scripts.
3. 	Install Jenkins module by pip: https://python-jenkins.readthedocs.org/en/latest/install.html
4. 	Now the py module can be import by "import jenkins".
5. 	Refer to each py file for examples to manipulate Jenkins CI by py.

