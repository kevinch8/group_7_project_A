import requests
import subprocess
import unittest
import json
from tests.projects_id_categories_id import const
import xml.etree.ElementTree as ET
from tests.helper_functions import elements_equal

class TestProjectsIdCategoriesId(unittest.TestCase):
    def setUp(self):
        self.active_projects = []

    def tearDown(self):
        for id in self.active_projects:
            response = requests.delete("http://localhost:4567/projects/" + id)

    def test_delete_projects_id_categories_id_json(self):
        # Create relationship between default project 1 and default category 1
        category_id = {
            "id": "1"
        }
        response = requests.post('http://localhost:4567/projects/1/categories', json = category_id, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 201)

        # Verify if relationship was properly applied
        response = requests.get('http://localhost:4567/projects/1/categories', headers={'Accept': 'application/json'})
        categories_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(categories_json['categories'][0], const.CATEGORIES_DEFAULT_JSON_1)

        # Delete relationship between default project 1 and cateory 1
        response = requests.delete('http://localhost:4567/projects/1/categories/1', headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)

        # Verify that relationship was deleted properly
        response = requests.get('http://localhost:4567/projects/1/categories', headers={'Accept': 'application/json'})
        categories_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(categories_json['categories'], [])

    def test_delete_projects_id_categories_id_xml(self):
        # Create relationship between default project 1 and default category 1
        category_id = {
            "id": "1"
        }
        response = requests.post('http://localhost:4567/projects/1/categories', json = category_id, headers={'Accept': 'application/xml'})
        self.assertEqual(response.status_code, 201)

        # Verify if relationship was properly applied
        response = requests.get('http://localhost:4567/projects/1/categories', headers={'Accept': 'application/xml'})
        categories_xml = ET.fromstring(response.content)
        expected_category_xml = ET.fromstring(const.CATEGORIES_DEFAULT_XML_1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(elements_equal(categories_xml, expected_category_xml))

        # Delete relationship between default project 1 and cateory 1
        response = requests.delete('http://localhost:4567/projects/1/categories/1', headers={'Accept': 'application/xml'})
        self.assertEqual(response.status_code, 200)

        # Verify that relationship was deleted properly
        response = requests.get('http://localhost:4567/projects/1/categories', headers={'Accept': 'application/xml'})
        categories_xml = ET.fromstring(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(categories_xml.find("./categories"))

    def test_delete_projects_id_categories_id_invalid_id(self):
        # Delete relationship between default project 1 and an invalid id
        response = requests.delete('http://localhost:4567/projects/1/categories/-1', headers={'Accept': 'application/json'})
        error_json = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(error_json['errorMessages'][0], "Could not find any instances with projects/1/categories/-1")