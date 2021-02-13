import requests
import subprocess
import unittest
import time
class TestTodos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.process = subprocess.Popen(['java', '-jar', 'runTodoManagerRestAPI-1.5.5.jar'])

    def test_1(self):

        request = requests.get('http://localhost:4567/todos')
        self.assertEqual(request.text, 2)

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
