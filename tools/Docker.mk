.PHONY: down
down:	
	docker compose -f $(DOCKER_COMPOSE) down --remove-orphans --volumes

.PHONY: up
up:	
	docker compose -f $(DOCKER_COMPOSE) up -d --force-recreate --remove-orphans --renew-anon-volumes
