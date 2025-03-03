import yaml

from pistol_magazine.data_exporter.exporter import Exporter


class YAMLExporter(Exporter):
    def export(self, data, filename):
        with open(filename, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
