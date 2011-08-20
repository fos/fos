import os

def get_font( name ):
    return os.path.join(os.path.dirname(__file__), 'font', name + '.tff')
