# coding=utf-8

"""Useful task commands for development and maintenance."""

import glob
import os
import shutil

from invoke import run, task

to_remove_dirnames = ['**/__pycache__', '.cache', '.tox', 'build', 'dist', 'gmusicapi_scripts.egg-info']
to_remove_filenames = ['**/*.pyc', '**/*.pyo', '.coverage']


@task
def clean():
	"""Clean the project directory of unwanted files and directories."""

	to_remove_dirs = [
		path for dirname in to_remove_dirnames for path in glob.glob(dirname) if os.path.isdir(path)
	]

	for dirpath in to_remove_dirs:
		shutil.rmtree(dirpath)

	to_remove_files = [
		path for filename in to_remove_filenames for path in glob.glob(filename) if os.path.isfile(path)
	]

	for filepath in to_remove_files:
		os.remove(filepath)


@task(clean)
def build():
	"""Build sdist and bdist_wheel distributions."""

	run('python setup.py sdist bdist_wheel')


@task(build)
def publish():
	"""Build and upload gmusicapi_scripts distributions."""

	upload()


@task
def upload():
	"""Upload gmusicapi_scripts distributions using twine."""

	run('twine upload dist/*')


@task
def docs(test=False):
	""""Build the gmusicapi_scripts docs."""

	if test:
		run('mkdocs serve')
	else:
		run('mkdocs gh-deploy --clean')
