
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import os


# Tạo thư mục logs nếu chưa tồn tại
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Đường dẫn đầy đủ tới file log
log_file_path = os.path.join(log_directory, "app.log")

# Thiết lập logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatLog = "[%(asctime)s], %(levelname)-8s [%(pathname)s :%(lineno)d in function %(funcName)s] %(message)s"
# Handler cho file log xoay vòng hàng ngày
file_handler = TimedRotatingFileHandler(
    log_file_path, when="midnight", interval=1, backupCount=7  # Giữ lại 7 ngày log
)
file_handler.setFormatter(logging.Formatter(
    formatLog
))

# Handler để ghi log ra console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(
    formatLog
))

# Thêm các handler vào logger
logger.addHandler(file_handler)  # Không cần gọi logging.FileHandler nữa
logger.addHandler(console_handler)
