import requests
import subprocess
import unittest
import json
from tests.projects import const
import xml.etree.ElementTree as ET
from tests.helper_functions import elements_equal

class TestProjects(unittest.TestCase):

    def setUp(self):
        self.active_projects = []

    def tearDown(self):
        for i in self.active_projects:
            requests.delete('http://localhost:4567/projects/' + i)

    def test_get_projects_json(self):
        response = requests.get('http://localhost:4567/projects', headers={'Accept': 'application/json'})
        project_json = response.json()
        # Compare response with expected json
        self.assertEqual(response.status_code, 200)
        self.assertIn(project_json, [const.DEFAULT_PROJECT_JSON_V1, const.DEFAULT_PROJECT_JSON_V2])

    def test_get_projects_xml(self):
        response = requests.get('http://localhost:4567/projects', headers={'Accept': 'application/xml'})
        # Compare response with expected xml
        project_xml = ET.fromstring(response.content)
        expected_project_xml_v1 = ET.fromstring(const.DEFAULT_PROJECT_XML_V1)
        expected_project_xml_v2 = ET.fromstring(const.DEFAULT_PROJECT_XML_V2)
        self.assertTrue(elements_equal(project_xml, expected_project_xml_v1) or elements_equal(project_xml, expected_project_xml_v2))
        self.assertEqual(response.status_code, 200)

    def test_head_projects_json(self):
        response = requests.head('http://localhost:4567/projects', headers={'Accept': 'application/json'})
        # Check if Content-Type in header is application/json
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)

    def test_head_projects_xml(self):
        response = requests.head('http://localhost:4567/projects', headers={'Accept': 'application/xml'})
        # Check if Content-Type in header is application/xml
        self.assertEqual(response.headers['Content-Type'], 'application/xml')
        self.assertEqual(response.status_code, 200)

    def test_create_project_json(self):
        project_data = {
            "title": "School Work",
            "completed": False,
            "active": False,
            "description": "Work on assignments."
        }
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

        response = requests.get('http://localhost:4567/projects/' + project_json['id'], headers={'Accept': 'application/json'})
        obtained_project = response.json()['projects'][0]
        # Check if created project matches what we have
        self.assertEqual(response.status_code, 200)
        self.assertEqual(project_json, obtained_project)

    def test_create_project_xml(self):
        project_data = {
            "title": "School Work",
            "completed": False,
            "active": False,
            "description": "Work on assignments."
        }
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

    def test_create_project_wrong_field_json(self):
        project_data = {
            "title": "School Work",
            "x": False,
            "active": False,
            "description": "Work on assignments."
        }
        response = requests.post('http://localhost:4567/projects', json = project_data, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 400)
        error_json = response.json()
        # Check if error message is returned
        self.assertEqual(error_json['errorMessages'][0], "Could not find field: x")

    def test_create_project_wrong_field_xml(self):
        project_data = {
            "title": "School Work",
            "x": False,
            "active": False,
            "description": "Work on assignments."
        }
        response = requests.post('http://localhost:4567/projects', json = project_data, headers={'Accept': 'application/xml'})
        self.assertEqual(response.status_code, 400)
        error_xml = ET.fromstring(response.content)
        # Check if error message is returned
        self.assertEqual(error_xml.find("./errorMessage").text, "Could not find field: x")
