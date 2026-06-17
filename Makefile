install:
	pip install -r requirements.txt

test:
	pytest

run:
	python src/main.py

lint:
	flake8 src/

clean:
	rm -rf __pycache__