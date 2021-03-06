EMPTY:

create-secret:
	-kubectl --namespace=hogwarts-bot delete secret hogwarts-secrets
	kubectl --namespace=hogwarts-bot create secret generic hogwarts-secrets \
	  --from-file=./secrets.py --from-file=./hogwarts-bot-credentials.json

create-namespace:
	kubectl create -f ./namespace.yaml

build-docker-image: EMPTY
	docker build -t hogwarts-bot .

test: build-docker-image
	docker run -it --entrypoint "python" -v "`pwd`/src:/app" -v "`pwd`/tmp:/tmp" hogwarts-bot image_test.py
	docker run -it --entrypoint "python" -v "`pwd`/src:/app" hogwarts-bot test.py

devshell:
	docker run -it --entrypoint "bash" -v "`pwd`/src:/app" -v "`pwd`/tmp:/tmp" hogwarts-bot

build: build-docker-image
	docker tag hogwarts-bot gcr.io/khan-internal-services/hogwarts-bot
	gcloud docker -- push gcr.io/khan-internal-services/hogwarts-bot

run: build
	kubectl create -f ./deployment.yaml

stop:
	kubectl --namespace=hogwarts-bot delete deployment hogwarts-bot