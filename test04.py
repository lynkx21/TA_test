from lxml import html
import requests
import pandas as pd
import googlemaps as gm
import random



# main page
inputPage = "https://www.tripadvisor.com/attractions-g190479-activities-oslo_eastern_norway.html#attraction_sort_wrapper"

# next pages
second_page01 = "https://www.tripadvisor.com/Attractions-g190479-Activities-oa"
second_page02 = "-Oslo_Eastern_Norway.html#ATTRACTION_LIST"


def stringCleaner(inputList):
    for n in inputList:
        if n != '\n':
            output = n.replace("\n", "")
            return output
            break


def tripScraper(tripPage,innerPage01,innerPage02):
    # first scraping
    page = requests.get(tripPage)
    tree = html.fromstring(page.content)
    attraction_xpath = tree.xpath('//div[@class="property_title"]/a/text()')
    attractions_links = tree.xpath('//div[@class="property_title"]/a/@href')

    max_attractions = tree.xpath('//a[@class="pageNum taLnk"]/@data-offset')
    print(max_attractions)
    print(max(map(int,max_attractions)))
    max_att = max(map(int,max_attractions))

    i = 30
    while (i <= max_att):
        second_page = requests.get(innerPage01+str(i)+innerPage02)
        tree = html.fromstring(second_page.content)
        page_attractions = tree.xpath('//div[@class="property_title"]/a/text()')
        page_attractions_links = tree.xpath('//div[@class="property_title"]/a/@href')
        for j, k in enumerate(page_attractions):
            attraction_xpath.append(k)
            attractions_links.append(page_attractions_links[j])
        i = i+30

    attractions_out = pd.DataFrame(columns=('name', 'address', 'extAddress', 'locality', 'postalCode', 'country', 'openingDays', 'openingHours'))

    for j,i in enumerate(attractions_links):
        print("https://www.tripadvisor.com"+i)
        attraction_page = requests.get("https://www.tripadvisor.com"+i)
        attraction_tree = html.fromstring(attraction_page.content)

        # xpath on the features
        names = attraction_tree .xpath('//h1[@property="name"]/text()')
        addresses = attraction_tree.xpath('//span[@class="street-address"]/text()')
        extAddress = attraction_tree.xpath('//span[@class="extended-address"]/text()')
        localities = attraction_tree.xpath('//span[@class="locality"]/span[@property="addressLocality"]/text()')
        postalCode = attraction_tree.xpath('//span[@class="locality"]/span[@property="postalCode"]/text()')
        country = attraction_tree.xpath('//span[@class="country-name"]/text()')
        openingDays = attraction_tree.xpath('//div/span[@class="days"]/text()')
        openingHours = attraction_tree.xpath('//div/span[@class="hours"]/text()')

        # clean the result
        name = stringCleaner(names)
        address = stringCleaner(addresses)
        locality = stringCleaner(localities)

        attractions_out.loc[j] = [name, address, extAddress, locality, postalCode, country, openingDays, openingHours]

    return attractions_out

# attractions = tripScraper(inputPage,second_page01,second_page02)
# print(attractions)
#
# attractions.to_csv('C:/Users/Leonardo/PycharmProjects/webscraping_test/attractions_in_Oslo.csv', encoding='ISO-8859-1')
#
# forecedError

attractions = pd.read_csv('C:/Users/Leonardo/PycharmProjects/webscraping_test/attractions_in_Oslo2.csv', encoding='ISO-8859-1')
print("Found "+str(attractions.shape[0])+" attractions!")

# forecedError

# from list of lists to a single list
# attraction_addresses2 = map(str, [val for sublist in attraction_addresses for val in sublist])

print(attractions['name'].head(15))
print(attractions['address'].head(15))

# for index, row in attractions.iterrows():
#     print("Attraction: " + str(row['name']))
#     print("Address: " + str(row['address']) + ", " + str(row['locality']) + " " + str(
#         row['postalCode']) + ", " + str(row['country']))
#     print("Opening days: " + str(row['openingDays']))
#     print("Opening hours: " + str(row['openingHours']))
#     print()


all_waypoints = []
for index, row in attractions.iterrows():
    if index < 10:
        print(index)
        print(index >= 0 & index < 15)
        temp = str(row['address']) + ", " + str(row['locality'])
        all_waypoints.append(temp)

homebase = 'Gronnegata 11, Oslo'
all_waypoints.append(homebase)

print(all_waypoints)


# distance matrix algorythm
gmaps = gm.Client(key="AIzaSyDbaMbHvupYTFZwsi9w9hKezNE_x1v4ItE")

from itertools import combinations

waypoint_distances = {}
waypoint_durations = {}

for (waypoint1, waypoint2) in combinations(all_waypoints, 2):
    try:
        route = gmaps.distance_matrix(origins=[waypoint1],
                                      destinations=[waypoint2],
                                      mode="walking",  # Change this to "walking" for walking directions,
                                      # "bicycling" for biking directions, etc.
                                      language="English",
                                      units="metric")

        # "distance" is in meters
        distance = route["rows"][0]["elements"][0]["distance"]["value"]

        # "duration" is in seconds
        duration = route["rows"][0]["elements"][0]["duration"]["value"]

        waypoint_distances[frozenset([waypoint1, waypoint2])] = distance
        waypoint_durations[frozenset([waypoint1, waypoint2])] = duration

    except Exception as e:
        print("Error with finding the route between %s and %s." % (waypoint1, waypoint2))

print(waypoint_distances)
print(waypoint_durations)

with open("my-waypoints-dist-dur.tsv", "w") as out_file:
    out_file.write("\t".join(["waypoint1",
                              "waypoint2",
                              "distance_m",
                              "duration_s"]))

    for (waypoint1, waypoint2) in waypoint_distances.keys():
        out_file.write("\n" +
                       "\t".join([waypoint1,
                                  waypoint2,
                                  str(waypoint_distances[frozenset([waypoint1, waypoint2])]),
                                  str(waypoint_durations[frozenset([waypoint1, waypoint2])])]))


