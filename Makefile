# Reef test project Makefile
#
# Requirements:
# - GNU Make or [Remake](https://bashdb.sourceforge.net/remake/)
# - Bash >= 4.1
# - sed
# - Python 3.11
#   - [validate-pyproject](https://validate-pyproject.readthedocs.io/en/latest/)
#   - [pip-tools](https://pip-tools.readthedocs.io/en/latest/)
# - Git
# - Docker
# - [hadolint](https://github.com/hadolint/hadolint)
# - [container-diff](https://github.com/GoogleContainerTools/container-diff)
# - [jq](https://stedolan.github.io/jq/)
# - [yq](https://mikefarah.gitbook.io/yq/)

SHELL := /bin/bash
XDG_DATA_HOME ?= $(HOME)/.local/share

# Project metadata
PROJECT_NAME := activities
PROJECT_VERSION := 0.1.0
PYTHON_VERSION := 3.11

# Python virtual environment
PYTHON := python$(PYTHON_VERSION)
PIP_COMPILE := pip-compile --quiet --resolver=backtracking --allow-unsafe
VENV ?= $(XDG_DATA_HOME)/venv/$(PROJECT_NAME)
ACTIVATE := . '$(VENV)/bin/activate'

# Docker and Compose commands
HADOLINT := $(if $(shell type -t hadolint),,docker run --rm -i -v '$(PWD):/src' -w '/src' ghcr.io/hadolint/hadolint )hadolint
BASE_IMAGE_TAG != sed -En '/ as app$$/s/^FROM +([^ ]+) +as +app$$/\1/p' Dockerfile
IMAGE_TAG := $(PROJECT_NAME):$(PROJECT_VERSION)
DIFF_FILE := $(PROJECT_NAME)-image.diff

# Docker image labels
now != date -u '+%Y-%m-%dT%T%z'
define labels :=
org.opencontainers.image.created='$(now)'
$(if $(IMAGE_REVISION),org.opencontainers.image.revision='$(IMAGE_REVISION)')
$(if $(IMAGE_SOURCE),org.opencontainers.image.source='$(IMAGE_SOURCE)')
$(if $(IMAGE_URL),org.opencontainers.image.url='$(IMAGE_URL)')
endef

# Targets
targets_lint   := $(addprefix lint-,pyproject yaml py docker)
targets_update := lf $(addprefix update-,version-python packages)
targets_docker := build image diff
targets_clean  := $(addprefix clean-,requirements requirements-dev venv image diff)

.PHONY: all venv touch-venv lint $(targets_lint) $(targets_update) $(targets_docker) $(targets_db) $(targets_clean)

#: Default target: build Docker image
all: build

#: Create Python virtual environment
venv: $(VENV)
requirements.txt requirements-dev.txt: pyproject.toml
	@$(PIP_COMPILE) $(PIP_COMPILE_FLAGS) --output-file='$@' '$<'
requirements.txt: PIP_COMPILE_FLAGS =
requirements-dev.txt: PIP_COMPILE_FLAGS = --extra=dev
$(VENV): requirements-dev.txt
	@$(PYTHON) -m venv '$@' && $(ACTIVATE) && \
	pip install --upgrade pip setuptools && \
	pip install --requirement='$<' && \
	touch '$@'
touch-venv:
	@if [[ -d '$(VENV)' ]]; then touch '$(VENV)'; fi

#: Replace line endings in all text files (CRLF with LF)
lf:
	@git ls-files --cached --others --exclude-per-directory=.gitignore -z | xargs -0 dos2unix

#: Update Python version
update-version-python: Makefile
	@sed -Ei '/Programming Language :: Python|requires-python/s/[0-9]+(\.[0-9]+)*/$(PYTHON_VERSION)/' pyproject.toml && \
	sed -Ei '/target-version/s/py[0-9]+/py$(subst .,,$(PYTHON_VERSION))/' pyproject.toml && \
	sed -Ei '/^FROM/s/[0-9]+(\.[0-9]+)*/$(PYTHON_VERSION)/' Dockerfile

#: Update all Python packages in the virtual environment
update-packages: | $(VENV)
	@$(ACTIVATE) && pip list --outdated --format=json | jq '.[].name' | xargs --max-args=1 pip install --upgrade

#: Lint everything
lint: $(targets_lint)

#: Lint pyproject.toml
lint-pyproject: pyproject.toml | $(VENV)
	@validate-pyproject '$<'

#: Lint all YAML files
lint-yaml: | $(VENV)
	@yamllint .

#: Lint Python code
lint-py: | $(VENV)
	@ruff .

#: Lint Dockerfile
lint-docker: Dockerfile
	@$(HADOLINT) '$<'

#: Build Docker image
build image: Dockerfile requirements.txt lint
	@docker build --progress plain \
		$(if $(no_cache), --no-cache)$(if $(no_pull),, --pull) \
		$(addprefix --build-arg=,$(build_args)) \
		$(addprefix --tag=,$(tags)) \
		$(addprefix --label=,$(labels)) .

#: Compare built Docker image to the base image
diff: $(DIFF_FILE)
$(DIFF_FILE):
	@docker pull '$(BASE_IMAGE_TAG)' && \
	container-diff diff 'daemon://$(BASE_IMAGE_TAG)' 'daemon://$(IMAGE_TAG)' --type=file --type=size > '$@'

# Cleaning
clean-requirements:
	@-rm -rf requirements.txt
clean-requirements-dev:
	@-rm -rf requirements-dev.txt
clean-venv:
	@-rm -rf '$(VENV)'
clean-image:
	@-docker image rm '$(IMAGE_TAG)'
clean-diff:
	@-rm -fv '$(DIFF_FILE)'
