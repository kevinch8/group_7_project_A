import requests
import subprocess
import unittest
import json
import xml.etree.ElementTree as ET
from tests.helper_functions import elements_equal

class TestProjectsIdTasks(unittest.TestCase):

    def setUp(self):
        self.active_projects = []
        self.active_todos = []

    def tearDown(self):
        for id in self.active_projects:
            response = requests.delete("http://localhost:4567/projects/" + id)
        
        for id in self.active_todos:
            response = requests.delete("http://localhost:4567/todos/" + id)

    def test_delete_projects_id_tasks_id_json(self):
        project_data = {
            "title": "School Work",
            "completed": False,
            "active": False,
            "description": "Work on assignments."
        }
        # Create a new project
        response = requests.post('http://localhost:4567/projects', json = project_data, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 201)
        project_json = response.json()
        # Check if what was created matches what was provided
        self.assertIn("id", project_json)
        self.active_projects.append(project_json["id"])
        self.assertEqual(project_json["title"], project_data["title"])
        self.assertEqual(project_json["completed"], json.dumps(project_data["completed"]))
        self.assertEqual(project_json["active"], json.dumps(project_data["active"]))
        self.assertEqual(project_json["description"], project_data["description"])

        # Create relationship between new project and default todo 1
        todo_id = {
            "id": "1"
        }
        response = requests.post('http://localhost:4567/projects/' + project_json["id"] + '/tasks', json = todo_id, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 201)

        # Verify if relationship was properly applied
        response = requests.get('http://localhost:4567/projects/' + project_json["id"] + '/tasks', headers={'Accept': 'application/json'})
        todos_json = response.json()['todos'][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(todos_json['id'], todo_id['id'])
        self.assertIn(todo_id, todos_json['tasksof'])

        # Delete relationship between new project and todo 1
        response = requests.delete('http://localhost:4567/projects/' + project_json["id"] + '/tasks/1', headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)

        # Verify that relationship was deleted properly
        response = requests.get('http://localhost:4567/projects/' + project_json["id"] + '/tasks', headers={'Accept': 'application/json'})
        todos_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(todos_json['todos'], [])

    def test_delete_projects_id_tasks_id_xml(self):
        project_data = {
            "title": "School Work",
            "completed": False,
            "active": False,
            "description": "Work on assignments."
        }
        # Create a new project
        response = requests.post('http://localhost:4567/projects', json = project_data, headers={'Accept': 'application/xml'})
        self.assertEqual(response.status_code, 201)
        project_xml = ET.fromstring(response.content)
        self.active_projects.append(project_xml.find("./id").text)
        # Check if what was created matches what was provided
        self.assertEqual(project_xml.find("./title").text, project_data["title"])
        self.assertEqual(project_xml.find("./completed").text, str(project_data["completed"]).lower())
        self.assertEqual(project_xml.find("./active").text, str(project_data["active"]).lower())
        self.assertEqual(project_xml.find("./description").text, project_data["description"])

        response = requests.get('http://localhost:4567/projects/' + project_xml.find("./id").text, headers={'Accept': 'application/xml'})
        obtained_project = ET.fromstring(response.content)[0]
        # Check if created project matches what we have
        self.assertEqual(response.status_code, 200)
        self.assertTrue(elements_equal(project_xml, obtained_project))

        # Create relationship between new project and default todo 1
        todo_id = {
            "id": "1"
        }
        response = requests.post('http://localhost:4567/projects/' + project_xml.find("./id").text + '/tasks', json = todo_id, headers={'Accept': 'application/xml'})
        self.assertEqual(response.status_code, 201)

        # Verify if relationship was properly applied
        response = requests.get('http://localhost:4567/projects/' + project_xml.find("./id").text + '/tasks', headers={'Accept': 'application/xml'})
        todos_xml = ET.fromstring(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(todos_xml.find("./todo/id").text, todo_id['id'])
        self.assertIn(project_xml.find("./id").text, [id.text for id in todos_xml.findall("./todo/tasksof/id")])

        # Delete relationship between new project and todo 1
        response = requests.delete('http://localhost:4567/projects/' + project_xml.find("./id").text + '/tasks/1', headers={'Accept': 'application/xml'})
        self.assertEqual(response.status_code, 200)

        # Verify that relationship was deleted properly
        response = requests.get('http://localhost:4567/projects/' + project_xml.find("./id").text + '/tasks', headers={'Accept': 'application/xml'})
        todos_xml = ET.fromstring(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(todos_xml.find("./todos"))

    def test_delete_projects_id_tasks_id_invalid_id(self):
        # Delete relationship between default project 1 and an invalid todo id
        response = requests.delete('http://localhost:4567/projects/1/tasks/-1', headers={'Accept': 'application/json'})
        error_json = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(error_json['errorMessages'][0], "Could not find any instances with projects/1/tasks/-1")