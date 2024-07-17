COMPOSE 		= cd ./source/ && docker compose

# ----------------------- building services --------------------------
up:
	$(COMPOSE) -f docker-compose.yml up --build -d

# ----------------------- removing services --------------------------
down:
	$(COMPOSE) -f docker-compose.yml down

# ----------------------- restarting services --------------------------
start:
	$(COMPOSE) -f docker-compose.yml start

stop:
	$(COMPOSE) -f docker-compose.yml stop

restart: stop start # restarting the services (volumes, network, and images stay the same)

re: down up # rebuilding the services without deleting the persistent storages

# ----------------------- Deleting services and their resources --------------------------
fclean: down
	@yes | docker system prune --all
	@docker volume rm $$(docker volume ls -q)
# @rm -rf ${DB_DIR} ${DATA_DIR}

# ----------------------- rebuilding from scratch --------------------------
# rebuild: fclean up 

.PHONY: up down fclean re restart rebuild