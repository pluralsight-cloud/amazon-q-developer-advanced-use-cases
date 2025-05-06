from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import calendar
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import uuid
import sqlite3
from ics import Calendar, Event
import pytz

app = Flask(__name__)

def create_calendar_invite(party_details):
    """Create an ICS file for the party"""
    cal = Calendar()
    event = Event()
    
    # Parse the date string and set time (assuming party starts at 7 PM and ends at 11 PM)
    date_obj = datetime.strptime(party_details['date'], "%B %d, %Y")
    
    # Set timezone (change 'America/New_York' to your desired timezone)
    local_tz = pytz.timezone('America/New_York')
    
    # Create start and end times (7 PM to 11 PM)
    start_time = local_tz.localize(date_obj.replace(hour=19, minute=0))
    end_time = local_tz.localize(date_obj.replace(hour=23, minute=0))
    
    event.name = f"Birthday Party"
    event.begin = start_time
    event.end = end_time
    event.description = f"""
    Birthday Party Celebration!
    
    Date: {party_details['date']}
    Time: 7:00 PM - 11:00 PM
    """
    
    cal.events.add(event)
    return str(cal)

def find_party_dates(birthday_date):
    """Find the closest Friday and Saturday before the birthday"""
    party_dates = []
    
    # Start checking from the birthday and work backwards
    current_date = birthday_date
    
    # Keep track of found days
    found_friday = False
    found_saturday = False
    
    # Check up to 7 days before birthday to ensure we find both days
    for _ in range(7):
        current_date = current_date - timedelta(days=1)
        day_of_week = current_date.weekday()
        
        # Friday is 4, Saturday is 5
        if day_of_week == 4 and not found_friday:
            party_dates.append({
                'day': 'Friday',
                'date': current_date.strftime("%B %d, %Y")
            })
            found_friday = True
            
        if day_of_week == 5 and not found_saturday:
            party_dates.append({
                'day': 'Saturday',
                'date': current_date.strftime("%B %d, %Y")
            })
            found_saturday = True
            
        if found_friday and found_saturday:
            break
    
    return sorted(party_dates, key=lambda x: datetime.strptime(x['date'], "%B %d, %Y"))

def calculate_birthday_day(birthday, target_year):
    """Calculate the day of week for birthday in target year"""
    try:
        future_birthday = datetime(
            year=target_year,
            month=birthday.month,
            day=birthday.day
        )
        day_of_week = calendar.day_name[future_birthday.weekday()]
        formatted_date = future_birthday.strftime("%B %d, %Y")
        party_dates = find_party_dates(future_birthday)
        
        return True, {
            'day_of_week': day_of_week,
            'formatted_date': formatted_date,
            'party_dates': party_dates
        }
    except ValueError as e:
        return False, str(e)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        birthday_str = request.form['birthday']
        target_year = int(request.form['target_year'])
        
        # Parse the birthday
        birthday = datetime.strptime(birthday_str, "%Y-%m-%d")
        
        # Validate target year
        if target_year < 1:
            return jsonify({
                'success': False,
                'error': 'Please enter a valid year'
            })

        success, result = calculate_birthday_day(birthday, target_year)
        
        if success:
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result
            })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Please enter valid date values'
        })

@app.route('/create_calendar_invite', methods=['POST'])
def generate_calendar_invite():
    try:
        data = request.get_json()
        cal_content = create_calendar_invite(data)
        
        return jsonify({
            'success': True,
            'ics_content': cal_content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)

