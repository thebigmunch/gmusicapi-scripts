# coding=utf-8

"""Useful task commands for development and maintenance."""

from invoke import run, task


@task
def clean():
	"""Clean the project directory of unwanted files and directories."""

	run('rm -rf gmusicapi_scripts.egg-info')
	run('rm -rf .coverage')
	run('rm -rf .tox')
	run('rm -rf .cache')
	run('rm -rf build/')
	run('rm -rf dist/')
	run('rm -rf site/')
	run('find . -name *.pyc -delete')
	run('find . -name *.pyo -delete')
	run('find . -name __pycache__ -delete -depth')
	run('find . -name *~ -delete')


@task(clean)
def build():
	"""Build sdist and bdist_wheel distributions."""

	run('python setup.py sdist bdist_wheel')


@task(build)
def deploy():
	"""Build and upload gmusicapi_scripts distributions."""

	upload()


@task
def docs(test=False):
	""""Build the gmusicapi_scripts docs."""

	if test:
		run('mkdocs serve')
	else:
		run('mkdocs gh-deploy --clean')


@task
def upload():
	"""Upload gmusicapi_scripts distributions using twine."""

	run('twine upload dist/*')
