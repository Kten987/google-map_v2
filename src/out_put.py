from src.gmaps import Gmaps
import time
import pandas as pd
from casefy import kebabcase

def out_put(queries,max):
   start_time = time.time()
   fields = [
      Gmaps.Fields.PLACE_ID, 
      Gmaps.Fields.NAME, 
      Gmaps.Fields.MAIN_CATEGORY, 
      Gmaps.Fields.PHONE, 
      Gmaps.Fields.ADDRESS,
      Gmaps.Fields.DETAILED_ADDRESS
   ]

   geo_coordinates = ["10.060336116445198, 105.7793725804415",
   "10.041776517690092, 105.79192278333913",
   "10.04857477707304, 105.78772157139154",
   "10.046438333359838, 105.78541529587908",
   "10.043633281202343, 105.78045937648928",
   "10.049551318433437, 105.76583895228515",
   "10.043779838092576, 105.75921778804167",
   "10.01983383968098, 105.74235539675001",
   "10.00934560594884, 105.72024872964793",
   "10.002303020043968, 105.7359847383653",
   "10.011664591261276, 105.74762846869369",
   "10.021279018641684, 105.75691964079013",
   "10.01557378840652, 105.76256300844409",
   "10.033502984314048, 105.76832508554213",
   "10.035510730486168, 105.78333742691751"]

   Gmaps.places(queries, geo_coordinates = geo_coordinates, zoom = 18 , max = max, fields=fields, convert_to_english = False ,lang=Gmaps.Lang.Vietnamese)

   end_time = time.time()
   elapsed_time = end_time - start_time

   print(f"Thời gian chạy: {elapsed_time/60} phút")

