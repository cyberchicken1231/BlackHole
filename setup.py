from setuptools import setup

APP = ['Black_Hole.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pygame'],
    'includes': ['jaraco.text'],  # add the missing module here
}

setup(
    app=['Black_Hole.py'],
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
