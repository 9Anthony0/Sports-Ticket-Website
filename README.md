# Purdue Student Ticket Exchange

A full-stack web app where Purdue students list, find and buy tickets to Boilermaker home games. Built with Flask and SQLAlchemy on SQLite, with a deployment config for Google App Engine.

<!-- LIVE DEMO: add your deployed link here -->

## Features
- **Browse and filter:** search listings by sport and maximum price. The sport dropdown is built from the database.
- **Sell:** list a ticket for any event, then edit the price or delete the listing from *My Tickets*.
- **Safe checkout:** each purchase runs as one explicit database transaction. It re-checks that the ticket is still available, marks it sold and writes the sale record together, so two buyers can't purchase the same ticket. On conflict or lock it rolls back cleanly.
- **Auto-seeded data:** on first start the app creates 51 events: football at Ross-Ade, basketball at Mackey and volleyball at Holloway, against all 17 Big Ten opponents.

## Data model
```
students      (PUID, first_name, last_name, email)
events        (event_id, sport_type, opponent, event_date, venue)
tickets       (ticket_id, event_id → events, seller_id → students, price, status)
transactions  (transaction_id, ticket_id → tickets, buyer_id → students, date, price)
```
Indexes on `sport_type`, `price` and `status` keep the filter queries fast.

## Run it locally
```bash
pip install -r requirements.txt
python seed.py            # optional: reset the database with fresh demo data
flask --app stage0:Stage1 run
```
Then open http://127.0.0.1:5000.

## Deploy
`app.yaml` targets the Google App Engine Python 3.11 standard runtime, served by gunicorn. On App Engine the SQLite file lives in `/tmp`, so data resets when an instance restarts. That's fine for a demo; a production version would use Cloud SQL.

## Notes
The buyer is a simulated logged-in student (PUID 1). Adding authentication is the natural next step.

## Tech
Python · Flask · Flask-SQLAlchemy · SQLite · Jinja2 · gunicorn · Google App Engine

---
Built by [Anthony Petrescu](https://www.linkedin.com/in/anthony-petrescu/) · Purdue Finance + Computer Science '27
