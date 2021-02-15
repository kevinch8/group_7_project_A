import requests
import subprocess
import unittest
import json
from tests.projects_id_categories import const
import xml.etree.ElementTree as ET
from tests.helper_functions import elements_equal

class TestProjectsIdCategories(unittest.TestCase):

    def setUp(self):
        self.active_projects = []

    def tearDown(self):
        for id in self.active_projects:
            response = requests.delete("http://localhost:4567/projects/" + id)

    def test_get_projects_id_categories_json(self):
        response = requests.get('http://localhost:4567/projects/1/categories', headers={'Accept': 'application/json'})
        categories_json = response.json()
        # Compare response with expected json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(categories_json['categories'], [])

    def test_get_projects_id_categories_xml(self):
        response = requests.get('http://localhost:4567/projects/1/categories', headers={'Accept': 'application/xml'})
        categories_xml = ET.fromstring(response.content)
        # Compare response with expected json
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(categories_xml.find("./categories"))

    @unittest.expectedFailure
    def test_get_projects_id_categories_invalid_id_bug(self):
        # This test should return an error status code as it's requesting for an invalid project id
        response = requests.get('http://localhost:4567/projects/-1/categories', headers={'Accept': 'application/json'})
        categories_json = response.json()
        # Compare response with expected json
        self.assertEqual(response.status_code, 404)

    def test_head_projects_id_categories_json(self):
        response = requests.head('http://localhost:4567/projects/1/categories', headers={'Accept': 'application/json'})
        # Check if Content-Type in header is application/json
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)

    def test_head_projects_id_categories_xml(self):
        response = requests.head('http://localhost:4567/projects/1/categories', headers={'Accept': 'application/xml'})
        # Check if Content-Type in header is application/json
        self.assertEqual(response.headers['Content-Type'], 'application/xml')
        self.assertEqual(response.status_code, 200)

    def test_post_projects_id_categories_json(self):
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

        # Create relationship between new project and default category 1
        category_id = {
            "id": "1"
        }
        response = requests.post('http://localhost:4567/projects/' + project_json["id"] + '/categories', json = category_id, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 201)

        # Verify if relationship was properly applied
        response = requests.get('http://localhost:4567/projects/' + project_json["id"] + '/categories', headers={'Accept': 'application/json'})
        categories_json = response.json()
        # Compare response with expected json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(categories_json['categories'][0], const.CATEGORIES_DEFAULT_JSON_1)

    def test_post_projects_id_categories_xml(self):
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

        # Create relationship between new project and default category 1
        category_id = {
            "id": "1"
        }
        response = requests.post('http://localhost:4567/projects/' + project_xml.find("./id").text + '/categories', json = category_id, headers={'Accept': 'application/xml'})
        self.assertEqual(response.status_code, 201)

        # Verify if relationship was properly applied
        response = requests.get('http://localhost:4567/projects/' + project_xml.find("./id").text + '/categories', headers={'Accept': 'application/xml'})
        categories_xml = ET.fromstring(response.content)
        expected_category_xml = ET.fromstring(const.CATEGORIES_DEFAULT_XML_1)
        # Compare response with expected json
        self.assertEqual(response.status_code, 200)
        self.assertTrue(elements_equal(categories_xml, expected_category_xml))

    def test_post_projects_id_categories_invalid_id(self):
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

        # Create relationship between new project and invalid category
        category_id = {
            "id": "-1"
        }
        response = requests.post('http://localhost:4567/projects/' + project_json["id"] + '/categories', json = category_id, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 404)
        error_json = response.json()
        self.assertEqual(error_json['errorMessages'][0], "Could not find thing matching value for id")

    def test_post_projects_id_categories_invalid_project_id(self):
        # Create relationship between an invalid project and default category 1
        category_id = {
            "id": "1"
        }
        response = requests.post('http://localhost:4567/projects/-1/categories', json = category_id, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 404)
        error_json = response.json()
        self.assertEqual(error_json['errorMessages'][0], "Could not find parent thing for relationship projects/-1/categories")

    def test_post_projects_id_categories_invalid_field(self):
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

        # Create relationship between new project and default category 1
        category_invalid_field = {
            "invalid_field": "invalid_value"
        }
        response = requests.post('http://localhost:4567/projects/' + project_json["id"] + '/categories', json = category_invalid_field, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 400)
        error_json = response.json()
        self.assertEqual(error_json['errorMessages'][0], "java.lang.NullPointerException")
        

    def test_post_projects_id_categories_with_title(self):
        # UNDOCUMENTED BEHAVIOUR: When a title is provided instead of an id, a new category is created and associated with the project
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

        # Create relationship between new project and default category 1
        category_title = {
            "title": "Games"
        }
        response = requests.post('http://localhost:4567/projects/' + project_json["id"] + '/categories', json = category_title, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 201)
        category_json = response.json()
        # Verify the content of the new category
        self.assertIn("id", category_json)
        self.assertIn("description", category_json)
        self.assertEqual(category_json["title"], category_title["title"])

        # Verify if relationship was properly applied
        response = requests.get('http://localhost:4567/projects/' + project_json["id"] + '/categories', headers={'Accept': 'application/json'})
        returned_category_json = response.json()['categories'][0]
        # Compare response with expected json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(returned_category_json['id'], category_json['id'])
        self.assertEqual(returned_category_json['title'], category_json['title'])
        self.assertEqual(returned_category_json['description'], category_json['description'])
