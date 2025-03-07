# AVRON Parser

**AVRON (A Very Readable Object Notation)** is a human-friendly data format that is also easy for machines to parse.  
This package provides a parser for AVRON, allowing you to read AVRON files and convert them into Python objects.

---

## Features
- **Simple, indentation-based syntax** (like YAML but better for machines)
- **Supports nested objects, lists, and inline data**
- **Multi-line strings and comments**
- **Boolean, numeric, and null values auto-detected**

---

## Usage
### **Parse an AVRON File**
```python
from avron_parser import parse_avron

parsed_data = parse_avron("example.avron")
print(parsed_data)
```

### **Example AVRON File (`example.avron`)**
```
title: "AVRON Example"
version: 1.0
author: "Kohan Mathers"

# Supports comments
description: """
  AVRON is a structured, human-readable format.
  It is simpler than YAML but more machine-friendly.
"""

settings:
  display:
    resolution:
      width: 1920
      height: 1080
    fullscreen: true

features:
  - "Simple syntax"
  - 100
  - true
  - null

metadata: { created_by: "QTI", last_updated: "2025-03-06" }
```

### **Accessing Specific Data**
```python
print(parsed_data["title"])
print(parsed_data["settings"]["display"]["resolution"]["width"])
```

---

## Development
### **Clone the Repository**
```sh
git clone https://github.com/kohanmathers/avron-parser.git
cd avron-parser
```
---

## License
This project is licensed under the **MIT License**.

---

## Contributing
1. Fork the repository
2. Create a new branch (`feature-name`)
3. Commit changes (`git commit -m "Added new feature"`)
4. Push to your branch (`git push origin feature-name`)
5. Open a pull request

---

- **GitHub:** [https://github.com/kohanmathers/avron-parser](https://github.com/kohanmathers/avron-parser)