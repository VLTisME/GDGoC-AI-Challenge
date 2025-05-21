SHELL := /bin/bash
.PHONY: base streamlit celery redis fastapi docker local_run package

docker_run:
	docker compose -f docker-compose.yaml up -d
	
local_run:
	chmod +x local_run.sh
	./local_run.sh

