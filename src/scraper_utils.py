import urllib.parse
from botasaurus import AntiDetectDriver

def perform_visit(driver: AntiDetectDriver, link:str):
    def visit_gmap_with_consent():
        """
        Truy cập vào trang Google Maps với sự đồng ý của người dùng.

        Hàm này sử dụng trình duyệt để truy cập vào liên kết được cung cấp và chấp nhận các cookie.
        Nếu trang hiển thị yêu cầu đồng ý của người dùng, hàm sẽ tự động nhấp vào nút đồng ý.
        Sau đó, hàm sẽ tiếp tục truy cập vào liên kết ban đầu.

        """
        driver.organic_get(link, accept_cookies=True)
        
    def visit_gmap_simple():
                    driver.get_by_current_page_referrer(link)
     

    if driver.about.is_new:
        visit_gmap_with_consent()
    else: 
        visit_gmap_simple()
        
def remove_spaces(input_string):
    # Use str.replace() to replace spaces with an empty string
    result_string = input_string.replace(" ", "")
    return result_string

def create_search_link(query: str, lang, geo_coordinates: str, zoom):
    # Check for invalid combination of geo_coordinates and zoom
    if geo_coordinates is None and zoom is not None:
        raise ValueError("geo_coordinates must be provided along with zoom")

    # URL encoding the query
    endpoint = urllib.parse.quote_plus(query)

    # Basic parameters
    params = {
            'authuser': '0',
            'hl': lang,
            'entry': 'ttu',

    } if lang is not None else {
            'authuser': '0',
            'entry': 'ttu',
          
    }


    # Constructing the geo-coordinates string
    geo_str = ""
    if geo_coordinates is not None:
        if zoom is not None:
            geo_str = f'/@{remove_spaces(geo_coordinates)},{zoom}z'
        else:
            geo_str = f'/@{remove_spaces(geo_coordinates)}'

    # Constructing the final URL
    url = f'https://www.google.com/maps/search/{endpoint}'
    if geo_str:
        url += geo_str
    url += f'?{urllib.parse.urlencode(params)}'

    return url

'''Hàm create_search_link được sử dụng để tạo ra một liên kết tìm kiếm trên Google Maps dựa trên các thông tin đầu vào như query (câu truy vấn), lang (ngôn ngữ), geo_coordinates (tọa độ địa lý), và zoom (mức độ phóng to).

Đầu tiên, hàm kiểm tra xem có sự kết hợp không hợp lệ giữa geo_coordinates và zoom hay không. Nếu geo_coordinates là None (không có tọa độ địa lý được cung cấp) và zoom không phải là None (có mức độ phóng to được cung cấp), hàm sẽ raise một ValueError với thông báo "geo_coordinates must be provided along with zoom".

Tiếp theo, hàm sử dụng urllib.parse.quote_plus để mã hóa URL của query (câu truy vấn) để đảm bảo nó được truyền đi một cách an toàn trong URL.

Sau đó, hàm xây dựng các tham số cơ bản cho URL, bao gồm 'authuser', 'hl' (ngôn ngữ), và 'entry'. Nếu lang không phải là None, các tham số này sẽ được thiết lập, ngược lại, chỉ có 'authuser' và 'entry' được thiết lập.

Tiếp theo, hàm xây dựng chuỗi tọa độ địa lý (geo_str) dựa trên geo_coordinates và zoom. Nếu geo_coordinates không phải là None, hàm sẽ kiểm tra xem zoom có khác None hay không. Nếu có, geo_str sẽ được xây dựng với định dạng '/@{remove_spaces(geo_coordinates)},{zoom}z', ngược lại, geo_str sẽ được xây dựng với định dạng '/@{remove_spaces(geo_coordinates)}'.

Cuối cùng, hàm xây dựng URL cuối cùng bằng cách kết hợp endpoint (URL đã được mã hóa), geo_str (nếu có), và các tham số cơ bản. URL cuối cùng được trả về từ hàm.'''

