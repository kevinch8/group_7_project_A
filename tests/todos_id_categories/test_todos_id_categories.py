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
        self.active_categories = []

    def tearDown(self):
        for id in self.active_todos:
            response = requests.delete("http://localhost:4567/todos/" + id)

        for id in self.active_categories:
            response = requests.delete("http://localhost:4567/categories/" + id)

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
        # Create a new todo to establish a category relationship
        category_todo = {
            "title": "Todo to be associated to category",
            "doneStatus": False,
            "description": ""
            }
        response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=category_todo)
        actual_category_todo = response.json()
        # Check if what was created matches the title we want
        self.assertEqual(category_todo["title"], actual_category_todo["title"])
        self.assertEqual(response.status_code, 201)
        self.active_todos.append(actual_category_todo["id"])

        # Create relationship with default category 1
        identify_json = {
            "id": "1"
        }
        response = requests.post('http://localhost:4567/todos/' + actual_category_todo["id"] + '/categories', json=identify_json)
        self.assertEqual(response.status_code, 201)

        # Check if category 1 is added to the todo
        response = requests.get('http://localhost:4567/todos/' + actual_category_todo["id"] + '/categories', json=identify_json)
        assigned_category = response.json()['categories']
        self.assertEqual(assigned_category[0], const.CATEGORIES_DEFAULT_JSON_1)
        self.assertEqual(response.status_code, 200)
        
    def test_post_todos_id_categories_xml(self):
        # Create a new todo to establish a category relationship
        category_todo = {
            "title": "Todo to be associated to category",
            "doneStatus": False,
            "description": ""
            }
        response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=category_todo)
        actual_category_todo = response.json()
        # Check if what was created matches the title we want
        self.assertEqual(category_todo["title"], actual_category_todo["title"])
        self.assertEqual(response.status_code, 201)
        self.active_todos.append(actual_category_todo["id"])

        # Create relationship with default category 1
        identify_json = {
            "id": "1"
        }
        response = requests.post('http://localhost:4567/todos/' + actual_category_todo["id"] + '/categories', json=identify_json)
        self.assertEqual(response.status_code, 201)

        # Check if category 1 is added to the todo (data received in XML)
        response = requests.get('http://localhost:4567/todos/' + actual_category_todo["id"] + '/categories',headers={'Accept': 'application/xml'}, json=identify_json)
        assigned_category = ET.fromstring(response.content)
        self.assertTrue(elements_equal(assigned_category, ET.fromstring(const.CATEGORIES_DEFAULT_XML_1)))
        self.assertEqual(response.status_code, 200)

    def test_post_todos_id_categories_invalid_todo_id(self):
        identify_json = {
            "id": "1"
        }
        response = requests.post('http://localhost:4567/todos/-1/categories', json=identify_json)
        error_msg = response.json()["errorMessages"][0]
        self.assertEqual(error_msg, "Could not find parent thing for relationship todos/-1/categories")
        self.assertEqual(response.status_code, 404)

    def test_post_todos_id_categories_invalid_category_id(self):
        identify_json = {
            "id": "0"
        }
        response = requests.post('http://localhost:4567/todos/1/categories', json=identify_json)
        error_msg = response.json()["errorMessages"][0]
        self.assertEqual(error_msg, "Could not find thing matching value for id")
        self.assertEqual(response.status_code, 404)

    def test_post_todos_id_categories_with_title(self):
        # Undocumented behavior is the creation of category if no id is provided and only a title is given
        # Create a new todo to establish a category relationship
        category_todo = {
            "title": "Todo to be associated to category",
            "doneStatus": False,
            "description": ""
            }
        response = requests.post('http://localhost:4567/todos', headers={'Accept': 'application/json'}, json=category_todo)
        actual_category_todo = response.json()
        # Check if what was created matches the title we want
        self.assertEqual(category_todo["title"], actual_category_todo["title"])
        self.assertEqual(response.status_code, 201)
        self.active_todos.append(actual_category_todo["id"])

        # Create relationship with category that does not exist
        new_category = {
            "title": "test_category"
        }
        response = requests.post('http://localhost:4567/todos/' + actual_category_todo["id"] + '/categories', json=new_category)
        created_category = response.json()
        self.assertEqual(created_category["title"], new_category["title"]) # There is a response with body of category as well.
        self.assertEqual(response.status_code, 201)
        self.active_categories.append(created_category["id"])

        identify_json = {
            "id": created_category["id"]
        }
        # Check if new category is added to the todo
        response = requests.get('http://localhost:4567/todos/' + actual_category_todo["id"] + '/categories', json=identify_json)
        assigned_category = response.json()['categories']
        self.assertEqual(assigned_category[0], created_category)
        self.assertEqual(response.status_code, 200)