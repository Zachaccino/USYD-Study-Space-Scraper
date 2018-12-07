import json
import datetime
import time
import sys
import math

# Configuration
# This is set to Sem 2 2018.
sem_start_date = datetime.date(2018, 7, 30)
weeks_per_sem = 13

# Mid sem break is week:
mid_sem_break = 9

# A dict for average O(1) access and for month text to digit conversion.
month_digit = {'Jan':1,
               'Feb':2,
               'Mar':3,
               'Apr':4,
               'May':5,
               'Jun':6,
               'Jul':7,
               'Aug':8,
               'Sep':9,
               'Oct':10,
               'Nov':11,
               'Dec':12}

# A dict to convert short hand day to digit.
day_digit = {'Mon':1,
             'Tue':2,
             'Wed':3,
             'Thu':4,
             'Fri':5,
             'Sat':6,
             'Sun':7}


# Reading Json from crawled files.
def read_schedule():
    file = open("schedulling.json", "r")
    data = json.loads(file.read())
    file.close()
    return data


def read_venue():
    file = open("venues.json", "r")
    data = json.loads(file.read())
    file.close()
    return data


# The string argument is in the form:
# Mon 31 JUL 2018
def parse_date(string):
    global month_digit
    global day_digit
    split_str = string.split(' ')
    date = datetime.date(int(split_str[3]), month_digit[split_str[2]], int(split_str[1]))
    return date, day_digit[split_str[0]]


# Create an empty dict for unoccupied_venues_sort_by_venue.
# True means unoccupied, False means occupied.
def empty_container():
    # Retrieve all venues
    venues = []
    for k, v in read_venue().items():
        venues.append(v['venue'])

    # Create a dictionation that contains all the teaching weeks.
    container = {}
    for week in range(1, 14):
        container.update({week:{}})
        for venue in venues:
            container[week].update({venue:{}})
            for day in range(1, 8):
                container[week][venue].update({day:{}})
                for hour in range(8, 21):
                    container[week][venue][day].update({hour:None})

    return container


# Convert actual date to universities's timetabled week. and the timetabled week
# is the key to access dictionary.
# i.e actual date in week 9 is mid sem and actual week 10 is timetable week 9.
def date_to_key(s_date):
    global mid_sem_break

    # +0.1 is used to correct the calculation. Otherwise, week 9 monday will be count
    # towards week 8. and the week 1 monday is count towards week 0 which is incorrect.
    actual_week = math.ceil(((s_date - sem_start_date).days+0.1)/7)

    if actual_week == mid_sem_break:
        return 0
    elif actual_week < mid_sem_break:
        return actual_week
    elif actual_week > mid_sem_break:
        return actual_week - 1


# Provide start and end date of the booking, Return a list of weeks that the
# venue is going to be occupied.
def get_scheduled_week(s_date, e_date, frequency):
    global sem_start_date
    scheduled_weeks = []
    increment = None

    # Set the frequency of occupying the venue.
    if frequency == "Weekly":
        increment = 1
    if frequency == "Fortnightly":
        increment = 2
    if frequency == "Once Only":
        scheduled_week = date_to_key(s_date)

        # <= 0 because sometimes the timetable actually contains events
        # which starts before semester and after semester, This is not a concern.
        if scheduled_week <= 0 or scheduled_week > 13:
            return []
        else:
            return [scheduled_week]

    # 14 weeks in total because mid sem break occupies the 9th week.
    index = 0
    while(index < 14):
        # Getting the actual date.
        actual_date = s_date + datetime.timedelta(days=index * 7)

        # Checking if the actual date is before end date.
        if actual_date > e_date:
            break

        # Get the week of the actual date.
        scheduled_week = date_to_key(actual_date)

        # Checking if it is during mid semester break etc. Skip if it is.
        if scheduled_week <= 0 or scheduled_week > 13:
            index += 1
            continue

        # Adding this week to scheduled weeks.
        scheduled_weeks.append(scheduled_week)

        # Checking if the week after this week is mid sem break and occupied fortnightly.
        if increment == 2 and date_to_key(actual_date + datetime.timedelta(days=7)) == 0:
            index += 3

        # Just increment by regular interval.
        else:
            index += increment

    return scheduled_weeks


# Extract the occupied time for each venue.
# Format {WEEK:{Venue:[Day:{Time:CourseCode / None}}}
def occupied_venues():
    data = read_schedule()
    occupied = empty_container()

    for key, schedule in data.items():
        # Getting the weeks occupied.
        s_date, s_day = parse_date(schedule['start_date'])
        e_date, e_day = parse_date(schedule['end_date'])
        frequency = schedule['frequency']
        scheduled_weeks = get_scheduled_week(s_date, e_date, frequency)

        # Getting the time to be occupied. Round down the hour if it starts
        # after xx:00.
        s_time = int(schedule['start_time'].split(":")[0])
        e_time = None

        # When a course not ends at xx:00, then round up to the next hour.
        if int(schedule['end_time'].split(":")[1]) > 0:
            e_time = int(schedule['end_time'].split(":")[0]) + 1
        else:
            e_time = int(schedule['end_time'].split(":")[0])

        # Get course code.
        course_code = schedule['course'].split("-")[0].strip()

        # Get Venue.
        venue = schedule['venue']

        # Updating dictionary.
        for week in scheduled_weeks:
            for hour in range(s_time, e_time):
                occupied[week][venue][s_day][hour] = course_code

    return occupied


# Convert Schedulling Json and Venues Json to Occupied data Json.
# Output a file that contains the occupied time for each venue.
def convert():
    # Get occupied data.
    data = occupied_venues()

    # Store them one file / week.
    for week in range(1, 14):
        file = open('./out/occupied_' + str(week) + '.json', 'w')
        file.write(json.dumps(data[week], default=str))
        file.close()


# Execute the program.
convert()
