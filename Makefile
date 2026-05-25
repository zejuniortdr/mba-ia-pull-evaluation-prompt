pull:
	uv run python src/pull_prompts.py

push: 
	uv run python src/push_prompts.py

evaluate:
	uv run python src/evaluate.py

test:
	uv run pytest tests/test_prompts.py