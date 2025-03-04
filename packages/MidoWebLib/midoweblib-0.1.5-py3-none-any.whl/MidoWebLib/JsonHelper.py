import json
import os

class JsonHelper:
  def __init__(self, path, indent=2):
    self.path = path
    self.indent = indent
    self._ensure_file_exists()

  def _ensure_file_exists(self):
    """يتأكد من أن الملف موجود، وإن لم يكن، ينشئ ملف JSON فارغ."""
    if not os.path.exists(self.path):
      self.write_json({})

  def read_json(self, pretty=False):
    """يقرأ بيانات JSON من الملف، مع إمكانية طباعتها بشكل جميل."""
    try:
      with open(self.path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return json.dumps(data, indent=2, ensure_ascii=False) if pretty else data
    except FileNotFoundError:
      return "Error: File not found."
    except json.JSONDecodeError:
      return "Error: Invalid JSON format."

  def write_json(self, data):
    """يكتب بيانات JSON إلى الملف."""
    try:
      with open(self.path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
      return "JSON file updated successfully."
    except Exception as e:
      return f"Error: {e}"

  def update_json(self, key, value):
    """يحدّث قيمة مفتاح معين داخل JSON."""
    data = self.read_json()
    if isinstance(data, dict):
      data[key] = value
      return self.write_json(data)
    return "Error: JSON is not a dictionary."

  def delete_key(self, key):
    """يحذف مفتاحًا من JSON."""
    data = self.read_json()
    if isinstance(data, dict) and key in data:
      del data[key]
      return self.write_json(data)
    return "Error: Key not found or JSON is not a dictionary."

  def search_key(self, key):
    """يبحث عن مفتاح داخل JSON ويعيد قيمته."""
    data = self.read_json()
    return data.get(key, "Error: Key not found.") if isinstance(data, dict) else "Error: JSON is not a dictionary."

  def append_to_list(self, key, value):
    """يضيف عنصرًا إلى قائمة موجودة داخل JSON."""
    data = self.read_json()
    if isinstance(data, dict):
      if key not in data:
        data[key] = []
      if isinstance(data[key], list):
        data[key].append(value)
        return self.write_json(data)
      return "Error: The key does not contain a list."
    return "Error: JSON is not a dictionary."

  def remove_from_list(self, key, value):
    """يحذف عنصرًا من قائمة داخل JSON."""
    data = self.read_json()
    if isinstance(data, dict) and key in data and isinstance(data[key], list):
      if value in data[key]:
        data[key].remove(value)
        return self.write_json(data)
      return "Error: Value not found in the list."
    return "Error: Key not found or is not a list."

# مثال على الاستخدام
helper = JsonHelper("data.json")

# قراءة JSON
print(helper.read_json(pretty=True))

# تحديث قيمة مفتاح
print(helper.update_json("name", "محمد"))

# إضافة عنصر إلى قائمة
print(helper.append_to_list("hobbies", "البرمجة"))

# حذف عنصر من قائمة
print(helper.remove_from_list("hobbies", "البرمجة"))

# البحث عن مفتاح
print(helper.search_key("name"))

# حذف مفتاح
print(helper.delete_key("name"))