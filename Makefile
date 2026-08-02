SVG_FILES := $(shell find graphs -type f -name '*.svg' | sort)
PNG_FILES := $(SVG_FILES:.svg=.png)

.PHONY: help check svg-qa artifact-qa qa png png-force

help:
	@echo "make png        Render missing or outdated PNG companions"
	@echo "make png-force  Regenerate every PNG companion"
	@echo "make check      Validate kernel and topic authoring specifications"
	@echo "make svg-qa     Check LLM-authored SVG coverage, bounds, and collisions"
	@echo "make qa         Run the spec -> LLM-authored SVG -> QA -> PNG artifact loop"

check:
	@set -e; for spec in $$(find specs -type f -name '*.json' | sort); do \
		PYTHONPATH=src python3 -m gpu_graph.cli "$$spec"; \
	done
	@python3 -m unittest discover -s tests

svg-qa:
	@python3 scripts/qa-graphs.py --stage svg

artifact-qa:
	@python3 scripts/qa-graphs.py --stage artifacts

qa:
	@$(MAKE) --no-print-directory check
	@$(MAKE) --no-print-directory svg-qa
	@$(MAKE) --no-print-directory png
	@$(MAKE) --no-print-directory artifact-qa

png: $(PNG_FILES)

%.png: %.svg scripts/render-svg.sh
	@./scripts/render-svg.sh "$<" "$@"

png-force:
	@set -e; for svg in $(SVG_FILES); do \
		./scripts/render-svg.sh "$$svg" "$${svg%.svg}.png"; \
	done
