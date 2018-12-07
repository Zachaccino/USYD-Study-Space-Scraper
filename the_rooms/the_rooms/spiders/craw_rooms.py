import scrapy
import json
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

class CrawRooms(scrapy.Spider):
    # Crawler Alias.
    name = "craw_rooms"

    # All class schedulling data with its own lock.
    schedulling = {}

    # Craw every venue.
    def start_requests(self):
        # Execute write data to file function when spider closes.
        dispatcher.connect(self.spider_closed, signals.spider_closed)

        # Reading all available venues.
        file = open('venues.json', 'r')
        venues = json.loads(file.read())
        file.close()
        print("Total: " + str(len(venues)))
        counter = 0

        # Scrape each venue.
        for k, v in venues.items():


            # Spawn crawler on new thread.
            print(">>> Acquiring web page for venue: " + v['venue'] + "\nQueue: " + str(counter))
            site = 'https://web.timetable.usyd.edu.au/venuebookings/venueCalendar.jsp?vs=0&venueId=' + k + '&mode=Timetables&day=4&month=12&year=2018&rangeType=semester&sessionId=2&semYear=2018'
            counter += 1
            yield scrapy.Request(url=site, callback=self.parse, meta={'venue':v['venue']})

    # Merge all data on schedulling pipeline when all spider finished crawling.
    def spider_closed(self, spider):
        file = open('schedulling.json', 'w')
        file.write(json.dumps(spider.schedulling))
        file.close()


    # Reading Data from page.
    def parse(self, response):
        # Get current venue being searched.
        current_venue = response.meta.get('venue')
        print(">>> Begin parsing venue: " + current_venue)

        # Extract venue booking information.
        raw_data = response.xpath('//a[@class = "ttBooking"]').extract()

        # Acquire lock and converting venue information lxml to useful information.
        for data in raw_data:
            self.schedulling.update({len(self.schedulling):self.token_parser(data, current_venue)})

        print(">>> Parsing done for venue: " + current_venue)
        pass


    # Retrieve tokens.
    def token_parser(self, string, current_venue):
        # Split the string based on <br /> tag.
        splits_str = string.split('&lt;br /&gt;')

        # Retrieve course code.
        course = splits_str[1].strip()

        # Retrieve date.
        date = splits_str[6][14:].split('-')
        start_date = date[0].strip()
        end_date = date[1].strip()

        # Retrieve time.
        time = splits_str[7][14:].split('-')
        start_time = time[0].strip()
        end_time = time[1].strip()

        # Retrieve Frequency.
        frequency = splits_str[8][10:].strip()

        return {'venue':current_venue,
                'course':course,
                'start_date':start_date,
                'end_date':end_date,
                'start_time':start_time,
                'end_time':end_time,
                'frequency':frequency}
