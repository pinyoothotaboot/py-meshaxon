
import redis
from .log import Logger

log = Logger('REDIS').get_logger()

class Redis:
    def __init__(self,host="127.0.0.1",port=6379):
        self.host = host
        self.port = port
        self.redis = None
        self.has_online = False
        self.publisher = None
        self.subscriber = None

        self.connect()
    
    def connect(self):
        try:
            for idx in range(10):
                self.redis = redis.Redis(host=self.host,port=self.port)
                if self.redis is not None:
                    self.has_online = True
                    log.info("Connected redis -> {}:{}".format(self.host,self.port))
                    break
        except Exception as ex:
            log.error("Has problem redis connection : {}".format(ex))
    
    def intial_publisher(self):
        if self.redis is not None:
            self.publisher = self.redis.pubsub()
            log.info("Intial redis publisher successed")
    
    def get_has_online(self):
        return self.has_online
    
    def subscribe(self,topic):
        if not topic:
            log.warning("Not found topic to subscribe")
            return
        
        if self.redis is not None:
            self.subscriber = self.redis.pubsub()
            self.subscriber.subscribe(topic)
            log.info("Redis subscribe topic : {} successed".format(topic))
    
    def unsubscribe(self,topic):
        if not topic:
            if self.subscriber is not None:
                self.subscriber.unsubscribe()
                log.info("Unsubscribe all successed")
        else:
            if self.subscriber is not None:
                self.subscriber.unsubscribe(topic)
                log.info("Unsubscribe topic : {} successed".format(topic))
    
    def publish(self,topic,payload):
        if not topic and not payload:
            log.warning("Topic or Pyload has empty!.")
            return
        
        if self.redis is None:
            self.connect()
        
        self.redis.publish(topic,payload)
        log.info("Redis publish topic : {} , payload : {} successed".format(topic,payload))
    
    def get_payload(self):
        if self.subscriber is not None:
            return self.subscriber.get_message()
    
    def disconnect(self):
        try:
            if self.subscriber is not None:
                self.unsubscribe()
                self.subscriber.close()
                log.info("Disconnect redis successed")
                self.has_online = False
        except Exception as ex:
            log.error("Cannot disconnect redis : {}".format(ex))


        




