from soft_webauthn import SoftWebauthnDevice
import requests
from base64 import urlsafe_b64decode
import json

ENDPOINT = "http://localhost:18488"


class User:
    def __init__(self):
        self.endpoint = ENDPOINT
        self.device = SoftWebauthnDevice()
        self.cookies = None

    def register(self, user_handle="load", credential_id=b"d2hhdGV2ZXI"):
        self.user_handle = user_handle
        self.credential_id = credential_id
        g = requests.get(ENDPOINT + f"/webauthn/register?username={self.user_handle}")
        gdata = g.json()
        cookies = g.cookies
        print(g.status_code, gdata)
        if g.status_code == 200:
            options = gdata["options"]
            options = {"publicKey": options}
            send = self.device.create(options, ENDPOINT, credential_id)
            send = json.dumps(send).replace(" ", "")
            print(send)
            p = requests.post(
                ENDPOINT + f"/webauthn/register?username={self.user_handle}",
                cookies=cookies,
                data=send,
            )
            self.cookies = p.cookies
            data2 = p.json()
            print(data2)
            if data2["status"] == "success":
                return True
        return False

    def login(self):
        g = requests.get(ENDPOINT + "/webauthn/authenticate", cookies=self.cookies)
        self.cookies = g.cookies
        gdata = g.json()
        print(g.status_code, gdata)
        if g.status_code == 200:
            options = gdata["options"]
            options = {"publicKey": options}
            print(options)
            send = self.device.get(options, ENDPOINT)
            print(send)
            send = json.dumps(send).replace(" ", "")
            print(send)
            p = requests.post(
                ENDPOINT + "/webauthn/authenticate", cookies=self.cookies, data=send
            )
            self.cookies = p.cookies
            pdata = p.json()
            print(pdata)
            if pdata["status"] == "success":
                g = requests.get(ENDPOINT, cookies=self.cookies)
                print(g.text)
                return True
        return False


# admin_credential_id = os.urandom(32)
admin_credential_id = urlsafe_b64decode("A_YlIOO3wkK4atDx6AFEQs67XLs==")
admin_public_key = "pQECAyYgASFYIHnavLt4MJVMclG5EFmEmA1qr_RbK8L2Xe1YLAhC5qWDIlgg6elGbeMWs78q3NnpLPbX1DletP2nrPXTXWm5fp-Lz5o"

u = User()
r = u.register(user_handle="inu888", credential_id=admin_credential_id)
print(r)
r = u.login()
print(r)
