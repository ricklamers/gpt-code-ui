.PHONY: all container_image container_run compile_frontend bundle_pypi upload_pypi increment_version release check_env_var

all: check_env_var build upload_pypi

build: check_env_var compile_frontend bundle_pypi

increment_version:
	@VERSION=$$(grep -e '^\s*version\s*=\s*"[^"]*"' pyproject.toml | cut -d '"' -f 2) && \
	MAJOR=$$(echo $$VERSION | cut -d. -f1) && \
	MINOR=$$(echo $$VERSION | cut -d. -f2) && \
	PATCH=$$(echo $$VERSION | cut -d. -f3) && \
	NEW_PATCH=$$((PATCH + 1)) && \
	NEW_VERSION="$$MAJOR.$$MINOR.$$NEW_PATCH" && \
	sed -i.bak "s/$$VERSION/$$NEW_VERSION/" pyproject.toml && \
	rm -f pyproject.toml.bak && \
	echo "Updated version to $$NEW_VERSION"


release:
	bash scripts/create_release.sh

compile_frontend:
	cd frontend && \
	npm install && \
	VITE_APP_VERSION=$$(grep -e '^\s*version\s*=\s*"[^"]*"' ../pyproject.toml | cut -d '"' -f 2) npm run build && \
	find ../gpt_code_ui/webapp/static -mindepth 1 ! -name '.gitignore' -delete && \
	rsync -av dist/ ../gpt_code_ui/webapp/static

container_image:
	podman build . --tag=gpt_code_ui

container_run:
	podman run \
		--env 'APP_SERVICE_CONFIG=$(shell cat .app_service_config.json)' \
		--env "FOUNDRY_DEV_TOOLS_FOUNDRY_URL=$(shell grep -e 'foundry_url' $$HOME/.foundry-dev-tools/config | cut -d '=' -f 2 | awk '{$$1=$$1;print}')" \
		--env "FOUNDRY_DEV_TOOLS_JWT=$(shell grep -e 'jwt' $$HOME/.foundry-dev-tools/config | cut -d '=' -f 2 | awk '{$$1=$$1;print}')" \
		-p=8080:8080/tcp \
		--name="GPT-Code-UI" \
		localhost/gpt_code_ui:latest

bundle_pypi:
	rm -rf dist build && \
	poetry build

upload_pypi: bundle_pypi
	poetry publish

check_env_var:
ifeq ($(VITE_WEB_ADDRESS),)
	@echo "VITE_WEB_ADDRESS not set, proceeding..."
else
	$(error "VITE_WEB_ADDRESS is set, aborting...")
endif
