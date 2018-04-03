import hashlib
import json
import ast
import gzip
import pickle
import re

PICKLE_PATH = './processed.pickle'

CONTENT_BLACKLIST = {  # Strings that hint us that this file is not necessary to be read
    "url='http://babel.pocoo.org/'",  # New Babel distro
    'http://babel.edgewall.org/wiki/License',  # Old Babel distro
    'openbabel-discuss',  # OpenBabel, not us
    'Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).',  # Old copy of Odoo
}

STRING_BLACKLIST = {  # Substrings that make a string not look like a babel version spec
    ' ',
    '.cfg',  # Filename
    '.extractors',  # Refers to the subpackage
    '.ini',  # Filename
    '/',
    'babel-vue-extractor',  # Not us!
    'babel_',  # Probably a command
    'babeldjango',  # Not us!
    'babelfish',  # Not us!
}


def smells_babely(s):
    s = s.lower()
    return s.startswith('babel') and not any(c in s for c in STRING_BLACKLIST)


class BabelStringVisitor(ast.NodeVisitor):
    def __init__(self):
        self.matches = []
        self.stack = []

    def visit(self, node):
        self.stack.append(node)
        super(BabelStringVisitor, self).visit(node)
        assert self.stack.pop(-1) is node

    def visit_Str(self, node):
        if node.s == 'babel':
            # Hack: avoid false positives from Odoo files like
            #       https://github.com/odoo/odoo/blob/f1a884e046dda1593fc4baeeeb9b27bd668936db/setup.py#L27
            if any(getattr(node, 'name', None) == 'py2exe_datafiles' for node in self.stack):
                return
        if smells_babely(node.s):
            self.matches.append(node.s)


def extract_from_setup_py(filename, content):
    # Ugly Py2 fixup...
    content = re.sub(r'\bprint (.+)', lambda m: 'print(%s)' % m.group(1).replace('>>', ''), content)
    tree = ast.parse(content, filename=filename)
    visitor = BabelStringVisitor()
    visitor.visit(tree)
    return visitor.matches


def process_datum(datum):
    datum = json.loads(datum)
    content = datum['content']
    repo_name = datum['repo_name']
    path = datum['path']
    repo_and_path = '%s:%s' % (repo_name, path)

    if any(blacklisted_content in content for blacklisted_content in CONTENT_BLACKLIST):
        return

    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

    if path.endswith('.txt'):
        for line in content.splitlines():
            if smells_babely(line):
                clean_line = line.split(None, 1)[0].lower()
                yield dict(path=repo_and_path, hash=content_hash, spec=clean_line)
    elif path.endswith('.py'):
        try:
            for spec in extract_from_setup_py(repo_and_path, content):
                yield dict(path=repo_and_path, hash=content_hash, spec=spec.lower())
        except SyntaxError:
            return


def generate_pickle():
    out_data = []
    with gzip.open('./contents-with-babel.json.gz', 'r') as infp:
        rows = list(infp)
    print('Analyzing %d files' % len(rows))

    for datum in rows:
        out_data.extend(process_datum(datum))
    print('Dumping pickle')
    with open(PICKLE_PATH, 'wb') as outfp:
        pickle.dump(out_data, outfp, protocol=pickle.HIGHEST_PROTOCOL)
    print('Done')


def read_pickle():
    with open(PICKLE_PATH, 'rb') as infp:
        return pickle.load(infp)


if __name__ == '__main__':
    generate_pickle()
