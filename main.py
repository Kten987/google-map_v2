from src.gmaps import Gmaps
import time
import pandas as pd
from casefy import kebabcase

#coordinates = pd.read_excel(r"C:\Users\thinh.lv\google-maps-scraper\src\xlsx\coordinates-quan1-hcm.xlsx")
#coordinates = pd.read_excel(r"C:\Users\thinh.lv\google-maps-scraper\src\xlsx\coordinates-quan1-hcm_v2.xlsx")
coordinates = pd.read_excel(r"C:\Users\thinh.lv\google-maps-scraper\src\xlsx\coordinates-quan1-hcm_v3.xlsx")[:21]
geo_coordinates  = [i for i in coordinates["lat_long"]]
start_time = time.time()
fields = [
   Gmaps.Fields.PLACE_ID, 
   Gmaps.Fields.NAME, 
   Gmaps.Fields.MAIN_CATEGORY, 
   Gmaps.Fields.PHONE, 
   Gmaps.Fields.FACEBOOK,
   Gmaps.Fields.WEBSITE,
   Gmaps.Fields.ADDRESS,
   Gmaps.Fields.DETAILED_ADDRESS,
   Gmaps.Fields.COORDINATES,
]


queries = ["kính mắt"
           ]
max = 40

Gmaps.places(queries, geo_coordinates = geo_coordinates, zoom = 18 , max = max, fields=fields, convert_to_english = False ,lang=Gmaps.Lang.Vietnamese)

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Thời gian chạy: {elapsed_time/60} phút")

xl = kebabcase(queries[0]) + "-" + str(max)
df = pd.read_csv(f"C:/Users/thinh.lv/google-maps-scraper/output/quan1_hcm/{xl}/csv/places-of-{xl}.csv").drop_duplicates()
print(f"Số dòng: {df.shape[0]}")
df.to_excel(f"C:/Users/thinh.lv/google-maps-scraper/src/xlsx/quan1_hcm/{queries[0]}.xlsx")
