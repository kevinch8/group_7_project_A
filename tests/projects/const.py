import json

DEFAULT_PROJECT_JSON = {
    "projects": [
        {
            "id": "1",
            "title": "Office Work",
            "completed": "false",
            "active": "false",
            "description": "",
            "tasks": [
                {
                    "id": "1"
                },
                {
                    "id": "2"
                }
            ]
        }
    ]
}

DEFAULT_PROJECT_XML = "<projects><project><active>false</active><description/><id>1</id><completed>false</completed><title>Office Work</title><tasks><id>1</id></tasks><tasks><id>2</id></tasks></project></projects>"