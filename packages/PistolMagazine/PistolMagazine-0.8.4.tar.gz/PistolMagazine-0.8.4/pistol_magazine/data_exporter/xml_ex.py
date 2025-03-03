import dicttoxml

from pistol_magazine.data_exporter.exporter import Exporter


class XMLExporter(Exporter):
    def export(self, data, filename):
        xml_data = dicttoxml.dicttoxml(data)
        with open(filename, 'wb') as output_file:
            output_file.write(xml_data)


if __name__ == '__main__':
    data = {"item": [{"name": "Create User",
                      "request": {"method": "POST", "header": [{"key": "Content-Type", "value": "application/json"}],
                                  "body": {"mode": "raw",
                                           "raw": "{\"246e8418-b605-4c00-80db-bbe2c8867a32\": {\"create_time\": 1740556035, \"user_name\": \"Jeffrey Maldonado\", \"user_email\": \"bethany48@example.org\", \"user_age\": 10, \"user_status\": \"INACTIVE\"}}"},
                                  "url": "https://api.example.com/users"}}, {"name": "Create User",
                                                                             "request": {"method": "POST", "header": [
                                                                                 {"key": "Content-Type",
                                                                                  "value": "application/json"}],
                                                                                         "body": {"mode": "raw",
                                                                                                  "raw": "{\"c17045b2-0703-4118-8eeb-b7a7061c5ff7\": {\"create_time\": 1740731753, \"user_name\": \"Eric Howard\", \"user_email\": \"emilyholden@example.com\", \"user_age\": 18, \"user_status\": \"ACTIVE\"}}"},
                                                                                         "url": "https://api.example.com/users"}}],
            "info": {"name": "Simple Collection", "description": "This is a sample Postman collection"}}
    XMLExporter().export(data, "test.xml")
