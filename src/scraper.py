import traceback
from botasaurus import *
from botasaurus.cache import DontCache
from src.extract_data import extract_data
from src.scraper_utils import create_search_link, perform_visit
from src.utils import convert_unicode_dict_to_ascii_dict, unique_strings
from .reviews_scraper import GoogleMapsAPIScraper
from time import sleep, time
from botasaurus.utils import retry_if_is_error
from selenium.common.exceptions import  StaleElementReferenceException
'''
1. Hàm process_reviews:

Trích xuất các trường dữ liệu mong muốn từ một danh sách reviews về các đánh giá của địa điểm.
Chuyển đổi một số trường dữ liệu như số ảnh và số đánh giá của người dùng từ chuỗi sang số nguyên.
Xử lý trường likes (số thích): nếu bằng -1 thì đặt về 0, nếu không thì giữ nguyên giá trị.
Thêm các trường mới như tổng số đánh giá và ảnh của người dùng, URL người dùng, cờ đánh dấu là hướng dẫn viên địa phương, bản dịch các trường đánh giá và phản hồi (nếu cần).
Trả về danh sách các đánh giá đã được xử lý, có thể tùy chọn chuyển đổi sang mã ASCII.
'''
def process_reviews(reviews, convert_to_english):
    processed_reviews = []

    for review in reviews:
        # Convert user_photos and user_reviews to integers, handling None and commas
        user_photos = review.get("user_photos")
        number_of_photos_by_reviewer = user_photos
        # int(user_photos.replace(",", "").replace(".", "")) if user_photos else 0

        user_reviews = review.get("user_reviews")
        number_of_reviews_by_reviewer = user_reviews
        # int(user_reviews.replace(",", "").replace(".", "")) if user_reviews else 0

        lk = review.get("likes")
        processed_review = {
            "review_id": review.get("review_id"),
            "reviewer_name": review.get("user_name"),
            "rating": int(review.get("rating")),
            "review_text": review.get("text"),
            "published_at": review.get("relative_date"),
            "published_at_date": review.get("text_date"),
            "response_from_owner_text": review.get("response_text"),
            "response_from_owner_ago": review.get("response_relative_date"),
            "response_from_owner_date": review.get("response_text_date"),
            "review_likes_count": 0 if lk == -1 else lk,
            "total_number_of_reviews_by_reviewer": number_of_reviews_by_reviewer,
            "total_number_of_photos_by_reviewer": number_of_photos_by_reviewer,
            "reviewer_url": review.get("user_url"),
            "is_local_guide": review.get("user_is_local_guide"),
            "review_translated_text": review.get("translated_text"),
            "response_from_owner_translated_text": review.get("translated_response_text"),
            # "extracted_at": review.get("retrieval_date")
        }
        processed_reviews.append(processed_review)

    if convert_to_english:
        return convert_unicode_dict_to_ascii_dict(processed_reviews)
    else:
        return processed_reviews


@request(

    close_on_crash=True,
    output=None,

)

# 2. Hàm scrape_reviews:

# Nhận các tham số requests (instance của lớp AntiDetectRequests) và data chứa thông tin về địa điểm cần cào đánh giá.
# Trích xuất các tham số cần thiết như ID địa điểm, URL, số lượng đánh giá tối đa, kiểu sắp xếp và ngôn ngữ từ data.
# Sử dụng lớp GoogleMapsAPIScraper để cào dữ liệu đánh giá từ Google Maps với các tham số đã nêu.
# Gọi hàm process_reviews để xử lý và làm sạch dữ liệu đánh giá thu được.
# Trả về một kết quả chứa ID địa điểm và danh sách đánh giá đã được xử lý.

def scrape_reviews(requests: AntiDetectRequests, data):
    place_id = data["place_id"]
    link = data["link"]

    max_r = data["max"]

    reviews_sort = data["reviews_sort"]
    lang = data["lang"]
    convert_to_english = data["convert_to_english"]
    
    processed = []
    with GoogleMapsAPIScraper() as scraper:

        result = scraper.scrape_reviews(
            link,  max_r, lang, sort_by=reviews_sort
        )
        processed = process_reviews(result, convert_to_english)
    
    return {"place_id":place_id, "reviews": processed}


cookies = None
def get_cookies():
         global cookies
         return cookies

def set_cookies(ck):
         global cookies
         cookies = ck

