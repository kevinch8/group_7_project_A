import requests
import subprocess
import unittest
from tests.todos_id_categories import const
import xml.etree.ElementTree as ET
from tests.helper_functions import elements_equal
import json

class TestTodosIdCategoriesId(unittest.TestCase):

    def test_delete_todos_id_categories_id_json(self):
        # Create category relationship of category 1 to todo id=2
        identify_category = {
            "id": "1"
        }
        response = requests.post('http://localhost:4567/todos/2/categories', headers={'Accept': 'application/json'}, json=identify_category)
        self.assertEqual(response.status_code, 201)

        # Check if category relationship was created
        response = requests.get('http://localhost:4567/todos/2/categories', headers={'Accept': 'application/json'})
        categories_json_1 = response.json()['categories'][0]
        self.assertEqual(categories_json_1, const.CATEGORIES_DEFAULT_JSON_1)
        self.assertEqual(response.status_code, 200)

        # Delete category relationship
        response = requests.delete('http://localhost:4567/todos/2/categories/1', headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)

        # Check if category still exists
        response = requests.get('http://localhost:4567/todos/2/categories', headers={'Accept': 'application/json'})
        empty_categories = response.json()['categories']
        self.assertFalse(empty_categories)
        self.assertEqual(response.status_code, 200)


    def test_delete_todos_id_categories_id_invalid_category_id_json(self):
        response = requests.delete('http://localhost:4567/todos/2/categories/-1', headers={'Accept': 'application/json'})
        error_msg = response.json()["errorMessages"][0]
        self.assertEqual(error_msg, "Could not find any instances with todos/2/categories/-1")
        self.assertEqual(response.status_code, 404)

    def test_delete_todos_id_categories_id_invalid_category_id_xml(self):
        response = requests.delete('http://localhost:4567/todos/2/categories/-1', headers={'Accept': 'application/xml'})
        error_msg = ET.fromstring(response.content).find("./errorMessage").text
        self.assertEqual(error_msg, "Could not find any instances with todos/2/categories/-1")
        self.assertEqual(response.status_code, 404)        

    