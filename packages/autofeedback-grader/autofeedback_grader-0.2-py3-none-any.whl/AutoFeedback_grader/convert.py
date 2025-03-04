import json

def generateAnswersJSON(fname):
    import jupytext
    nb = jupytext.read(fname)
    return json.loads(jupytext.writes(nb,fmt='ipynb'))

#def generateNBnode(contents):
#    return jupytext.writes(contents, fmt='ipynb')

def execute(contents):
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor
    nb_in = nbformat.reads(json.dumps(contents), as_version=4)
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    return ep.preprocess(nb_in)[0]
        

contents = generateAnswersJSON('answers.py')

postrun = execute(contents)
