.PHONY: all compile_frontend bundle_pypi upload_pypi

# Extract version from setup.py file
VERSION := $(shell sed -n "s/^.*version='\([^']*\)'.*$$/\1/p" setup.py)

all: build upload_pypi

build: compile_frontend bundle_pypi

setenv:
    export VITE_APP_VERSION=${VERSION}
	
compile_frontend:
	cd frontend && \
	npm install && \
	npm run build && \
	rsync -av dist/ ../gpt_code_ui/webapp/static

bundle_pypi:
	python setup.py sdist bdist_wheel

upload_pypi:
	twine upload dist/*
