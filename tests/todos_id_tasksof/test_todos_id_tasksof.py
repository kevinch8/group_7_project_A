import requests
import subprocess
import unittest
from tests.todos_id_tasksof import const
import xml.etree.ElementTree as ET
from tests.helper_functions import elements_equal
import json

class TestTodosIdTasksof(unittest.TestCase):

    def setUp(self):
        self.active_todos = []
        self.active_projects = []

    def tearDown(self):
        for id in self.active_todos:
            response = requests.delete("http://localhost:4567/todos/" + id)
        
        for id in self.active_projects:
            response = requests.delete("http://localhost:4567/projects/" + id)

    def test_get_todos_id_tasksof_json(self):
        response = requests.get('http://localhost:4567/todos/1/tasksof', headers={'Accept': 'application/json'})
        project_1 = response.json()['projects'][0]
        project_1["tasks"].sort(key=lambda val: val["id"]) # Sort to keep data consistent
        # Check if the project associated with todos 1 is project 1
        self.assertEqual(project_1, const.PROJECT_DEFAULT_JSON_1)
        self.assertEqual(response.status_code, 200)

    def test_get_todos_id_tasksof_xml(self):
        response = requests.get('http://localhost:4567/todos/1/tasksof', headers={'Accept': 'application/xml'})
        project_1 = ET.fromstring(response.content).find("./project")
        # Check if the project associated with todos 1 is project with id=1 in XML
        self.assertEqual(project_1.find("./id").text, ET.fromstring(const.PROJECT_DEFAULT_XML_1).find("./project/id").text)
        self.assertEqual(response.status_code, 200)

    def test_get_todos_id_tasksof_invalid_id(self):
        # Undocumented behavior similar to one observed in categories
        # If an invalid id is provided no error is shown, instead it shows list of projects for all todos
        # In default case, since todo with id 1 & 2 are tasksof project 1. Project 1 will appear twice in the repsonse.
        response = requests.get('http://localhost:4567/todos/-1/tasksof', headers={'Accept': 'application/json'})
        projects = response.json()['projects']
        projects[0]["tasks"].sort(key=lambda val: val["id"]) # Sort to keep data consistent
        projects[1]["tasks"].sort(key=lambda val: val["id"])
        # Check if the list of projects are exactly 2 project of id 1.
        self.assertEqual(projects[0], const.PROJECT_DEFAULT_JSON_1)
        self.assertEqual(projects[1], const.PROJECT_DEFAULT_JSON_1)
        self.assertEqual(response.status_code, 200)

    @unittest.expectedFailure
    def test_get_todos_id_tasksof_invalid_id_expected_fail(self):
        # Expected fail should return error 404 not found because todo -1 does not exist
        response = requests.get('http://localhost:4567/todos/-1/tasksof', headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 404)
    
    def test_get_todos_id_tasksof_no_id(self):
        # Undocumented behavior similar to one observed in categories
        # If no id is provided, it shows list of projects for all todos
        # In default case, since todo with id 1 & 2 are tasksof project 1. Project 1 will appear twice in the repsonse.
        response = requests.get('http://localhost:4567/todos/tasksof', headers={'Accept': 'application/json'})
        projects = response.json()['projects']
        projects[0]["tasks"].sort(key=lambda val: val["id"]) # Sort to keep data consistent
        projects[1]["tasks"].sort(key=lambda val: val["id"])
        # Check if the list of projects are exactly 2 project of id 1.
        self.assertEqual(projects[0], const.PROJECT_DEFAULT_JSON_1)
        self.assertEqual(projects[1], const.PROJECT_DEFAULT_JSON_1)
        self.assertEqual(response.status_code, 200)

    def test_head_todos_id_tasksof_json(self):
        response = requests.head('http://localhost:4567/todos/1/tasksof', headers={'Accept': 'application/json'})
        # Check if Content-Type in header is application/json
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)

    def test_head_todos_id_tasksof_xml(self):
        response = requests.head('http://localhost:4567/todos/1/tasksof', headers={'Accept': 'application/xml'})
        # Check if Content-Type in header is application/json
        self.assertEqual(response.headers['Content-Type'], 'application/xml')
        self.assertEqual(response.status_code, 200)
    
    def test_head_todos_id_tasksof_invalid_id(self):
        response = requests.head('http://localhost:4567/todos/-1/tasksof', headers={'Accept': 'application/json'})
        # This is the actual behavior being tested
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)

    @unittest.expectedFailure
    def test_head_todos_id_tasksof_invalid_id_expected_fail(self):
        response = requests.head('http://localhost:4567/todos/-1/tasksof', headers={'Accept': 'application/json'})
        # This should be the expected response
        self.assertEqual(response.status_code, 404)

    def test_post_todos_id_tasksof_json(self):
        tasksof_todo = {
            "title": "Todo to be associated to project",
            "doneStatus": False,
            "description": ""
            }
        response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=tasksof_todo)
        actual_tasksof_todo = response.json()
        # Check if what was created matches the title we want
        self.assertEqual(tasksof_todo["title"], actual_tasksof_todo["title"])
        self.assertEqual(response.status_code, 201)
        self.active_todos.append(actual_tasksof_todo["id"])

        project_identity = {
            "id": "1"
        }
        response = requests.post('http://localhost:4567/todos/'+ actual_tasksof_todo["id"] + '/tasksof', headers={'Accept': 'application/json'}, json=project_identity)
        self.assertEqual(response.status_code, 201)

        response = requests.get('http://localhost:4567/todos/'+ actual_tasksof_todo["id"] + '/tasksof', headers={'Accept': 'application/json'})
        project1 = response.json()['projects'][0]
        self.assertEqual(project1['id'], project_identity['id'])
        self.assertEqual(response.status_code, 200)
    
    def test_post_todos_id_tasksof_xml(self):
        # Unexpected failing behavior
        tasksof_todo =  "<project><id>1</id></project>"
        response = requests.post('http://localhost:4567/todos/1/tasksof', headers={'Content-type': 'application/xml'}, data=tasksof_todo)
        error_msg = response.json()["errorMessages"][0]
        self.assertEqual(error_msg, "Could not find thing matching value for id")
        self.assertEqual(response.status_code, 404)

    @unittest.expectedFailure
    def test_post_todos_id_tasksof_xml_expected_fail(self):
        # Behavior should be a successful post
        tasksof_todo =  "<project><id>1</id></project>"
        response = requests.post('http://localhost:4567/todos/1/tasksof', headers={'Content-type': 'application/xml'}, data=tasksof_todo)
        self.assertEqual(response.status_code, 201)

    def test_post_todos_id_tasksof_with_title_json(self):
        # Testing unexpected behavior of new project being created 
        tasksof_todo = {
            "title": "Todo to be associated to project",
            "doneStatus": False,
            "description": ""
            }
        response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=tasksof_todo)
        actual_tasksof_todo = response.json()
        # Check if what was created matches the title we want
        self.assertEqual(tasksof_todo["title"], actual_tasksof_todo["title"])
        self.assertEqual(response.status_code, 201)
        self.active_todos.append(actual_tasksof_todo["id"])

        project_with_title = {
            "title": "new_project"
        }
        response = requests.post('http://localhost:4567/todos/'+ actual_tasksof_todo["id"] + '/tasksof', headers={'Accept': 'application/json'}, json=project_with_title)
        new_project = response.json()
        self.assertEqual(new_project['title'], project_with_title['title'])
        self.active_projects.append(new_project['id'])
        self.assertEqual(response.status_code, 201)

        response = requests.get('http://localhost:4567/todos/'+ actual_tasksof_todo["id"] + '/tasksof', headers={'Accept': 'application/json'})
        project1 = response.json()['projects'][0]
        self.assertEqual(project1['id'], new_project['id'])
        self.assertEqual(response.status_code, 200)

    def test_post_todos_id_tasksof_invalid_id_json(self):
        project_identity = {
            "id": "1"
        }
        response = requests.post('http://localhost:4567/todos/-1/tasksof', headers={'Accept': 'application/json'}, json=project_identity)
        error_msg = response.json()["errorMessages"][0]
        self.assertEqual(error_msg, "Could not find parent thing for relationship todos/-1/tasksof")
        self.assertEqual(response.status_code, 404)