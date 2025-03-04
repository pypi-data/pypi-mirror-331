import json
import sys

def UID():
    """generate a unique 10 digit ID for directory naming"""
    import random
    import string
    digits = string.digits + string.ascii_letters
    return (''.join(random.choice(digits) for i in range(12)))

fname = sys.argv[-1]

with open(fname, 'r') as f:
    template = json.load(f)

for cell in template["cells"]:
    if not cell["metadata"]:
        cell["metadata"]["id"] = UID()
    cell["outputs"] = []


print(json.dumps(template, indent=2))
