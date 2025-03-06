import os
import json
import datetime
import xml.etree.ElementTree as ET


class QMetryConfig:
    def __init__(self):
        from .plugin import QMetryApi

        self.config = QMetryApi()
        self.properties = self.config.properties
        self.qmetry_url = self.properties.get("qmetry.url")
        self.authorization = self.properties.get("qmetry.authorization")

    def automation_import_result_header(self):
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "apiKey": self.properties.get("qmetry.automation.apikey"),
            "Authorization": self.authorization,
        }

    def automation_import_result_payload(self):
        payload = {
            "format": "cucumber",
            "attachFile": self.properties.get("qmetry.automation.payload.attachFile", "true").lower() != "false",
            "isZip": self.properties.get("qmetry.automation.payload.isZip", "false").lower() == "true",
            "environment": self.properties.get("qmetry.automation.payload.environment", ""),
            "build": self.properties.get("qmetry.automation.payload.build", ""),

            "fields": {
                "testCycle": {
                    "labels": self.properties.get("qmetry.automation.payload.fields.testCycle.labels", "").split(","),
                    "status": self.properties.get("qmetry.automation.payload.fields.testCycle.status", ""),
                    "summary": self.properties.get("qmetry.automation.payload.fields.testCycle.summary", ""),
                    "customFields": self.build_custom_fields(self.properties.get("qmetry.automation.payload.fields.testCycle.customFields", "")),
                },
                "testCase": {
                    "labels": self.properties.get("qmetry.automation.payload.fields.testCase.labels", "").split(","),
                    "status": self.properties.get("qmetry.automation.payload.fields.testCase.status", ""),
                }
            }
        }
        return payload
    
    def build_custom_fields(self, custom_fields_str):
        custom_fields = []
        if custom_fields_str:
            pairs = custom_fields_str.split(",")
            for pair in pairs:
                name, value = pair.split(":")
                custom_fields.append({"name": name.strip(), "value": value.strip()})
        return custom_fields

    def automation_file_upload_header(self):
        return {
            "apiKey": self.properties.get("qmetry.automation.apikey"),
            "Authorization": self.authorization,
        }

    def automation_file_upload_payload(self):
        file = self.properties.get("qmetry.automation.resultfile", "")

        if not file.endswith(".json"):
            self.junit_to_cucumber()
            cucumber_json_file = file.replace(".xml", ".json")
        else:
            cucumber_json_file = file

        filename_with_extension = os.path.basename(cucumber_json_file)

        return [
            (
                "file",
                (
                    filename_with_extension,
                    open(cucumber_json_file, "rb"),
                    "application/json",
                ),
            )
        ]

    def junit_to_cucumber(self):
        tree = ET.parse(self.properties.get("qmetry.automation.resultfile"))
        root = tree.getroot()

        cucumber_results = []

        for testcase in root.findall(".//testcase"):
            scenario_name = testcase.get("name")
            classname = testcase.get("classname")

            if testcase.find("failure") is not None:
                status = "failed"
            elif testcase.find("error") is not None:
                status = "failed"
            elif testcase.find("skipped") is not None:
                status = "skipped"
            else:
                status = "passed"

            feature = {
                "elements": [
                    {
                        "id": f"features/{classname}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.feature",
                        "keyword": "Scenario",
                        "name": scenario_name,
                        "steps": [
                            {
                                "keyword": "Given",
                                "name": "",
                                "result": {"status": status},
                            }
                        ],
                        "tags": [],
                        "type": "scenario",
                    }
                ],
                "id": f"features/{classname}.feature",
                "keyword": "Feature",
                "name": "feature name",
                "tags": [],
                "uri": f"features/{classname}.feature",
            }

            cucumber_results.append(feature)

        cucumber_json_file = self.properties.get(
            "qmetry.automation.resultfile"
        ).replace(".xml", ".json")

        with open(cucumber_json_file, "w") as json_file:
            json.dump(cucumber_results, json_file, indent=2)
