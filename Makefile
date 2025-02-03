.PHONY: install activate install_venv start start_detached

install:
	. .venv/bin/activate; pip install -Ur requirements.txt

activate:
	. .venv/bin/activate

install_venv:
	python3 -m venv .venv
	. .venv/bin/activate; python -m pip install --upgrade pip
	. .venv/bin/activate; python -m pip install -r requirements.txt

start:
	. .venv/bin/activate; python -m pip install --upgrade pip
	. .venv/bin/activate; python -m pip install -r requirements.txt
	. .venv/bin/activate; command gunicorn -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:5051 & \
	command gunicorn -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:5056 & \
	command python -m worker_metadata & \
	command python -m worker_paragraphs & \
	command python -m worker_translations

start_inside_docker:
	command gunicorn -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:5051 & \
	command gunicorn -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:5056 & \
	command python -m worker_metadata & \
	command python -m worker_paragraphs & \
	command python -m worker_translations

docker:
	docker compose up --build

formatter:
	. .venv/bin/activate; command black --line-length 125 .