# ADR 0001: Arq Over Celery

Use Arq for scheduled async work. The project is Redis-first already, and Arq
keeps the worker model small while still providing delayed jobs and retries.
Redis Pub/Sub remains the bus; Arq is the durable work queue.
