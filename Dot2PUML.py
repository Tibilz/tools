import sys
import re

class Package:
    def __init__(self, name, depth=0):
        self.name = name
        self.subpackages = {}
        self.classes = []
        self.depth = depth  # Tiefe des Pakets für Farbzuweisung

    def add_class(self, package_path, class_info):
        parts = package_path.split('.')
        if len(parts) == 0 or parts[0] == '':
            self.classes.append(class_info)
            return
        first, *rest = parts
        if first not in self.subpackages:
            self.subpackages[first] = Package(first, self.depth + 1)
        self.subpackages[first].add_class('.'.join(rest), class_info)

    def get_color(self):
        """
        Generiert eine Farbe basierend auf der Tiefe des Pakets.
        Äußere Pakete haben dunkleres Blau, innere Pakete helleres Blau.
        """
        # Basisfarbton für Blau in HSL (Hue=220°)
        hue = 220
        saturation = 50  # 50%
        # Berechnung der Helligkeit basierend auf der Tiefe
        # Start mit 30% Helligkeit, zunimmt um 20% pro Tiefe, max 80%
        lightness = min(30 + (self.depth * 20), 80)

        # Konvertiere HSL zu RGB
        c = (1 - abs(2 * lightness / 100 - 1)) * (saturation / 100)
        x = c * (1 - abs((hue / 60) % 2 - 1))
        m = lightness / 100 - c / 2

        if 0 <= hue < 60:
            r1, g1, b1 = c, x, 0
        elif 60 <= hue < 120:
            r1, g1, b1 = x, c, 0
        elif 120 <= hue < 180:
            r1, g1, b1 = 0, c, x
        elif 180 <= hue < 240:
            r1, g1, b1 = 0, x, c
        elif 240 <= hue < 300:
            r1, g1, b1 = x, 0, c
        else:
            r1, g1, b1 = c, 0, x

        r = int((r1 + m) * 255)
        g = int((g1 + m) * 255)
        b = int((b1 + m) * 255)

        return f'#{r:02X}{g:02X}{b:02X}'


    def to_puml(self, puml, indent=0):
        """
        Generiert die PlantUML-Repräsentation dieses Pakets und seiner Unterpakete.
        """
        indent_str = '  ' * indent
        if self.name != "Root":  # Root-Paket nicht anzeigen
            color = self.get_color()
            puml.append(f'{indent_str}package "{self.name}" {{')
            puml.append(f'{indent_str}  skinparam packageBackgroundColor {color}')
            puml.append(f'{indent_str}  skinparam packageBorderColor Black')  # Optional: Setzt die Randfarbe
        else:
            puml.append(f'{indent_str}package "Root" {{')  # Optional: Kann angepasst werden
    
        # Rekursiv durch alle Unterpakete
        for subpackage in self.subpackages.values():
            subpackage.to_puml(puml, indent + 1)
    
        # Füge Klassen dieses Pakets hinzu
        for node_id, class_info in self.classes:
            class_name = class_info['name']
            alias = node_id.replace('.', '_')
            puml.append(f'{indent_str}  class "{class_name}" as {alias} {{')
            for attr in class_info['attributes']:
                puml.append(f'{indent_str}    {attr}')
            for method in class_info['methods']:
                puml.append(f'{indent_str}    {method}')
            puml.append(f'{indent_str}  }}')
    
        # Schließe das Paket
        puml.append(f'{indent_str}}}')


