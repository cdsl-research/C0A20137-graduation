#frontに負荷
import base64
from locust import HttpUser, task, between
import random
import time
import string

def randomname(n):
        randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
        return ''.join(randlst)

class WebUser(HttpUser):
    @task
    def load(self):

        ut = time.time()

        headers = {'Content-Type': 'application/json'}
        payload = {
            "Username": randomname(10),  # ユーザネーム
            "First name": "tarou",  #ファーストネーム
            "Last name": "kouka",  #ラストネーム
            "Email": "abc@abc",  # メアド
            "Password": "password123"  # パスワード
        }

        payload_address = {
                "number": "1404-1",
                "street": "katakuramachi",
                "city": "hachiouji",
                "postcode": "1920982",
                "country": "japan"
            }
        
        payload_payment = {
                "longNum": "1234567890123456",
                "expires": "12/24",
                "ccv": "123"
            }

        # catalogue = self.client.get("/catalogue").json()

        ## delete Holy
        # count = 0
        # for dic in catalogue:
        #     if dic['name'] == 'Holy':
        #         catalogue.pop(count)
        #     count += 1


        # category_item = random.choice(catalogue)
        # item_id = category_item["id"]

        self.client.get("/")
        time.sleep(3)
        self.client.post("/register", json=payload, headers=headers)
        time.sleep(3)
        # self.client.get("/category.html")
        # time.sleep(3)
        # self.client.get("/detail.html?id={}".format(item_id))
        # time.sleep(3)
        # self.client.delete("/cart")
        # time.sleep(3)
        # self.client.post("/cart", json={"id": item_id, "quantity": 1})
        # time.sleep(3)
        # self.client.get("/basket.html")
        # time.sleep(3)
        # self.client.post("/addresses", json=payload_address, headers=headers)
        # time.sleep(3)
        # self.client.post("/cards", json=payload_payment, headers=headers)
        # time.sleep(3)
        # self.client.post("/orders")
        # time.sleep(3)
