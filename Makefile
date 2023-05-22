.PHONY: all compile_frontend bundle_pypi upload_pypi increment_version release check_env_var

# Extract version from setup.py file
VERSION := $(shell grep -oP "(?<=version=')[^']*" setup.py)

all: check_env_var build upload_pypi

build: check_env_var compile_frontend bundle_pypi

setenv:
    export VITE_APP_VERSION=${VERSION}

increment_version:
	@VERSION=$$(grep -oP "(?<=version=')[^']*" setup.py) && \
	MAJOR=$$(echo $$VERSION | cut -d. -f1) && \
	MINOR=$$(echo $$VERSION | cut -d. -f2) && \
	PATCH=$$(echo $$VERSION | cut -d. -f3) && \
	NEW_PATCH=$$((PATCH + 1)) && \
	NEW_VERSION="$$MAJOR.$$MINOR.$$NEW_PATCH" && \
	sed -i "s/version='.*'/version='$$NEW_VERSION'/" setup.py && \
	echo "Updated version to $$NEW_VERSION"

release:
	bash scripts/create_release.sh

compile_frontend:
	cd frontend && \
	npm install && \
	npm run build && \
	find ../gpt_code_ui/webapp/static -mindepth 1 ! -name '.gitignore' -delete && \
	rsync -av dist/ ../gpt_code_ui/webapp/static

bundle_pypi:
	rm -rf dist build && \
	python3 setup.py sdist bdist_wheel

upload_pypi:
	twine upload dist/*

check_env_var:
ifeq ($(VITE_WEB_ADDRESS),)
	@echo "VITE_WEB_ADDRESS not set, proceeding..."
else
	$(error "VITE_WEB_ADDRESS is set, aborting...")
endif
