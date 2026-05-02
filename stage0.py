from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import datetime

Stage1 = Flask(__name__)

# Database Config
if os.environ.get('GAE_ENV') == 'standard':
    Stage1.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/tickets.db'
else :
    Stage1.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db' 

Stage1.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(Stage1)

# Database Model
class Student(db.Model):
    __tablename__ = 'students'
    PUID = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Event(db.Model):
    __tablename__ = 'events'
    event_id = db.Column(db.Integer, primary_key=True)
    sport_type = db.Column(db.String(50), nullable=False, index=True)
    opponent = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.String(50), nullable=False)
    venue = db.Column(db.String(100), nullable=False)

class Ticket(db.Model):
    __tablename__ = 'tickets'
    ticket_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('students.PUID'), nullable=False)
    price = db.Column(db.Float, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='Available', index=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    transaction_id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.ticket_id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('students.PUID'), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)



# Routes

@Stage1.route("/")
def home():
    # Now it loads a sleek HTML template instead of plain text!
    return render_template('home.html')

@Stage1.route('/my-tickets')
def my_tickets():
    # For now, we will hardcode a student_id to simulate a logged-in user
    current_student_id = 1 
    
    # Query the database for all tickets listed by this student
    user_tickets = Ticket.query.filter_by(seller_id=current_student_id).all()
    
    # Pass the data to an HTML template to display
    return render_template('my_tickets.html', tickets=user_tickets)

# 2. CREATE: Insert a new ticket listing into the database
@Stage1.route('/add-ticket', methods=['GET', 'POST'])
def add_ticket():
    if request.method == 'POST':
        # Grab data submitted from the HTML form
        event_id = request.form.get('event_id')
        price = request.form.get('price')
        current_student_id = 1 # Simulated logged-in user
        
        # Create a new Ticket object
        new_ticket = Ticket(
            event_id=event_id, 
            seller_id=current_student_id, 
            price=price, 
            status='Available'
        )
        
        # Insert the new record into the database and save
        db.session.add(new_ticket)
        db.session.commit()
        
        # Send the user back to their dashboard
        return redirect(url_for('my_tickets'))
        
    # If it's a GET request, we need to show the form.
    # We query the Events table to dynamically populate the "Select Event" drop-down menu!
    events = Event.query.all()
    return render_template('add_ticket.html', events=events)

# 3. UPDATE: Edit the price or status of an existing ticket
@Stage1.route('/edit-ticket/<int:ticket_id>', methods=['GET', 'POST'])
def edit_ticket(ticket_id):
    # Find the specific ticket in the database, or return a 404 error if it doesn't exist
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if request.method == 'POST':
        try:
            with db.session.begin():
                # Update the ticket's attributes with the new form data
                ticket.price = request.form.get('price')
                ticket.status = request.form.get('status')
        except Exception as e:
            # If the database is locked by another user, it rolls back safely
            print(f"Transaction failed and rolled back: {e}")
        
        return redirect(url_for('my_tickets'))
        
    # Pass the existing ticket data to the template so the form fields are pre-filled
    return render_template('edit_ticket.html', ticket=ticket)

# 4. DELETE: Remove a ticket from the database completely
@Stage1.route('/delete-ticket/<int:ticket_id>', methods=['POST'])
def delete_ticket(ticket_id):
    # Find the ticket
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Delete it from the database and save
    db.session.delete(ticket)
    db.session.commit()
    
    return redirect(url_for('my_tickets'))

# ---------------------------------------------------------
# REQUIREMENT 2: Filtering and Reporting
# ---------------------------------------------------------
@Stage1.route('/find-tickets', methods=['GET'])
def find_tickets():
    # Grab filter inputs from the search bar
    sport_filter = request.args.get('sport')
    max_price = request.args.get('max_price')

    # Start a database query that joins Tickets and Events
    query = db.session.query(Ticket, Event).join(Event, Ticket.event_id == Event.event_id)

    # Apply the filters if the user typed them in
    if sport_filter:
        query = query.filter(Event.sport_type == sport_filter)
    if max_price:
        query = query.filter(Ticket.price <= float(max_price))

    # Get the final filtered results
    results = query.all()

    # Get unique sports to dynamically populate the filter dropdown (Requirement 2c)
    sports = db.session.query(Event.sport_type).distinct().all()
    sports_list = [sport[0] for sport in sports]

    return render_template('find_tickets.html', results=results, sports=sports_list)

# Stage 3 Checkout Isolation
@Stage1.route('/buy-ticket/<int:ticket_id>', methods=['POST'])
def buy_ticket(ticket_id):
    # Simulated logged-in buyer
    current_student_id = 1 
    
    try:
        # EXPLICIT TRANSACTION START
        with db.session.begin():
            # Query the ticket
            ticket = Ticket.query.get_or_404(ticket_id)
            
            # Check if someone else already bought it
            if ticket.status != 'Available':
                # Cancel the transaction safely
                print("Ticket is no longer available.")
                return redirect(url_for('find_tickets'))
                
            # 1. Update the ticket status
            ticket.status = 'Sold'
            
            # 2. Create a new record in the Transactions table
            new_sale = Transaction(
                ticket_id=ticket.ticket_id,
                buyer_id=current_student_id,
                date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                price=ticket.price
            )
            db.session.add(new_sale)
            
        # EXPLICIT TRANSACTION END (Commits automatically if no errors occurred)
        print("Ticket purchased successfully!")
        
    except Exception as e:
        # If SQLite is locked by another transaction, it jumps here and safely rolls back
        print(f"Transaction failed and rolled back due to concurrency/database error: {e}")
        
    return redirect(url_for('find_tickets'))

# Run the server
with Stage1.app_context():
    db.create_all()
    
    # If the database is empty, seed it with data automatically
    if not Event.query.first():
        # Add a test student
        student1 = Student(PUID=1, first_name="Anthony", last_name="Boilermaker", email="anthony@purdue.edu")
        db.session.add(student1)

        # Add the Big Ten match-ups
        sports_info = [
            {"sport": "Basketball", "venue": "Mackey Arena", "date": "Winter 2026"},
            {"sport": "Football", "venue": "Ross-Ade Stadium", "date": "Fall 2026"},
            {"sport": "Volleyball", "venue": "Holloway Gymnasium", "date": "Fall 2026"}
        ]
        big_ten_opponents = [
            "Illinois", "Indiana", "Iowa", "Maryland", "Michigan", 
            "Michigan State", "Minnesota", "Nebraska", "Northwestern", 
            "Ohio State", "Penn State", "Rutgers", "Wisconsin",
            "Oregon", "UCLA", "USC", "Washington"
        ]

        for info in sports_info:
            for opponent in big_ten_opponents:
                new_event = Event(
                    sport_type=info["sport"],
                    opponent=opponent,
                    event_date=info["date"],
                    venue=info["venue"]
                )
                db.session.add(new_event)
                
        db.session.commit()
if __name__ == "__main__":
    Stage1.run(debug=True)