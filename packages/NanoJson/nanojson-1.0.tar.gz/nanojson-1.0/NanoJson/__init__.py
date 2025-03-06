import json, os

class JsonHelper:
  def __init__(self, path, indent=2):
    self.path = path
    self.indent = indent
    self._ensure_file_exists()

  def _ensure_file_exists(self):
    """يتأكد من أن الملف موجود، وإذا لم يكن، ينشئ ملف JSON فارغ."""
    if not os.path.exists(self.path):
      self.write_json({})

  def read_json(self, pretty=False):
    """يقرأ بيانات JSON من الملف، مع إمكانية طباعتها بشكل جميل."""
    try:
      with open(self.path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return json.dumps(data, indent=self.indent, ensure_ascii=False) if pretty else data
    except (FileNotFoundError, json.JSONDecodeError):
      return None

  def write_json(self, data):
    """يكتب بيانات JSON إلى الملف."""
    try:
      with open(self.path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=self.indent, ensure_ascii=False)
      return True
    except Exception:
      return False

  def update_json(self, key, value):
    """يحدّث أو يضيف مفتاحًا جديدًا داخل JSON."""
    data = self.read_json()
    if isinstance(data, dict):
      data[key] = value
      return self.write_json(data)
    return False

  def delete_key(self, key):
    """يحذف مفتاحًا من JSON."""
    data = self.read_json()
    if isinstance(data, dict) and key in data:
      del data[key]
      return self.write_json(data)
    return False

  def search_key(self, key):
    """يبحث عن مفتاح داخل JSON ويعيد قيمته."""
    data = self.read_json()
    return data.get(key) if isinstance(data, dict) else None

  def append_to_list(self, key, value):
    """يضيف عنصرًا إلى قائمة موجودة داخل JSON."""
    data = self.read_json()
    if isinstance(data, dict):
      if key not in data:
        data[key] = []
      if isinstance(data[key], list):
        data[key].append(value)
        return self.write_json(data)
    return False

  def remove_from_list(self, key, value):
    """يحذف عنصرًا من قائمة داخل JSON."""
    data = self.read_json()
    if isinstance(data, dict) and key in data and isinstance(data[key], list):
      if value in data[key]:
        data[key].remove(value)
        return self.write_json(data)
    return False

  def deep_search(self, key, data=None):
    """يبحث عن مفتاح داخل JSON، حتى لو كان متداخلًا."""
    if data is None:
      data = self.read_json()
    if isinstance(data, dict):
      if key in data:
        return data[key]
      for sub_key in data:
        result = self.deep_search(key, data[sub_key])
        if result is not None:
          return result
    elif isinstance(data, list):
      for item in data:
        result = self.deep_search(key, item)
        if result is not None:
          return result
    return None

  def merge_json(self, new_data):
    """يدمج JSON الحالي مع بيانات جديدة."""
    data = self.read_json()
    if isinstance(data, dict) and isinstance(new_data, dict):
      data.update(new_data)
      return self.write_json(data)
    return False

  def clear_json(self):
    """يمسح جميع البيانات داخل JSON."""
    return self.write_json({})