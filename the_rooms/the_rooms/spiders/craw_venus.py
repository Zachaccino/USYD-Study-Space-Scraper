import scrapy
import json

class CrawVenues(scrapy.Spider):
    name = "craw_venues"

    # Craw venue 1 to begin with.
    def start_requests(self):
        urls = [
            'https://web.timetable.usyd.edu.au/venuebookings/venueCalendar.jsp?vs=0&venueId=1774&mode=Timetables&day=4&month=12&year=2018&rangeType=semester&sessionId=2&semYear=2018',
            ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # Reading Data from page.
    def parse(self, response):
        raw_data = response.xpath('//select[@id = "venueIdShort"]/option').extract()
        venues = {}

        for item in raw_data:
            # Handling Formatting
            splits_str = item.split("\"")
            venue_id = splits_str[1]
            venue_name = splits_str[2][1:].split("\xa0")[0]

            if venue_id == "1774":
                venue_name = venue_name.replace('selected>','')

            venue_code = splits_str[-1].split("\xa0")[-1].split('<')[0][1:-1]

            venues.update({venue_id:{'venue':venue_name, 'code':venue_code}})

        # Writing to file.
        file = open('venues.json', 'w')
        file.write(json.dumps(venues))
        file.close()
        pass