@request(
    parallel=5,
    async_queue=True,

    close_on_crash=True,
    output=None,

    # TODO: IMPLEMENT AND UNCOMMENT
    max_retry=5,
    # retry_wait=30, {ADD}
    # request_interval=0.2, {ADD}

)

# 3. Hàm scrape_place:

# Nhận các tham số requests và link (URL của địa điểm).
# Lấy cookie đã lưu trước đó.
# Thực hiện truy cập trang web theo URL, trích xuất nội dung HTML.
# Tách nội dung HTML để tìm và lấy phần chứa dữ liệu JavaScript được lưu trữ trong biến app_initialization_state.
# Gọi hàm extract_data (chưa được cung cấp giải thích) để trích xuất dữ liệu mong muốn từ app_initialization_state.
# Thêm trường is_spending_on_ads cho biết địa điểm có đang chạy quảng cáo hay không (giá trị mặc định là False).
# Trả về dữ liệu đã trích xuất và làm sạch.
# Xử lý ngoại lệ bằng cách ngủ 63 giây và raise lỗi.

def scrape_place(requests: AntiDetectRequests, link):
        cookies = get_cookies()
        try:
            html =  requests.get(link,cookies=cookies,).text
            # Splitting HTML to get the part after 'window.APP_INITIALIZATION_STATE='
            initialization_state_part = html.split(';window.APP_INITIALIZATION_STATE=')[1]

            # Further splitting to isolate the APP_INITIALIZATION_STATE content
            app_initialization_state = initialization_state_part.split(';window.APP_FLAGS')[0]

            # Extracting data from the APP_INITIALIZATION_STATE
            data = extract_data(app_initialization_state, link)
            # data['link'] = link

            data['is_spending_on_ads'] = False
            cleaned = data
            
            return cleaned  
        except:
            sleep(63)
            raise

# 4. Hàm merge_sponsored_links:

# Duyệt qua danh sách các địa điểm.
# Đánh dấu các địa điểm có URL nằm trong danh sách liên kết tài trợ (tham số sponsored_links).
# Trả về danh sách các địa điểm đã được đánh dấu.
def merge_sponsored_links(places, sponsored_links):
    for place in places:
        place['is_spending_on_ads'] = place['link'] in sponsored_links

    return places

@browser(
    block_images=True,
    reuse_driver=True,
    keep_drivers_alive=True, 
    close_on_crash=True,
    headless=True,
    output=None,
)

# 5. Hàm scrape_places_by_links:

# Nhận các tham số driver (instance của AntiDetectDriver) và data chứa danh sách URL các địa điểm và tùy chọn chuyển đổi sang tiếng Anh.
# Khởi tạo instance của scrape_place bằng cách sử dụng AsyncQueueResult.
# Lấy cookie từ trình duyệt và lưu vào biến toàn cục.
# Gọi hàm scrape_place_obj.put để đưa danh sách URL vào hàng đợi xử lý của scrape_place.
# Chờ kết quả từ hàng đợi và gán vào biến places.
# Lấy danh sách liên kết tài trợ (nếu có).
# Đánh dấu các địa điểm có URL nằm trong danh sách liên kết tài trợ.
# Thực hiện chuyển đổi sang tiếng Anh (nếu cần).
# Trả về danh sách các địa điểm đã được xử lý.
def scrape_places_by_links(driver: AntiDetectDriver, data):
    # get's the cookies accepted which scraper needs.
    driver.get_google(True)
    set_cookies(driver.get_cookies_dict())

    links = data["links"]
    cache = data["cache"]
    
    scrape_place_obj: AsyncQueueResult = scrape_place(cache=cache)
    convert_to_english = data['convert_to_english']

    scrape_place_obj.put(links)
    places = scrape_place_obj.get()

    sponsored_links = []
    places = merge_sponsored_links(places, sponsored_links)

    if convert_to_english:
        places = convert_unicode_dict_to_ascii_dict(places)

    return places 

class StuckInGmapsException(Exception):
    pass


def get_lang(data):
     return data['lang']

@browser(
    block_images=True,
    reuse_driver=True,
    keep_drivers_alive=True, 
    lang=get_lang,
    close_on_crash=True,
    headless=True,
    output=None,
)

# 6. Hàm scrape_places:

