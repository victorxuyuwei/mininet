import redis
import threading
from mininet.log import info, error
from urllib.parse import urlparse, urlencode, parse_qs
from os.path import split

class MininetService():
    def __init__(self, net):
        self.net = net

        self.start()

    def __del__(self): 
        pass

    def start(self):
        self.thread = threading.Thread(target=self.mainLoop)
        pass

    def stop(self):
        pass

    def mainLoop(self):
        rs = redis.Redis()

        ps = rs.pubsub()
        ps.subscribe('mininet')
        for msg in ps.listen():
            info("redis message", msg)
            if not isinstance(msg.get('data'), bytes):
                continue
            command = msg.get('data').decode()

            res = self.evalCommand(command)
        
    
    def evalCommand(self, command):
        """Command is encode with urlencode with doseq=True, start with
        obj/cmd as path

        e.g. net/start, h1/run?
        """

        try:
            qs = urlparse(command)
            fullArgs = parse_qs(qs.query)
            target, func = split(qs.path)
            tgtObj = None
            if target == 'net':
                tgtObj = self.net
            else:
                tgtObj = self.net.get(target)
            
            f = getattr(tgtObj, func)
            args = fullArgs.pop('args', [])

            return f(*args, **fullArgs)

        except Exception as e:
            error(e)
        
        return ''
        
