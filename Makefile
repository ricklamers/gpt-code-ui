.PHONY: all compile_frontend bundle_pypi upload_pypi

all: compile_frontend bundle_pypi upload_pypi

compile_frontend:
	cd frontend && \
	npm install && \
	npm run build && \
	rsync -av dist/ ../gpt_code/webapp/static

bundle_pypi:
	python setup.py sdist bdist_wheel

upload_pypi:
	twine upload dist/*
