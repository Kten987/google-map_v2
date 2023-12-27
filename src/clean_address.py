import requests


def get_location(list_address, api_key):
    address_info_list = []
    for address in list_address:
        url = f'https://geocode.search.hereapi.com/v1/geocode?q={address}&apiKey={api_key}'

        try:
            # Gửi yêu cầu API
            response = requests.get(url)

            # Khởi tạo output_address trước khi thử nghiệm điều kiện
            output_address = {"lat": "", "lng": "", "House_number": "", "Street": "", "Ward": "", "District": "", "City": "", "progress": "False"}

            if response.status_code == 429:
                return output_address

            data = response.json()    
            # Xử lý kết quả và trả về
            if data == {'items': []}: 
                output_address["progress"] = "True"
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
                output_address = {"lat": lat, "lng": long, "House_number": houseNumber, "Street": street, "Ward": ward, "District": district, "City": city, "progress": "True"}
        except:
            # Nếu thử xảy ra lỗi trả ra tập rỗng và progess là False đánh dấu những case chưa xử lí
            pass
        
        address_info_list.append(output_address)
    return address_info_list


address_info = get_location(df2["address"], "mwA5L1GvWFvnwIYL-U1kP0RDsZ61ElOKAH7wnbsTs4M")
address_df = pd.DataFrame(address_info_list)
df10 = pd.concat([df2, address_df], axis=1)

    
