import re


def parse_avron(file_path):
  with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

  root = {}
  context_stack = [(root, -1)]
  multi_line_string = None
  last_key = None
  in_multi_line_comment = False

  for line in lines:
    line = line.rstrip()

    if not line.strip():
      continue

    if line.strip().startswith("###"):
      in_multi_line_comment = not in_multi_line_comment
      continue
    if in_multi_line_comment or line.strip().startswith("#"):
      continue

    if '"""' in line:
      if multi_line_string is None:
        multi_line_string = []
        continue
      else:
        value = "\n".join(multi_line_string).strip()
        current_obj, _ = context_stack[-1]
        current_obj[last_key] = value
        multi_line_string = None
        continue

    if multi_line_string is not None:
      multi_line_string.append(line)
      continue

    indent = len(line) - len(line.lstrip())
    stripped = line.strip()

    if ":" in stripped and not stripped.startswith("-"):
      key, value = map(str.strip, stripped.split(":", 1))
      last_key = key

      while context_stack and indent <= context_stack[-1][1]:
        context_stack.pop()

      current_obj, _ = context_stack[-1]

      if not value:
        new_obj = {}
        current_obj[key] = new_obj
        context_stack.append((new_obj, indent))
        continue

      if value.lower() == "true":
        value = True
      elif value.lower() == "false":
        value = False
      elif value.lower() == "null":
        value = None
      elif re.match(r'^-?\d+(\.\d+)?$', value):
        value = float(value) if "." in value else int(value)
      elif value.startswith("[") and value.endswith("]"):
        value = parse_inline_list(value[1:-1])
      elif value.startswith("{") and value.endswith("}"):
        value = parse_inline_object(value[1:-1])

      current_obj[key] = value

    elif stripped.startswith("-"):
      value = stripped[1:].strip()

      if value.lower() == "true":
        value = True
      elif value.lower() == "false":
        value = False
      elif value.lower() == "null":
        value = None
      elif re.match(r'^-?\d+(\.\d+)?$', value):
        value = float(value) if "." in value else int(value)

      current_obj, _ = context_stack[-1]

      if last_key not in current_obj:
        current_obj[last_key] = []
      elif not isinstance(current_obj[last_key], list):
        current_obj[last_key] = [current_obj[last_key]]

      current_obj[last_key].append(value)

  return root


def parse_inline_list(text):
  """Parse an inline list like [item1, item2, item3]"""
  items = []
  for item in text.split(","):
    item = item.strip()
    if not item:
      continue

    if item.lower() == "true":
      items.append(True)
    elif item.lower() == "false":
      items.append(False)
    elif item.lower() == "null":
      items.append(None)
    elif re.match(r'^-?\d+(\.\d+)?$', item):
      items.append(float(item) if "." in item else int(item))
    else:
      items.append(item)

  return items


def parse_inline_object(text):
  """Parse an inline object like {key1: value1, key2: value2}"""
  obj = {}
  for item in text.split(","):
    if ":" not in item:
      continue

    key, value = map(str.strip, item.split(":", 1))

    if value.lower() == "true":
      obj[key] = True
    elif value.lower() == "false":
      obj[key] = False
    elif value.lower() == "null":
      obj[key] = None
    elif re.match(r'^-?\d+(\.\d+)?$', value):
      obj[key] = float(value) if "." in value else int(value)
    else:
      obj[key] = value

  return obj
