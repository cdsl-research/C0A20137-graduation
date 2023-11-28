import base64
from locust import HttpUser, task
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

        catalogueList = [
            "3395a43e-2d88-40de-b95f-e00e1502085b",
            "510a0d7e-8e83-4193-b483-e27e09ddc34d",
            "808a2de1-1aaa-4c25-a9b9-6612e8f29a38",
            "819e1fbf-8b7e-4f6d-811f-693534916a8b",
            "837ab141-399e-4c1f-9abc-bace40296bac",
            "a0a4f044-b040-410d-8ead-4de0446aec7e",
            "d3588630-ad8e-49df-bbd7-3167f7efb246",
            "zzz4f044-b040-410d-8ead-4de0446aec7e"
        ]   #Holy以外

        item_id = random.choice(catalogueList)

        # self.client.get("/")
        # time.sleep(3)
        # self.client.post("/register", json=payload, headers=headers)
        # time.sleep(3)
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
        # self.client.post("/cards")
        # time.sleep(3)
        self.client.post("/orders")
