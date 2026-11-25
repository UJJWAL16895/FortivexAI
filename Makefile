ifeq ($(OS),Windows_NT)
VENV_PY := .venv/Scripts/python.exe
BOOTSTRAP ?= $(if $(wildcard $(VENV_PY)),$(VENV_PY),py -3.13)
else
BOOTSTRAP ?= python3.13
VENV_PY := .venv/bin/python
endif

PORT ?= 8000
VOICE_MODELS ?= 0
KNOWLEDGE_MODEL ?= 0

.PHONY: setup verify scan run demo
setup:
	$(BOOTSTRAP) scripts/tasks.py setup $(if $(filter 1,$(VOICE_MODELS)),--voice-models) $(if $(filter 1,$(KNOWLEDGE_MODEL)),--knowledge-model)

verify scan:
	$(VENV_PY) scripts/tasks.py $@

run demo:
	$(VENV_PY) scripts/tasks.py $@ --port $(PORT)
