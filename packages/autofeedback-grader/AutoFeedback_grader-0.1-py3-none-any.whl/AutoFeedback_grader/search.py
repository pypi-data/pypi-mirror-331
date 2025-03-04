import json


def extractCodeCellIDs(ipynbFile):
    with open(ipynbFile, 'r') as f:
        contents = json.load(f)

    targetCells = []
    for ii, cell in enumerate(contents["cells"]):
        if cell["cell_type"] == "code":
            if any([v for v in cell["source"] if v.startswith("runtest(")]):
                targetCells.append(contents["cells"][ii-1]["metadata"]["id"])
    return targetCells
