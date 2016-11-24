import urllib
import requests
import lxml
from bs4 import BeautifulSoup
import pandas as pd

# wiki = "https://en.wikipedia.org/wiki/List_of_state_and_union_territory_capitals_in_India"
wiki = "https://www.tripadvisor.com/robots.txt"
response = requests.get(wiki)

## print(response.text)

soup = BeautifulSoup(response.text, "lxml")
# print(soup.prettify())
# print(soup.title.string + " SUPER!")

# print(soup.a)
# print(soup.find_all("a"))
# all_links = soup.find_all("a")
# for link in all_links:
#    print(link.get("href"))

all_tables = soup.find_all("table")
len(all_tables)
right_table = soup.find("table", class_ = "wikitable sortable plainrowheaders")
right_table
# print(right_table)

# Generate lists
A = []
B = []
C = []
D = []
E = []
F = []
G = []
for row in right_table.findAll("tr"):
    cells = row.findAll("td")
    states = row.findAll("th")
    if len(cells) == 6: # Only extracting table body, not heading
        A.append(cells[0].find(text=True))
        B.append(states[0].find(text=True))
        C.append(cells[1].find(text=True))
        D.append(cells[2].find(text=True))
        E.append(cells[3].find(text=True))
        F.append(cells[4].find(text=True))
        G.append(cells[5].find(text=True))

df = pd.DataFrame(A, columns=['Number'])
df['State/UT'] = B
df['Admin_Capital'] = C
df['Legislative_Capital'] = D
df['Judiciary_Capital'] = E
df['Year_Capital'] = F
df['Former_Capital'] = G
df

print(df.head(5))

# print("Hello World!")
# print("It's webscraping time!")

