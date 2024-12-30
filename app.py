import logging
import datetime
import json
from flask_cors import CORS
from flask import Flask
from node import node_bp
from link import link_bp
from subcatchments import subcatchments_bp
from swmm_model import swmm_model_bp
from timeseries import timeseries_bp

public_path = '/hrw/swmm/api/'

app = Flask(__name__)

CORS(app, resources=r'/*')
# Load configuration from JSON file
with open('config.json') as config_file:
    config_data = json.load(config_file)

app.config.update(config_data)
# 注册蓝图
version = app.config['VERSION']
app.register_blueprint(node_bp, url_prefix=public_path + version)
app.register_blueprint(subcatchments_bp, url_prefix=public_path + version)
app.register_blueprint(swmm_model_bp, url_prefix=public_path + version)
app.register_blueprint(link_bp, url_prefix=public_path + version)
app.register_blueprint(timeseries_bp, url_prefix=public_path + version)
# 配置日志记录
logging.basicConfig(level=logging.ERROR)  # 设置日志级别为DEBUG

# 创建Formatter对象并配置格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


# 要求认证的路由
@app.route('/')
def home():
    return 'Welcome! You are authenticated.'


if __name__ == '__main__':
    filename = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m')
    handler = logging.FileHandler('logs/' + filename + '.log')
    handler.formatter = formatter
    app.logger.addHandler(handler)
    app.run(debug=True, host='0.0.0.0', port=9990)
