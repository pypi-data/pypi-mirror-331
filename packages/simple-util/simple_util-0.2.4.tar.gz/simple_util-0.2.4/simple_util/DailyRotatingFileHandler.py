from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
import os
import time

class DailyRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='midnight', interval=1, backupCount=0, encoding=None, delay=False, utc=False,maxBytes=10485760):
        # 获取基础文件名（不带日期）
        self.base_filename = filename
        # 初始文件名包含当前日期
        self.suffix = "%Y%m%d"
        self.baseFilename = self._get_filename()
        self.maxBytes = maxBytes
        self.tommorw = self.get_next_midnight_timestamp()
        super().__init__(
            filename=self.baseFilename,
            when=when,
            interval=interval,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay,
            utc=utc
        )
    def get_next_midnight_timestamp(self):
        # 获取当前时间
        now = datetime.now()
        
        # 计算明天的日期
        next_day = now + timedelta(days=1)
        
        # 设置时间为明天的0点0分0秒
        next_midnight = datetime(next_day.year, next_day.month, next_day.day, 0, 0, 0)
        
        # 转换为时间戳
        next_midnight_timestamp = int(next_midnight.timestamp())
        
        return next_midnight_timestamp
    def _get_filename(self):
        # 生成带日期的文件名
        return time.strftime(f"{self.base_filename}.%Y%m%d.txt.0")

    def shouldRollover(self, record):
        # 检查文件大小或日期变更
        if self.stream is None:
            self.stream = self._open()
        if self.maxBytes > 0:
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  # 文件末尾
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1
        current_time = int(time.time())
        if current_time >= self.tommorw:
            return 1
        return 0

    def doRollover(self):
        # 处理日期变更和文件大小限制
        if self.stream:
            self.stream.close()
            self.stream = None

        current_time = int(time.time())
        if current_time>=self.tommorw:
            self.baseFilename = self._get_filename()
            self.tommorw = self.get_next_midnight_timestamp()
            self.base_dir = os.path.dirname(self.baseFilename)
            os.makedirs(self.base_dir, exist_ok=True)
        else:
            
            cnt = int(self.baseFilename.split(".")[-1:][0])
            cnt +=1
            baseFile = time.strftime(f"{self.base_filename}.%Y%m%d.txt")
            dfn = f"{baseFile}.{cnt}"
            if os.path.exists(dfn):
                cnt += 1
                while True:
                    dfn = f"{baseFile}.{cnt}"
                    if not os.path.exists(dfn):
                        break
                    cnt += 1
            self.baseFilename = dfn

        if not self.delay:
            self.stream = self._open()
        
        # 更新下次滚动时间
        new_rollover_at = self.computeRollover(current_time)
        while new_rollover_at <= current_time:
            new_rollover_at += self.interval
        
        self.rolloverAt = new_rollover_at