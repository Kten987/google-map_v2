import requests

def get_location(address):
    api_key = "mwA5L1GvWFvnwIYL-U1kP0RDsZ61ElOKAH7wnbsTs4M"

    url = f'https://geocode.search.hereapi.com/v1/geocode?q={address}&apiKey={api_key}'
    
    try:
        # Gửi yêu cầu API
        response = requests.get(url)

        data = response.json()    
        # Xử lý kết quả và trả về
        if data == {'items': []}: 
          list_address = {"lat": "", "lng": "", "House_number": "", "Street": "", "Ward": "", "District": "", "City": "", "progress": "True" }
        else: 
          result = data['items'][0]
          position = result['position']
          lat = position.get('lat', '')
          long = position.get('lng', '')
          address_info = result['address']
          city = address_info.get('county', '')
          district = address_info.get('city', '')
          ward = address_info.get('district', '')
          street = address_info.get('street', '')
          houseNumber = address_info.get('houseNumber', '')
          list_address = {"lat": lat, "lng": long, "House_number": houseNumber, "Street": street, "Ward": ward, "District": district, "City": city, "progress": "True" }
    except:
           # Nếu thử xảy ra lỗi trả ra tập rỗng và progess là False đánh dấu những case chưa xử lí
        list_address = {"lat": "", "lng": "", "House_number": "", "Street": "", "Ward": "", "District": "", "hCity": "", "progress": "False" }
           
    return list_address
