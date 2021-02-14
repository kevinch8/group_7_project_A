import requests
import subprocess
import unittest
from tests.todos_id_tasksof import const
import xml.etree.ElementTree as ET
from tests.helper_functions import elements_equal
import json

class TestTodosIdTasksofId(unittest.TestCase):

    def setUp(self):
        self.active_todos = []


    def tearDown(self):
        for id in self.active_todos:
            response = requests.delete("http://localhost:4567/todos/" + id)


    def test_delete_todos_id_tasksof_json(self):
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

        response = requests.delete('http://localhost:4567/todos/'+ actual_tasksof_todo["id"] + '/tasksof/1', headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)

        response = requests.get('http://localhost:4567/todos/'+ actual_tasksof_todo["id"] + '/tasksof', headers={'Accept': 'application/json'})
        empty_projects = response.json()
        self.assertFalse(empty_projects) # Check if no projects is associated to current todo
        self.assertEqual(response.status_code, 200)
        
    def test_delete_todos_id_tasksof_invalid_todo_but_valid_project(self):
        response = requests.post('http://localhost:4567/todos/-1/tasksof/1')
        error_msg = response.json()["errorMessages"][0]
        self.assertEqual(error_msg, "java.lang.NullPointerException")
        self.assertEqual(response.status_code, 400)

    def test_delete_todos_id_tasksof_valid_todo_invalid_project(self):
        response = requests.post('http://localhost:4567/todos/1/tasksof/-1')
        error_msg = response.json()["errorMessages"][0]
        self.assertEqual(error_msg, "Could not find any instances with todos/1/tasksof/-1")
        self.assertEqual(response.status_code, 404)
        

