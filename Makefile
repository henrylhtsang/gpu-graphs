SVG_FILES := $(shell find graphs -type f -name '*.svg' | sort)
PNG_FILES := $(SVG_FILES:.svg=.png)

.PHONY: help png png-force

help:
	@echo "make png        Render missing or outdated PNG companions"
	@echo "make png-force  Regenerate every PNG companion"

png: $(PNG_FILES)

%.png: %.svg scripts/render-svg.sh
	@./scripts/render-svg.sh "$<" "$@"

png-force:
	@set -e; for svg in $(SVG_FILES); do \
		./scripts/render-svg.sh "$$svg" "$${svg%.svg}.png"; \
	done
