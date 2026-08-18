import json

#File handling functions
#return the text of a file
def returnfiletext(path, encoding='utf-8'):
    with open(path, 'r', encoding=encoding) as file:
        return file.read()

#write text to a file
def writefiletext(path, text, encoding='utf-8'):
    with open(path, 'w', encoding=encoding) as file:
        file.write(text)

#convert a python object to a json file
def write_python_object_to_json_file(oby):
    text = json.dumps(oby)
    with open("database.txt", "w", encoding="utf-8") as f:
        f.seek(0)
        f.write(text)