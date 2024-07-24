
COMPOSE 		= cd ./source/ && docker compose


# ----------------------- building services --------------------------
up:
	$(COMPOSE) -f docker-compose.yml up --build -d

down:
	$(COMPOSE) -f docker-compose.yml down

re: down up # rebuilding the services without deleting the persistent storages


# ----------------------- restarting services --------------------------

start:
	$(COMPOSE) -f docker-compose.yml start

stop:
	$(COMPOSE) -f docker-compose.yml stop

restart: stop start # restarting the services (volumes, network, and images stay the same)


# ----------------------- Deleting resources and rebuilding --------------------------

fclean: down
	@yes | docker system prune --all
	@docker volume rm $$(docker volume ls -q)

rebuild: fclean up 

# ----------------------- Managing transcendence service only --------------------------

trans-down:
	$(COMPOSE) -f docker-compose.yml stop transcendence
	$(COMPOSE) -f docker-compose.yml rm -f transcendence

trans-up:
	$(COMPOSE) -f docker-compose.yml up --build -d --no-deps transcendence

trans-restart: trans-down trans-up

# ---------------------------- git push target -------------------------------

push:
	@if [ -z "$(msg)" ]; then \
		echo "Please provide a commit message."; \
		echo "Usage: make push msg=\"<commit_message>\""; \
		exit 1; \
	fi
	git add .
	git status
	git commit -m "$(msg)"
	git push


# ---------------------------- PHONY PHONY ... -------------------------------
.PHONY: up down fclean re restart rebuild

