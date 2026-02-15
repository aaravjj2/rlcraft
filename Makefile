.PHONY: up down reset-db migrate ingest-fixtures wait-db

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rlc

up:
	pg_ctlcluster 16 main start || true

wait-db:
	@for i in $$(seq 1 60); do \
		pg_isready -h localhost -p 5432 -U postgres >/dev/null 2>&1 && echo "postgres healthy" && exit 0; \
		sleep 1; \
	done; echo "postgres not healthy"; exit 1

down:
	pg_ctlcluster 16 main stop || true

reset-db:
	PGPASSWORD=postgres psql -h localhost -U postgres -d rlc -v ON_ERROR_STOP=1 -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

migrate:
	for f in $$(ls packages/db/migrations/*.sql | sort); do \
		echo "Applying $$f"; \
		PGPASSWORD=postgres psql -h localhost -U postgres -d rlc -v ON_ERROR_STOP=1 -f $$f; \
	done

ingest-fixtures:
	DATABASE_URL=$(DATABASE_URL) python -m ingest ingest --build-dir fixtures/demo_build --pack-name demo --pack-version 1.0 --mc-version 1.12.2
	DATABASE_URL=$(DATABASE_URL) python -m ingest ingest-images --build-id $$(DATABASE_URL=$(DATABASE_URL) python -m ingest latest-build-id) --images-dir fixtures/images --labels fixtures/images/labels.json --embedder toy
