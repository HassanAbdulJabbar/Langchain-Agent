.PHONY: format-code

start-weather-agent:
	python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python main.py

format-code:
	@echo "🔧 Formatting Python files with black and isort..."
	@find . -type f -name "*.py" -not -path "./venv/*" | while read file; do \
		echo "🖤 Formatting with black: $$file"; \
		black "$$file"; \
		echo "📦 Sorting imports with isort: $$file"; \
		isort "$$file"; \
	done
	@echo "✅ Formatting complete."

clean-cache:
	find ./ -type d \( -name '__pycache__' -o -name '.cache' \) -exec rm -rf {} +

