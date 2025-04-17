install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python -m pytest -vv test_main.py

format:
	black *.py

run:
	python src/main.py

lint:
	-pylint --disable=R,C src/main.py

clean:
	rm -rf __pycache__/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf htmlcov/

all: install lint