# Nhận các tham số driver và data chứa thông tin về địa điểm cần cào, ngôn ngữ, tùy chọn chi tiêu cho quảng cáo và chuyển đổi sang tiếng Anh.
# Khởi tạo instance của scrape_place bằng cách sử dụng AsyncQueueResult.
# Định nghĩa hàm nội bộ get_sponsored_links để lấy danh sách liên kết tài trợ từ JavaScript nếu cần.
# Định nghĩa hàm put_links để thực hiện các bước sau:
# Thực hiện lặp để cuộn xuống trang kết quả và lấy các URL của các địa điểm.
# Kiểm tra điều kiện số lượng địa điểm tối đa (nếu có).
# Đưa danh sách URL vào hàng đợi của scrape_place nếu không phải liên kết tài trợ.
# Kiểm tra điều kiện cuộn trang đã đến cuối hay chưa.
def scrape_places(driver: AntiDetectDriver, data):
    
    # This fixes consent Issues in Countries like Spain 
    max_results = data['max']
    is_spending_on_ads = data['is_spending_on_ads']
    convert_to_english = data['convert_to_english']

    scrape_place_obj: AsyncQueueResult = scrape_place()

    sponsored_links = None
    def get_sponsored_links():
         nonlocal sponsored_links
         if sponsored_links is None:
              sponsored_links = driver.execute_file('get_sponsored_links.js')
         return sponsored_links



    def put_links():
                start_time = time()
                
                WAIT_TIME = 40 # WAIT 40 SECONDS

                while True:
                    el = driver.get_element_or_none_by_selector(
                        '[role="feed"]', bt.Wait.LONG)
                    if el is None:
                        if driver.is_in_page("/maps/search/"):
                        # No Feeds Eg: https://www.google.com/maps/search/this+should+retuen+absolutely+mothoing+hahahahahahaha/@37.6,-95.665,4z?entry=ttu
                            rst = []
                        elif driver.is_in_page("/maps/place/"):
                            rst = [driver.current_url]
                            scrape_place_obj.put(rst)
                        return
                    else:
                        did_element_scroll = driver.scroll_element(el)

                        links = None
                        
                        if max_results is None:
                            links = driver.links(
                                '[role="feed"] >  div > div > a', bt.Wait.LONG)
                        else:
                            links = unique_strings(driver.links(
                                '[role="feed"] >  div > div > a', bt.Wait.LONG))[:max_results]
                                                    
                        
                        if is_spending_on_ads:
                            scrape_place_obj.put(get_sponsored_links())
                            return 
                            
                        scrape_place_obj.put(links)


                        if max_results is not None and len(links) >= max_results:
                            return

                        end_el = driver.get_element_or_none_by_selector(
                            "p.fontBodyMedium > span > span", bt.Wait.SHORT)

                        if end_el is not None:
                            driver.scroll_element(el)
                            return
                        elapsed_time = time() - start_time

                        if elapsed_time > WAIT_TIME :
                            print('Google Maps was stuck in scrolling. Retrying.')
                            sleep(63)
                            raise StuckInGmapsException()                           
                            # we increased speed so occurence if higher than 
                            #   - add random waits
                            #   - 3 retries  
                             
                        if did_element_scroll:
                            start_time = time()
                        else:
                            sleep_time = 0.1
                            sleep(sleep_time)
    
    search_link = create_search_link(data['query'], data['lang'], data['geo_coordinates'], data['zoom'])
    
    perform_visit(driver, search_link)
    
    set_cookies(driver.get_cookies_dict())
    
    RETRIES = 5
    failed_to_scroll = False
    def on_failed_after_retry_exhausted(e):
        nonlocal failed_to_scroll
        failed_to_scroll = True
        print('Failed to scroll after 5 retries. Skipping.')

    retry_if_is_error(put_links, [StaleElementReferenceException, StuckInGmapsException], RETRIES, raise_exception=False, on_failed_after_retry_exhausted=on_failed_after_retry_exhausted)

    places = scrape_place_obj.get()

    sponsored_links = get_sponsored_links() 
    places = merge_sponsored_links(places, sponsored_links)
    
    if convert_to_english:
        places = convert_unicode_dict_to_ascii_dict(places)

    result = {"query": data['query'], "places": places}
    
    if failed_to_scroll:
        DontCache(result)
    return result 

if __name__ == "__main__":
    print(scrape_places(["restaurants in delhi"]))

