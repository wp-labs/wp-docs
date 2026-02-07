# Makefile for mdbook documentation management

.PHONY: help build serve install clean summary summary-simple validate build-zh build-en build-all serve-zh serve-en

# Default target
help:
	@echo "Available targets:"
	@echo "  build         - Build all language versions"
	@echo "  build-zh      - Build Chinese version only"
	@echo "  build-en      - Build English version only"
	@echo "  build-all     - Build all language versions (same as build)"
	@echo "  serve         - Serve Chinese version (http://localhost:3000)"
	@echo "  serve-zh      - Serve Chinese version (http://localhost:3000)"
	@echo "  serve-en      - Serve English version (http://localhost:3001)"
	@echo "  install       - Install required tools"
	@echo "  summary       - Generate structured SUMMARY.md"
	@echo "  summary-simple- Generate simple SUMMARY.md"
	@echo "  validate      - Validate markdown links and formatting"
	@echo "  clean         - Clean build artifacts"

# Install required tools
install:
	@echo "Installing mdbook..."
	@if ! command -v mdbook &> /dev/null; then \
		curl -L https://github.com/rust-lang/mdBook/releases/download/v0.4.21/mdbook-v0.4.21-x86_64-apple-darwin.tar.gz | tar xz -C /usr/local/bin; \
	fi
	@echo "Installing mdbook-auto-summary..."
	@if ! command -v mdbook-auto-summary &> /dev/null; then \
		cargo install mdbook-auto-summary; \
	fi
	@echo "Installing markdown-link-check..."
	@if ! command -v markdown-link-check &> /dev/null; then \
		npm install -g markdown-link-check; \
	fi

# Build all language versions
build: build-zh build-en copy-assets
	@echo "All documentation built successfully!"

# Build Chinese version
build-zh:
	@echo "Building Chinese documentation..."
	cd docs-zh && mdbook build
	@mkdir -p book/zh/theme
	@cp theme/lang-switch.css book/zh/theme/
	@cp theme/lang-switch.js book/zh/theme/

# Build English version
build-en:
	@echo "Building English documentation..."
	cd docs-en && mdbook build
	@mkdir -p book/en/theme
	@cp theme/lang-switch.css book/en/theme/
	@cp theme/lang-switch.js book/en/theme/

# Copy index.html and assets
copy-assets:
	@echo "Copying language selection page..."
	@mkdir -p book
	@cp index.html book/

# Serve documentation locally (Chinese, default port 3000)
serve: serve-zh

# Serve Chinese version
serve-zh:
	@echo "Starting Chinese documentation server on http://localhost:3000..."
	cd docs-zh && mdbook serve --hostname 0.0.0.0 --port 3000

# Serve English version
serve-en:
	@echo "Starting English documentation server on http://localhost:3001..."
	cd docs-en && mdbook serve --hostname 0.0.0.0 --port 3001

# Generate structured SUMMARY.md
summary:
	@echo "Generating structured SUMMARY.md..."
	python3 generate_summary.py

# Generate simple SUMMARY.md
summary-simple:
	@echo "Generating simple SUMMARY.md..."
	python3 generate_summary.py

# Validate markdown links and formatting
validate:
	@echo "Validating markdown links..."
	@if command -v markdown-link-check &> /dev/null; then \
		markdown-link-check **/*.md; \
	else \
		echo "markdown-link-check not found. Install with: npm install -g markdown-link-check"; \
	fi

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf book/
	rm -f SUMMARY.md.bak

# Full rebuild workflow
rebuild: clean summary build
	@echo "Documentation rebuilt successfully!"

# Watch for changes and auto-rebuild (requires inotify-tools)
watch:
	@echo "Watching for changes (requires inotify-tools)..."
	@while inotifywait -e modify -r **/*.md; do \
		echo "Changes detected, rebuilding..."; \
		make build; \
	done