############################################################
##                      INSTALLATION                      ##
## ------------------------------------------------------ ##
## pip install pyperclip                                  ##
############################################################
############################################################
##                         README                         ##
## ------------------------------------------------------ ##
## Dieses Skript liest Inhalte von Dateien und            ##
## Verzeichnissen aus, formatiert sie und kopiert die     ##
## Ausgabe in die Zwischenablage.                         ##
##                                                        ##
## AUSFÜHRUNG:                                            ##
## 1. Mit Parametern:                                     ##
##    python copy4chatGPT.py VERZEICHNIS/DATEI_PFAD [OPTIONALE_DATEI_1] ... [OPTIONALE_DATEI_N]  ##
##                                                        ##
## 2. Interaktiv:                                         ##
##    python copy4chatGPT.py                              ##
##    Gib die Pfade ein (Verzeichnisse und Dateien),      ##
##    getrennt durch Leerzeichen.                         ##
############################################################

import os
import sys
import pyperclip

def get_files_content(paths):
    """
    Reads content from files and directories and formats it in a readable way.
    """
    output = []
    for path in paths:
        if os.path.isfile(path):
            # Add a specific file to the output
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                output.append(f"FILE: {os.path.basename(path)}\nCONTENT:\n{content}\n{'-' * 40}\n")
            except Exception as e:
                output.append(f"FILE: {path}\nCONTENT:\n<Error reading file: {e}>\n{'-' * 40}\n")
        elif os.path.isdir(path):
            # Traverse all files in the directory (and subdirectories)
            for root, _, dir_files in os.walk(path):
                for file in dir_files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        relative_path = os.path.relpath(file_path, path)
                        output.append(f"FILE: {relative_path}\nCONTENT:\n{content}\n{'-' * 40}\n")
                    except Exception as e:
                        output.append(f"FILE: {file_path}\nCONTENT:\n<Error reading file: {e}>\n{'-' * 40}\n")
        else:
            output.append(f"FILE: {path}\nCONTENT:\n<Error: Not a valid file or directory>\n{'-' * 40}\n")

    return "\n".join(output)

def main():
    # 1. Sammle Eingaben (Parameter-Modus oder interaktiver Modus)
    if len(sys.argv) > 1:
        # Parameter-Modus
        paths_to_process = sys.argv[1:]
    else:
        # Interaktiver Modus
        print("Gib deine Datei, dein Verzeichnis oder dein Verzeichnis mit Dateien ein. Schema: VERZEICHNIS/DATEI_PFAD [OPTIONALE_DATEI_1] ... [OPTIONALE_DATEI_N] ")
        input_paths = input("Eingabe: ").strip().split()
        paths_to_process = [path.strip() for path in input_paths]

    # 2. Überprüfe, ob die Pfade existieren
    valid_paths = [path for path in paths_to_process if os.path.exists(path)]
    if not valid_paths:
        print("Keine gültigen Dateien oder Verzeichnisse angegeben.")
        return

    # 3. Inhalte sammeln und kopieren
    print("Inhalte werden gesammelt...")
    files_content = get_files_content(valid_paths)

    print("Inhalte in die Zwischenablage kopieren...")
    pyperclip.copy(files_content)

    print("Die Inhalte wurden in die Zwischenablage kopiert! Du kannst sie jetzt einfügen.")

if __name__ == "__main__":
    main()
