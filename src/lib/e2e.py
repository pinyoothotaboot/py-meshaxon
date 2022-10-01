import uuid
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto import Random

class EndToEndEncrypt(object):

    def __init__(self): 
        self.bs = AES.block_size
        self.key = ""

    def get_salt(self):
        return str(uuid.uuid4())
    
    def payload(self,enc_message,salt):
        return {
            "enc_message" : enc_message,
            "salt" : str(salt)
        }
    
    def get_key(self,payload,salt):
        try:
            to_user = payload['to']
            from_user = payload['from']
            key = "{}:{}:{}".format(to_user,from_user,salt)
            self.key = hashlib.sha256(key.encode()).digest()
            return self.key
        except KeyError as ke:
            print("Key error : {}".format(ke))
            return ""
        except ValueError as ve:
            print("Value error : {}".format(ve))
            return ""

    def encrypt(self, raw,key):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc,key):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

if __name__ == "__main__":
    try:
        payload = {
            "to" : "user_01",
            "from" : "user_02",
            "message" : "Hello World"
        }

        e2e = EndToEndEncrypt()
        salt = e2e.get_salt()
        key = e2e.get_key(payload,salt)
        print("SALT :",salt)
        print("KEY  :",key)
        enc_message = e2e.encrypt("Hello World",key)
        enc_payload = e2e.payload(enc_message.decode(),key)
        print("enc message",enc_message)
        print("enc payload",enc_payload)
        dec_message = e2e.decrypt(enc_message,key)
        print("dec message",dec_message)
    except KeyboardInterrupt:
        print("Exit process...")


    
