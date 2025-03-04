import json
import logging
import os
import socket
import time
import uuid
from .DailyRotatingFileHandler import DailyRotatingFileHandler
from contextvars import ContextVar
trace_id = ContextVar("trace_id", default=None)

class TraceIdFilter(logging.Filter):
    def filter(self, record):
        tracieid = trace_id.get()
        if not tracieid:
            tracieid=uuid.uuid4().hex[:16]
            trace_id.set(tracieid)
        record.trace_id = tracieid
        
        return True
def new_trace():
    trace_id.set(uuid.uuid4().hex[:16])
def create_logger(logLeve,appName,env,filename='log/app',file_type='log',backupCount=5,maxBytes=10485760):
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            # 构建日志记录的字典
            log_record = {
                "appName":appName,
                "serverAddr":os.environ.get('IP','127.0.0.1'),
                "name": record.name,
                "cluster": env,
                "levelname": record.levelname,
                "filename": record.filename,
                "lineno": record.lineno,
                "traceId": record.trace_id,
                "message": record.getMessage(),
                "CreateTime": self.formatTime(record, self.datefmt),
                "createdOn": int(time.time() * 1000)  # 添加 Unix 时间戳
            }
            # 将字典转换为 JSON 字符串
            return json.dumps(log_record, ensure_ascii=False)
    logging.basicConfig(
        level=logLeve,
        # format='%(asctime)s %(name)s %(levelname)s (%(filename)s:%(lineno)d) - %(message)s',
        # datefmt='%Y-%m-%d %H:%M:%S'
    )
    _logger = logging.getLogger("MediaCrawler")
    _logger.setLevel(logLeve)
    # 创建一个 RotatingFileHandler 对象
    # 确保 log 目录存在
    os.makedirs('log', exist_ok=True)
    handler = DailyRotatingFileHandler(
        filename=filename,
        file_type=file_type,
        when='midnight',
        interval=300,
        backupCount=backupCount,
        maxBytes=maxBytes  # 10MB
    )
    # handler = RotatingFileHandler('log/app.txt', maxBytes=10*1024*1024, backupCount=5)
    formatter = JsonFormatter()

    # 设置日志记录级别
    handler.setLevel(logLeve)
    handler.setFormatter(formatter)
    handler.addFilter(TraceIdFilter())

    _logger.addHandler(handler)
    return _logger

def get_local_ip():
    try:
        ip = os.environ.get('IP')
        if ip:
            return ip
        # 创建一个UDP套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到一个公共的IP地址和端口（这里使用Google的公共DNS服务器）
        sock.connect(("8.8.8.8", 80))
        # 获取本地IP地址
        local_ip = sock.getsockname()[0]
    finally:
        # 关闭套接字
        sock.close()
    return local_ip