
.PHONY: list_topics

list_topics:
	docker exec -it redpanda rpk topic list --brokers=localhost:19092

list_schemas:
	curl http://localhost:8081/subjects


list_connectors:
	curl http://localhost:8083/connectors

mongo_client:
	docker run -it --rm rtsp/mongosh mongosh mongodb://host.docker.internal:27017

postgres_client:
	docker run -it --rm postgres psql -h host.docker.internal -U debezium -d lumi_credit

init:
	docker compose exec -it timeplus timeplus sync --username proton --password timeplus@t+ apply ./tp-sync/