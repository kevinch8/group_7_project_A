import requests
import subprocess
import unittest
import json
from tests.projects_id_tasks import const
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

    def test_get_projects_id_tasks_json(self):
        response = requests.get('http://localhost:4567/projects/1/tasks', headers={'Accept': 'application/json'})
        todos_json = response.json()
        # Compare response with expected json
        self.assertEqual(response.status_code, 200)
        self.assertIn(todos_json, [const.TODOS_DEFAULT_JSON_V1, const.TODOS_DEFAULT_JSON_V2])

    def test_get_projects_id_tasks_xml(self):
        response = requests.get('http://localhost:4567/projects/1/tasks', headers={'Accept': 'application/xml'})
        todos_xml = ET.fromstring(response.content)
        expected_todos_xml_v1 = ET.fromstring(const.TODOS_DEFAULT_XML_V1)
        expected_todos_xml_v2 = ET.fromstring(const.TODOS_DEFAULT_XML_V2)
        # Compare response with expected xml
        self.assertEqual(response.status_code, 200)
        self.assertTrue(elements_equal(todos_xml, expected_todos_xml_v1) or elements_equal(todos_xml, expected_todos_xml_v2))

    @unittest.expectedFailure
    def test_get_projects_id_tasks_invalid_id_bug(self):
        # ERROR: Requesting the tasks of an inexistant project will return the tasks of project 1 instead of an error
        response = requests.get('http://localhost:4567/projects/-1/tasks', headers={'Accept': 'application/json'})
        # Verify status code
        self.assertEqual(response.status_code, 404)

    def test_head_projects_id_tasks_json(self):
        response = requests.head('http://localhost:4567/projects/1/tasks', headers={'Accept': 'application/json'})
        # Check if Content-Type in header is application/json
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)

    def test_head_projects_id_tasks_xml(self):
        response = requests.head('http://localhost:4567/projects/1/tasks', headers={'Accept': 'application/xml'})
        # Check if Content-Type in header is application/json
        self.assertEqual(response.headers['Content-Type'], 'application/xml')
        self.assertEqual(response.status_code, 200)

    @unittest.expectedFailure
    def test_head_projects_id_tasks_invalid_id(self):
        # ERROR: This request should return an error since it is requesting an inexistant project
        response = requests.head('http://localhost:4567/projects/-1/tasks', headers={'Accept': 'application/json'})
        # Check if Content-Type in header is application/json
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 404)

    def test_post_projects_id_tasks_json(self): 
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
        # Compare response with expected json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(todos_json['id'], todo_id['id'])
        self.assertIn(todo_id, todos_json['tasksof'])

    def test_post_projects_id_tasks_xml(self):
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
        # Compare response with expected json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(todos_xml.find("./todo/id").text, todo_id['id'])
        self.assertIn(project_xml.find("./id").text, [id.text for id in todos_xml.findall("./todo/tasksof/id")])

    def test_post_projects_id_tasks_invalid_task_id(self): 
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

        # Create relationship between new project and invalid todo
        invalid_todo_id = {
            "id": "-1"
        }
        response = requests.post('http://localhost:4567/projects/' + project_json["id"] + '/tasks', json = invalid_todo_id, headers={'Accept': 'application/json'})
        error_json = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(error_json['errorMessages'][0], "Could not find thing matching value for id")

    def test_post_projects_id_tasks_invalid_project_id(self):
        # Create relationship between an invalid project and todo 1
        todo_id = {
            "id": "1"
        }
        response = requests.post('http://localhost:4567/projects/-1/tasks', json = todo_id, headers={'Accept': 'application/json'})
        error_json = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(error_json['errorMessages'][0], "Could not find parent thing for relationship projects/-1/tasks")

    def test_post_projects_id_tasks_invalid_field(self):
        # UNDOCUMENTED BEHAVIOUR: When assigning a todo to a project, specifying the title field instead of the id will automatically create a new instance of todo and assign it to the project
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

        # Create relationship between new project and new todo
        todo_title = {
            "title": "a task"
        }
        response = requests.post('http://localhost:4567/projects/' + project_json["id"] + '/tasks', json = todo_title, headers={'Accept': 'application/json'})
        todo_json = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", todo_json)
        self.active_todos.append(todo_json['id'])
        self.assertEqual(todo_json['title'], todo_title['title'])
        self.assertEqual(todo_json['tasksof'][0]['id'], project_json["id"])

        # Verify if relationship was properly applied
        response = requests.get('http://localhost:4567/projects/' + project_json["id"] + '/tasks', headers={'Accept': 'application/json'})
        returned_todo_json = response.json()['todos'][0]
        # Compare response with expected json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(returned_todo_json['id'], todo_json['id'])
        self.assertEqual(returned_todo_json['title'], todo_json['title'])
        self.assertEqual(returned_todo_json['doneStatus'], todo_json['doneStatus'])
        self.assertEqual(returned_todo_json['description'], todo_json['description'])
        self.assertEqual(returned_todo_json['tasksof'], todo_json['tasksof'])
        