def dot_classes_to_puml(dot_file, puml_file):
    try:
        with open(dot_file, 'r', encoding='utf-8') as infile:
            dot_content = infile.read()

        # Kommentare entfernen
        dot_content = re.sub(r'//.*', '', dot_content)
        dot_content = re.sub(r'/\*.*?\*/', '', dot_content, flags=re.DOTALL)

        # Muster für Knoten und Kanten
        node_pattern = re.compile(r'"(?P<id>[^"]+)"\s+\[.*?label=<\{(?P<label>.*?)\}>.*?\];', re.DOTALL)
        edge_pattern = re.compile(r'"(?P<from>[^"]+)"\s*->\s*"(?P<to>[^"]+)"\s*\[.*?label="(?P<label>[^"]*)".*?\];')

        classes = {}
        edges = []

        # Knoten verarbeiten (Klassen)
        for node_match in node_pattern.finditer(dot_content):
            node_id = node_match.group('id')
            label_content = node_match.group('label')

            # HTML-Entities dekodieren
            label_content = label_content.replace('<br ALIGN="LEFT"/>', '\n')
            label_content = re.sub(r'<.*?>', '', label_content)

            # Label teilen
            label_parts = label_content.split('|')
            class_name = label_parts[0].strip()
            attributes = []
            methods = []
            if len(label_parts) > 1:
                for part in label_parts[1:]:
                    part = part.strip()
                    if not part:
                        continue
                    lines = part.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        if ':' in line and '(' not in line:
                            attributes.append(line)
                        else:
                            # Entferne die Rückgabewerte in den Methoden
                            method = re.sub(r":\s*'([^']*)'", r": \1", line)
                            methods.append(method)
            classes[node_id] = {
                'name': class_name,
                'attributes': attributes,
                'methods': methods
            }

        # Kanten verarbeiten (Beziehungen)
        for edge_match in edge_pattern.finditer(dot_content):
            from_node = edge_match.group('from')
            to_node = edge_match.group('to')
            label = edge_match.group('label')
            edges.append({
                'from': from_node,
                'to': to_node,
                'label': label
            })

        # Pakete erstellen basierend auf dem Namespace
        root_package = Package("Root")  # Ein oberstes Wurzelpaket
        for node_id, class_info in classes.items():
            if '.' in node_id:
                package_name = '.'.join(node_id.split('.')[:-1])
            else:
                package_name = 'Global'
            root_package.add_class(package_name, (node_id, class_info))

        # PlantUML-Code generieren
        puml_lines = []
        puml_lines.append('@startuml')
        puml_lines.append('skinparam classAttributeIconSize 0')
        puml_lines.append('left to right direction')
        puml_lines.append('skinparam shadowing true')
        puml_lines.append('skinparam packageStyle rect')
        puml_lines.append('skinparam class {')
        puml_lines.append('  BackgroundColor LightYellow')
        puml_lines.append('  ArrowColor DarkBlue')
        puml_lines.append('  BorderColor Black')
        puml_lines.append('  FontName Arial')
        puml_lines.append('  FontSize 12')
        puml_lines.append('}')
        puml_lines.append('skinparam package {')
        puml_lines.append('  BackgroundColor LightSteelBlue')  # Basisfarbe, überschrieben von Paketen
        puml_lines.append('  FontName Arial')
        puml_lines.append('}')
        puml_lines.append('skinparam arrow {')
        puml_lines.append('  Color DarkBlue')
        puml_lines.append('}')
        puml_lines.append('set namespaceSeparator none')

        # Füge die Pakete und Klassen hinzu
        # Überspringe das Root-Paket und beginne direkt mit den Unterpaketen
        for package in root_package.subpackages.values():
            package.to_puml(puml_lines, indent=0)

        # Beziehungen hinzufügen
        for edge in edges:
            from_alias = edge['from'].replace('.', '_')
            to_alias = edge['to'].replace('.', '_')
            label = edge['label']
            puml_lines.append(f'{from_alias} --> {to_alias} : {label}')

        puml_lines.append('@enduml')

        # In die Ausgabedatei schreiben
        with open(puml_file, 'w', encoding='utf-8') as outfile:
            outfile.write('\n'.join(puml_lines))

    except Exception as e:
        print(f"Fehler beim Verarbeiten der Datei: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Verwendung: python dot_classes_to_puml.py <eingabe.dot> <ausgabe.puml>")
    else:
        dot_file = sys.argv[1]
        puml_file = sys.argv[2]
        dot_classes_to_puml(dot_file, puml_file)
