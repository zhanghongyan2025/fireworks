
import os

# 获取项目根目录路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 如果是放在 conf 目录下，获取项目根目录可能需要调整，比如：
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 定义数据文件路径常量
CERTIFICATE = os.path.join(PROJECT_ROOT, 'tests', 'data',  '123.jpg')
