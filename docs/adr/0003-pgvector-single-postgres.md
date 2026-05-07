# ADR 0003: pgvector In Single Postgres

Use pgvector in the same Postgres database as the warm relational store. This
reduces operational surface area during homelab bootstrap and keeps migrations,
backups, and local development simple.
