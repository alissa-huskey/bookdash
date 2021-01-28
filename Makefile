makefile  := $(firstword $(MAKEFILE_LIST))
rootdir   := $(realpath $(dir ${makefile}))
rootdir   := $(rootdir:/=)
name      := $(shell sed -ne '/^name =/ { s/^name = "\([^"]*\)"/\1/ ; p ; }' ${rootdir}/pyproject.toml)
version   := $(shell sed -ne '/^version =/ { s/^version = "\([^"]*\)"/\1/ ; p ; }' ${rootdir}/pyproject.toml)

# help: init   project initilization tasks like installing dependencies
init:
	poetry install --no-root

# help: shell  start a python shell in the project environment
shell:
	@${rootdir}/tools/mkshell && poetry run ipython -i ${rootdir}/tools/shell.py

# help: run    run code
run:
	@poetry run dash --help

help:
	@echo
	@echo "${name} v ${version}"
	@echo
	@echo "USAGE"
	@echo "   make [cmd]"
	@echo
	@echo "COMMANDS"
	@sed -ne '/^# help:/ { s/^# help:/  / ; p ; }' ${makefile}


.PHONY: init shell run help
.DEFAULT_GOAL := help
