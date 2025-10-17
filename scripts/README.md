# Database Management Scripts

This directory contains scripts for managing the database schema and data.

## Available Scripts

### Seed Database
```bash
poetry run seed-db
```
Sets up the database schema and seeds it with initial episode data.

### Reset Database
```bash
poetry run reset-db
```
**WARNING**: This will delete all data in the database!
Drops all tables and recreates the schema with fresh data.

## Manual Execution

You can also run the scripts directly:

```bash
# Seed database
python scripts/seed_database.py

# Reset database (with confirmation prompt)
python scripts/reset_database.py
```

## Migration Files

The `migrations/` directory contains SQL files that define the database schema:

- `001_initial_schema.sql` - Creates tables and indexes
- `002_seed_episodes.sql` - Inserts initial episode data (the Python seed script replays this file so update it to change seed data)

## Workflow

1. **First time setup**: Run `poetry run seed-db`
2. **Development**: Use the main application normally
3. **Reset data**: Run `poetry run reset-db` when you need to start fresh
4. **Add new episodes**: Add them to the migration files or use the API

## Environment Variables

Make sure you have the following environment variables set:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=gent_disagreement
```
