SVG_FILES := $(shell find graphs -type f -name '*.svg' | sort)
PNG_FILES := $(SVG_FILES:.svg=.png)

CUTLASS_ROOT ?= $(HOME)/cutlass

.PHONY: help generate check-cutlass-inventory png png-force

help:
	@echo "make png        Render missing or outdated PNG companions"
	@echo "make png-force  Regenerate every PNG companion"
	@echo "make generate   Regenerate diagrams backed by repository generators"
	@echo "make check-cutlass-inventory  Audit warp-specialized CUTLASS coverage"

generate:
	@python3 scripts/generate-quack-infographs.py
	@python3 scripts/generate-cutlass-warp-specialization.py

check-cutlass-inventory:
	@python3 scripts/generate-cutlass-warp-specialization.py --check "$(CUTLASS_ROOT)"

png: $(PNG_FILES)

%.png: %.svg scripts/render-svg.sh
	@./scripts/render-svg.sh "$<" "$@"

png-force:
	@set -e; for svg in $(SVG_FILES); do \
		./scripts/render-svg.sh "$$svg" "$${svg%.svg}.png"; \
	done
