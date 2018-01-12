test:
	python -m unittest discover -p "test*.py"

clean:
	find . -type f -name '*.pyc' -delete

.PHONY: test clean
