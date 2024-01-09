from src.gmaps import Gmaps
import time
import pandas as pd
from casefy import kebabcase

#coordinates = pd.read_excel(r"C:\Users\thinh.lv\google-maps-scraper\src\xlsx\coordinates-quan4-hcm.xlsx")
#coordinates = pd.read_excel(r"C:\Users\thinh.lv\google-maps-scraper\src\xlsx\coordinates-quan4-hcm_v2.xlsx")
#coordinates = pd.read_excel(r"C:\Users\thinh.lv\google-maps-scraper\src\xlsx\coordinates-quan4-hcm_v3.xlsx")[:21]
#geo_coordinates  = [i for i in coordinates["lat_long"]]
geo_coordinates  = ["10.766718704539583, 106.70581695774777",
"10.755124520426056, 106.71560165627074",
"10.76256592984892, 106.70317766406723",
"10.75870822494212, 106.70802709798431",
"10.758834707852863, 106.70379993656103",
"10.76014169482375, 106.7002379629759",
"10.757527715216838, 106.69637558197999",
"10.754492097561803, 106.69144031737412",
"10.755124520426056, 106.69659015870201",
"10.754934793706006, 106.7007958624531",
"10.755061278199292, 106.7008173201253",
"10.755630457762761, 106.70622465351957",
"10.75535640847738, 106.71083805304245",
"10.756916378007153, 106.71746847375209",
"10.759150914897612, 106.71345588905079",
"10.759129834438275, 106.71347734672298",
"10.7613854352284, 106.70963642339929",
"10.764146942187658, 106.70581695774777"]
#geo_coordinates  = ["10.775300838611173, 106.70388693195741"]
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


queries = ["túi"
           ]
max = 10
zoom = 19
Gmaps.places(queries, geo_coordinates = geo_coordinates, zoom = zoom , max = max, fields=fields, convert_to_english = False ,lang=Gmaps.Lang.Vietnamese)

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Thời gian chạy: {elapsed_time/60} phút")

xl = kebabcase(queries[0]) + "-" + str(max)
df = pd.read_csv(f"C:/Users/thinh.lv/google-maps-scraper/output/quan4_hcm_bo_sung/{xl}/csv/places-of-{xl}.csv").drop_duplicates()
print(f"Số dòng: {df.shape[0]}")
df.to_excel(f"C:/Users/thinh.lv/google-maps-scraper/src/xlsx/quan4_hcm_bo_sung/{queries[0]}.xlsx")
