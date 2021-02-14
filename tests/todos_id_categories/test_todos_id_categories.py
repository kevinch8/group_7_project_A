import requests
import subprocess
import unittest
from tests.todos_id_categories import const
import xml.etree.ElementTree as ET
from tests.helper_functions import elements_equal
import json

class TestTodosIdCategories(unittest.TestCase):

    def setUp(self):
        self.active_todos = []

    def tearDown(self):
        for id in self.active_todos:
            response = requests.delete("http://localhost:4567/todos/" + id)

    def test_get_todos_id_categories_json(self):
        response = requests.get('http://localhost:4567/todos/1/categories', headers={'Accept': 'application/json'})
        categories_json_1 = response.json()['categories'][0]
        # Compare expected default categories json with id 1
        self.assertEqual(categories_json_1, const.CATEGORIES_DEFAULT_JSON_1)
        self.assertEqual(response.status_code, 200)

    def test_get_todos_id_categories_xml(self):
        response = requests.get('http://localhost:4567/todos/1/categories', headers={'Accept': 'application/xml'})
        categories_xml_1 = ET.fromstring(response.content)
        # Compare expected default categories xml with id 1
        self.assertTrue(elements_equal(categories_xml_1, ET.fromstring(const.CATEGORIES_DEFAULT_XML_1)))
        self.assertEqual(response.status_code, 200)

    def test_get_todos_id_categories_invalid_id(self):
        # This tests an undocumented behavior of inserting an invalid id
        # There are 2 default categories -> but only 1 shows up. This endpoint shows all categories that have a RELATIONSHIP with a todo
        # Therefore, we should only see the first category that is associated to todo id=1
        response = requests.get('http://localhost:4567/todos/-1/categories', headers={'Accept': 'application/json'})
        list_of_categories = response.json()
        self.assertEqual(list_of_categories["categories"][0], const.CATEGORIES_DEFAULT_JSON_1)
        self.assertEqual(response.status_code, 200)

    @unittest.expectedFailure
    def test_head_todos_id_categories_json_invalid_expected_fail(self):
        # Getting relationship between id and categories that does not exist should fail
        response = requests.get('http://localhost:4567/todos/-1/categories', headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 404)

    def test_get_todos_id_categories_no_id(self):
        # This tests an undocumented behavior of having no id
        # This also shows the list of all categories that have existing relationships
        response = requests.get('http://localhost:4567/todos/categories', headers={'Accept': 'application/json'})
        list_of_categories = response.json()
        self.assertEqual(list_of_categories["categories"][0], const.CATEGORIES_DEFAULT_JSON_1)
        self.assertEqual(response.status_code, 200)

    def test_head_todos_id_categories_json(self):
        response = requests.head('http://localhost:4567/todos/1/categories', headers={'Accept': 'application/json'})
        # Check if Content-Type in header is application/json
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)

    @unittest.expectedFailure
    def test_head_todos_id_categories_json_invalid(self):
        # Expect failed
        response = requests.head('http://localhost:4567/todos/-1/categories', headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 404)


    def test_head_todos_id_categories_xml(self):
        response = requests.head('http://localhost:4567/todos/1/categories', headers={'Accept': 'application/xml'})
        # Check if Content-Type in header is application/xml
        self.assertEqual(response.headers['Content-Type'], 'application/xml')
        self.assertEqual(response.status_code, 200)

    def test_post_todos_id_categories_json(self):
        category_todo = {
            "title": "Todo to be associated to category",
            "doneStatus": False,
            "description": ""
            }
        response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=category_todo)
        actual_category_todo = response.json()
        # Check if what was created matches the title we want
        self.assertEqual(sample_todo["title"], actual_category_todo["title"])
        self.assertEqual(response.status_code, 201)
        self.active_todos.append(actual_category_todo["id"])

        identify_json = {
            "id": str(actual_category_todo["id"])
        }
        response = requests.post('http://localhost:4567/todos/' + actual_category_todo["id"] + '/categories', json=identify_json)
        
        # Create a new todo to establish a category relationship





    # def test_get_todos_invalid_id_json(self):
    #     response = requests.get('http://localhost:4567/todos/-1', headers={'Accept': 'application/json'})
    #     error_msg = response.json()
    #     # Compare expected error message for invalid ID
    #     self.assertEqual(error_msg["errorMessages"][0], "Could not find an instance with todos/-1")
    #     self.assertEqual(response.status_code, 404)

    # def test_get_todos_id_xml(self):
    #     response = requests.get('http://localhost:4567/todos/1', headers={'Accept': 'application/xml'})
    #     actual_todos_xml = ET.fromstring(response.content)
    #     # Compare actual xml from expected xml
    #     expected_todos_xml = ET.fromstring(const.TODOS_DEFAULT_XML_1)
    #     self.assertTrue(elements_equal(actual_todos_xml, expected_todos_xml))
    #     self.assertEqual(response.status_code, 200)

    # def test_head_todos_id_json(self):
    #     response = requests.head('http://localhost:4567/todos/1', headers={'Accept': 'application/json'})
    #     # Check if Content-Type in header is application/json
    #     self.assertEqual(response.headers['Content-Type'], 'application/json')
    #     self.assertEqual(response.status_code, 200)

    # def test_head_todos_id_xml(self):
    #     response = requests.head('http://localhost:4567/todos/1', headers={'Accept': 'application/xml'})
    #     # Check if Content-Type in header is application/xml
    #     self.assertEqual(response.headers['Content-Type'], 'application/xml')
    #     self.assertEqual(response.status_code, 200)

    # def test_post_todos_id_json(self):
    #     # Create a json to edit
    #     modifiable_todo = {
    #         "title": "Test Todo To Edit",
    #         "doneStatus": False,
    #         "description": ""
    #         }
    #     response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=modifiable_todo)
    #     modifiable_todo_actual = response.json()
    #     # Check if what was created matches the title we want
    #     self.assertEqual(modifiable_todo["title"], modifiable_todo_actual["title"])
    #     self.assertEqual(response.status_code, 201)
    #     self.active_todos.append(modifiable_todo_actual["id"])

    #     # Check if json actually exists
    #     response = requests.get('http://localhost:4567/todos/' + modifiable_todo_actual["id"], headers={'Accept': 'application/json'})
    #     obtained_todo = response.json()['todos'][0]
    #     # Check if created todo matches what we have
    #     self.assertEqual(modifiable_todo_actual, obtained_todo)
    #     self.assertEqual(response.status_code, 200)

    #     # Modify the newly created json
    #     modified_todo = {
    #         "title": "Edited Todo",
    #         "doneStatus": False,
    #         "description": ""
    #     }
    #     response = requests.post('http://localhost:4567/todos/' + modifiable_todo_actual["id"], headers={'Accept': 'application/json'}, json=modified_todo)
    #     modified_todo_actual = response.json()
    #     # Check if new edited has the right title
    #     self.assertEqual(modified_todo_actual["title"], modified_todo["title"])
    #     self.assertEqual(response.status_code, 200)

    # def test_post_todos_xml(self):
    #     # Create a json to edit
    #     modifiable_todo = {
    #         "title": "Test Todo To Edit",
    #         "doneStatus": False,
    #         "description": ""
    #         }
    #     response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=modifiable_todo)
    #     modifiable_todo_actual = response.json()
    #     # Check if what was created matches the title we want
    #     self.assertEqual(modifiable_todo["title"], modifiable_todo_actual["title"])
    #     self.assertEqual(response.status_code, 201)
    #     self.active_todos.append(modifiable_todo_actual["id"])

    #     # Check if json actually exists
    #     response = requests.get('http://localhost:4567/todos/' + modifiable_todo_actual["id"], headers={'Accept': 'application/json'})
    #     obtained_todo = response.json()['todos'][0]
    #     # Check if created todo matches what we have
    #     self.assertEqual(modifiable_todo_actual, obtained_todo)
    #     self.assertEqual(response.status_code, 200)

    #     # Modify the newly created json
    #     modified_todo = {
    #         "title": "Edited Todo",
    #         "doneStatus": False,
    #         "description": ""
    #     }
    #     # Test for XML payload
    #     response = requests.post('http://localhost:4567/todos/' + modifiable_todo_actual["id"], headers={'Accept': 'application/xml'}, json=modified_todo)
    #     modified_todo_actual =  ET.fromstring(response.content)
    #     # Check if new edited has the right title
    #     self.assertEqual(modified_todo_actual.find("./title").text , modified_todo["title"])
    #     self.assertEqual(response.status_code, 200)

    # def test_post_todos_id_empty(self):
    #     # This shows the unintended behavior of giving us the contend of todo id=1, (the get method returns todos with 1 todo)
    #     response = requests.post('http://localhost:4567/todos/1', headers={'Accept': 'application/json'})
    #     actual_todo_json_1 = response.json()
    #     # Compare expected default json with id 1
    #     self.assertEqual(actual_todo_json_1, const.TODOS_DEFAULT_JSON_1)
    #     self.assertEqual(response.status_code, 200)

    # def test_put_todos_id_json(self):
    #     # Create a json to edit
    #     modifiable_todo = {
    #         "title": "Test Todo To Edit",
    #         "doneStatus": False,
    #         "description": ""
    #         }
    #     response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=modifiable_todo)
    #     modifiable_todo_actual = response.json()
    #     # Check if what was created matches the title we want
    #     self.assertEqual(modifiable_todo["title"], modifiable_todo_actual["title"])
    #     self.assertEqual(response.status_code, 201)
    #     self.active_todos.append(modifiable_todo_actual["id"])

    #     # Check if json actually exists
    #     response = requests.get('http://localhost:4567/todos/' + modifiable_todo_actual["id"], headers={'Accept': 'application/json'})
    #     obtained_todo = response.json()['todos'][0]
    #     # Check if created todo matches what we have
    #     self.assertEqual(modifiable_todo_actual, obtained_todo)
    #     self.assertEqual(response.status_code, 200)

    #     # Modify the newly created json with PUT method
    #     modified_todo = {
    #         "title": "Edited Todo",
    #         "doneStatus": False,
    #         "description": ""
    #     }
    #     response = requests.put('http://localhost:4567/todos/' + modifiable_todo_actual["id"], headers={'Accept': 'application/json'}, json=modified_todo)
    #     modified_todo_actual = response.json()
    #     # Check if new edited has the right title
    #     self.assertEqual(modified_todo_actual["title"], modified_todo["title"])
    #     self.assertEqual(response.status_code, 200)

    # def test_put_todos_xml(self):
    #     # Create a json to edit
    #     modifiable_todo = {
    #         "title": "Test Todo To Edit",
    #         "doneStatus": False,
    #         "description": ""
    #         }
    #     response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=modifiable_todo)
    #     modifiable_todo_actual = response.json()
    #     # Check if what was created matches the title we want
    #     self.assertEqual(modifiable_todo["title"], modifiable_todo_actual["title"])
    #     self.assertEqual(response.status_code, 201)
    #     self.active_todos.append(modifiable_todo_actual["id"])

    #     # Check if json actually exists
    #     response = requests.get('http://localhost:4567/todos/' + modifiable_todo_actual["id"], headers={'Accept': 'application/json'})
    #     obtained_todo = response.json()['todos'][0]
    #     # Check if created todo matches what we have
    #     self.assertEqual(modifiable_todo_actual, obtained_todo)
    #     self.assertEqual(response.status_code, 200)

    #     # Modify the newly created json
    #     modified_todo = {
    #         "title": "Edited Todo",
    #         "doneStatus": False,
    #         "description": ""
    #     }
    #     # Test for XML payload with PUT method
    #     response = requests.put('http://localhost:4567/todos/' + modifiable_todo_actual["id"], headers={'Accept': 'application/xml'}, json=modified_todo)
    #     modified_todo_actual =  ET.fromstring(response.content)
    #     # Check if new edited has the right title
    #     self.assertEqual(modified_todo_actual.find("./title").text , modified_todo["title"])
    #     self.assertEqual(response.status_code, 200)

    # def test_put_todos_id_empty(self):
    #     # This shows that unlike post, this shows the proper error message.
    #     response = requests.put('http://localhost:4567/todos/1', headers={'Accept': 'application/json'})
    #     error_message_json = response.json()
    #     # See if expected error message is received
    #     self.assertEqual(error_message_json["errorMessages"][0], "title : field is mandatory")
    #     self.assertEqual(response.status_code, 400)

    # def test_delete_todos_id_json(self):
    #     # Create a todo to delete
    #     todo_to_delete = {
    #         "title": "Test Todo To DELETE",
    #         "doneStatus": False,
    #         "description": ""
    #         }
    #     response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=todo_to_delete)
    #     actual_todo_to_delete = response.json()
    #     # Check if what was created matches the title we want
    #     self.assertEqual(actual_todo_to_delete["title"], todo_to_delete["title"])
    #     self.assertEqual(response.status_code, 201)
    #     self.active_todos.append(actual_todo_to_delete["id"])

    #     # Delete the todo
    #     response = requests.delete('http://localhost:4567/todos/' + actual_todo_to_delete["id"] , headers={'Accept': 'application/json'})
    #     self.assertEqual(response.status_code, 200)

    #     # Check if todo exists
    #     response = requests.get('http://localhost:4567/todos/' + actual_todo_to_delete["id"], headers={'Accept': 'application/json'})
    #     error_message = response.json()
    #     self.assertEqual(error_message["errorMessages"][0], "Could not find an instance with todos/" + actual_todo_to_delete["id"])
    #     self.assertEqual(response.status_code, 404)

    

        

