from flask import jsonify, request, Blueprint, current_app as app
from swmm_api import SwmmInput
from swmm_api.input_file.section_labels import JUNCTIONS
from pyswmm import Simulation, Nodes
from datetime import datetime
import time

node_bp = Blueprint('node', __name__)

# 返回码的定义
return_code = {"success": 200, "error": 400, 'internal error': 500, "not found": 404}

error_msg = '请求异常，请联系管理员'
success_msg = '请求成功'


# 发起模拟
@node_bp.route('/sim', methods=['POST'])
def start_sim():
    try:
        data = request.json
        model_name = data.get('model_name')
        start = time.time()
        with Simulation(app.config["MODEL_PATH"] + model_name + '.inp') as sim:
            sim.start_time = datetime.strptime(data.get("start_time"), "%Y-%m-%d %H:%M:%S")
            sim.end_time = datetime.strptime(data.get("end_time"), "%Y-%m-%d %H:%M:%S")
            for step in sim:
                print(sim.current_time)
        execute_time = time.time() - start
        app.logger.info("运行所花费时间 %s s", execute_time)
        return jsonify({"msg": success_msg, 'code': 200, "data": {"msg": "运行成功", "execute_time": execute_time}})
    except Exception as e:
        app.logger.error("error is %s", e)
        return jsonify({"msg": error_msg + str(e), 'code': 200})


# 查询模拟结果   节点对应的时间序列数据
@node_bp.route('/node/results', methods=['GET'])
def get_node_sim_data():
    try:
        # 获取查询参数
        data_id = request.args.get('id')
        index = request.args.get('index')
        app.logger.info('data_id is %s', data_id)
        model_name = request.args.get('model_name')
        if index is None:
            return jsonify({"msg": "需要指定查询对象的指标名称，参数名称为index"})
        data = []
        with Simulation(app.config["MODEL_PATH"] + model_name + '.inp') as sim:
            j1 = Nodes(sim)[data_id]
            print(sim.start_time)
            for ind, step in enumerate(sim):
                data.append(
                    {"current_time": sim.current_time.strftime("%Y-%m-%d %H:%M:%S"),
                     index: round(getattr(j1, index), 5)})
        return jsonify({"data": data, 'code': return_code.get("success"), 'msg': '查询成功'})
    except Exception as e:
        app.logger.error('error is %s', e)
        return jsonify({"code": 200, 'msg': error_msg})


# 查询节点列表
@node_bp.route('/node', methods=['GET'])
def get_node_data():
    # 获取查询参数
    model_name = request.args.get('model_name')
    node_type = request.args.get('node_type')
    print(node_type)
    data = []
    sim = Simulation(app.config["MODEL_PATH"] + model_name + '.inp')
    node_attribute = app.config["NODE_ATTRIBUTE"]
    if node_type is None:
        for node in Nodes(sim):
            d = {"nodeid": node.nodeid, 'node_type': get_node_type(node)}
            data.append(d)
            for att in node_attribute:
                d[att] = getattr(node, att)
    else:
        for node in Nodes(sim):
            if judge_node_type(node_type, node):
                d = {"nodeid": node.nodeid, 'node_type': node_type}
                data.append(d)
                for att in node_attribute:
                    d[att] = getattr(node, att)
    return jsonify({"data": data, 'code': return_code.get('success'), "msg": success_msg})


# 判断节点类型是否是需要的类型
def judge_node_type(node_type, node):
    bl = False
    if node_type == "junction":
        bl = node.is_junction()
    elif node_type == 'divider':
        bl = node.is_divider()
    elif node_type == 'storage':
        bl = node.is_storage()
    elif node_type == 'outfall':
        bl = node.is_outfall()
        print(bl)
    return bl


# 获取节点的类型
def get_node_type(node):
    if node.is_outfall():
        node_type = "outfall"
    elif node.is_storage():
        node_type = 'storage'
    elif node.is_divider():
        node_type = 'divider'
    else:
        node_type = "junction"
    return node_type


# 更新模型中的数据
@node_bp.route('/node/junction', methods=['POST'])
def update_node_data():
    # 获取查询参数
    try:
        data = request.json
        node_id = data.get('id')
        attr_name = data.get('attribute_name')
        attr_value = data.get('attribute_value')
        model_name = data.get('model_name')
        model_path = app.config["MODEL_PATH"] + model_name + '.inp'
        inp = SwmmInput.read_file(model_path)
        inp[JUNCTIONS][node_id][attr_name] = attr_value
        inp.write_file(model_path)
        return jsonify({'code': 200, 'msg': '更新成功'})
    except Exception as e:
        app.logger.error("An unexpected error occurred: %s", e)
        return jsonify({'msg': '更新失败' + str(e)})
