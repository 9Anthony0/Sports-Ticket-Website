from stage0 import Stage1, db, Student, Event, Ticket, Transaction

with Stage1.app_context():
    # 1. Clear out the old dummy data so we don't get duplicates
    db.drop_all()
    db.create_all()

    # 2. Add our test student (You!)
    student1 = Student(PUID=1, first_name="Anthony", last_name="Boilermaker", email="anthony@purdue.edu")
    db.session.add(student1)

    # 3. The 17 other Big Ten Schools
    big_ten_opponents = [
        "Illinois", "Indiana", "Iowa", "Maryland", "Michigan", 
        "Michigan State", "Minnesota", "Nebraska", "Northwestern", 
        "Ohio State", "Penn State", "Rutgers", "Wisconsin",
        "Oregon", "UCLA", "USC", "Washington"
    ]

    # 4. Define the sports and their correct Purdue venues
    sports_info = [
        {"sport": "Basketball", "venue": "Mackey Arena", "date": "Winter 2026"},
        {"sport": "Football", "venue": "Ross-Ade Stadium", "date": "Fall 2026"},
        {"sport": "Volleyball", "venue": "Holloway Gymnasium", "date": "Fall 2026"}
    ]

    # 5. Loop through and create an event for every combination
    for info in sports_info:
        for opponent in big_ten_opponents:
            new_event = Event(
                sport_type=info["sport"],
                opponent=opponent,
                event_date=info["date"],
                venue=info["venue"]
            )
            db.session.add(new_event)
            
    # 6. Save all 51 events to the database
    db.session.commit()
    print("Database successfully seeded with all Big Ten matchups!")