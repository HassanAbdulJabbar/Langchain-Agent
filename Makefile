.PHONY: format-code

start-weather-agent:
	python main.py

format-code:
	@echo "🔧 Formatting Python files with black and isort..."
	@find . -type f -name "*.py" -not -path "./venv/*" | while read file; do \
		echo "🖤 Formatting with black: $$file"; \
		black "$$file"; \
		echo "📦 Sorting imports with isort: $$file"; \
		isort "$$file"; \
	done
	@echo "✅ Formatting complete."

