import requests
import subprocess
import unittest
from tests.todos import const
import xml.etree.ElementTree as ET
from tests.helper_functions import elements_equal
import json

class TestTodos(unittest.TestCase):

    def setUp(self):
        self.active_todos = []

    def tearDown(self):
        for id in self.active_todos:
            response = requests.delete("http://localhost:4567/todos/" + id)

    def test_get_todos_json(self):
        response = requests.get('http://localhost:4567/todos', headers={'Accept': 'application/json'})
        actual_todos_json = response.json()
        # Compare actual json from expected json
        self.assertEqual(actual_todos_json, const.TODOS_DEFAULT_JSON)
        self.assertEqual(response.status_code, 200)

    def test_get_todos_xml(self):
        response = requests.get('http://localhost:4567/todos', headers={'Accept': 'application/xml'})
        actual_todos_xml = ET.fromstring(response.content)
        # Compare actual xml from expected xml
        expected_todos_xml = ET.fromstring(const.TODOS_DEFAULT_XML)
        self.assertTrue(elements_equal(actual_todos_xml, expected_todos_xml))
        self.assertEqual(response.status_code, 200)

    def test_head_todos_json(self):
        response = requests.head('http://localhost:4567/todos', headers={'Accept': 'application/json'})
        # Check if Content-Type in header is application/json
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)

    def test_head_todos_xml(self):
        response = requests.head('http://localhost:4567/todos', headers={'Accept': 'application/xml'})
        # Check if Content-Type in header is application/xml
        self.assertEqual(response.headers['Content-Type'], 'application/xml')
        self.assertEqual(response.status_code, 200)

    def test_post_todos_json(self):
        sample_todo = {
            "title": "Test Todo",
            "doneStatus": False,
            "description": ""
            }
        response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=sample_todo)
        actual_sample_todo = response.json()
        # Check if what was created matches the title we want
        self.assertEqual(sample_todo["title"], actual_sample_todo["title"])
        self.assertEqual(response.status_code, 201)
        self.active_todos.append(actual_sample_todo["id"])

        response = requests.get('http://localhost:4567/todos/' + actual_sample_todo['id'], headers={'Accept': 'application/json'})
        obtained_todo = response.json()['todos'][0]
        # Check if created todo matches what we have
        self.assertEqual(actual_sample_todo, obtained_todo)
        self.assertEqual(response.status_code, 200)

    def test_post_todos_xml(self):
        sample_todo = {
            "title": "Test Todo",
            "doneStatus": False,
            "description": ""
            }
        response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/xml'}, json=sample_todo)
        actual_sample_todo = ET.fromstring(response.content)
        # Check if what was created matches the title we want
        self.assertEqual(sample_todo["title"], actual_sample_todo.find("./title").text)
        self.assertEqual(response.status_code, 201)
        self.active_todos.append(actual_sample_todo.find("./id").text)

        response = requests.get('http://localhost:4567/todos/' + actual_sample_todo.find("./id").text, headers={'Accept': 'application/xml'})
        obtained_todo = ET.fromstring(response.content)[0]
        # Check if created todo matches what we have
        self.assertTrue(elements_equal(actual_sample_todo, obtained_todo))
        self.assertEqual(response.status_code, 200)

    def test_post_todos_json_id_gap(self):
        # Following test shows bug -> empty body when creating todos lead to GAPS in ID increments.
        # Begin by creating a marker todo (to determine initial ID)
        sample_todo = {
            "title": "Test Todo",
            "doneStatus": False,
            "description": ""
            }
        response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=sample_todo)
        initial_sample_todo = response.json()
        self.assertEqual(response.status_code, 201)
        initial_id = int(initial_sample_todo["id"])
        self.active_todos.append(initial_sample_todo["id"])

        for i in range(4): # Run loop 4 times to observe ID gap of 5
            response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()["errorMessages"][0], "title : field is mandatory")
        
        # Create identical todo to obtain a new id
        response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=sample_todo)
        final_sample_todo = response.json()
        self.assertEqual(response.status_code, 201)
        final_id = int(final_sample_todo["id"])
        self.active_todos.append(final_sample_todo["id"])

        # Check if the next id created is incremented by 5
        self.assertEqual(final_id-initial_id, 5)

    def test_post_todos_malformed_json(self):
        malformed_todo = {
            "fake_attribute": "fake_value"
            }
        response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=malformed_todo)
        self.assertEqual(response.status_code, 400)
        error_msg = response.json()["errorMessages"][0]
        self.assertEqual(error_msg, "Could not find field: fake_attribute")

    def test_post_todo_malformed_xml(self):
        malformed_todo = "<todo><fakeField>fake text</fakeField></todo>"
        response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/xml', 'Content-Type': 'application/xml'}, data=malformed_todo)
        self.assertEqual(response.status_code, 400)
        error_msg = ET.fromstring(response.content).find("./errorMessage").text
        self.assertEqual(error_msg, "Could not find field: fakeField")

    

        

