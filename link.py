from flask import jsonify, request, Blueprint, current_app as app
from pyswmm import Simulation, Links
from swmm_api import SwmmInput
from swmm_api.input_file.section_labels import PUMPS

link_bp = Blueprint('link', __name__)


# 查询节点列表
@link_bp.route('/link', methods=['GET'])
def get_link_data():
    # 获取查询参数
    model_name = request.args.get('model_name')
    link_type = request.args.get('link_type')
    print(link_type)
    data = []
    sim = Simulation(app.config["MODEL_PATH"] + model_name + '.inp')
    link_attribute = app.config["Link_ATTRIBUTE"]
    if link_type is None:
        for link1 in Links(sim):
            d = {"link_id": link1.linkid, 'link_type': get_link_type(link1)}
            data.append(d)
            for att in link_attribute:
                d[att] = getattr(link1, att)
    else:
        for link1 in Links(sim):
            if judge_link_type(link_type, link1):
                d = {"link_id": link1.linkid, 'link_type': link_type}
                data.append(d)
                for att in link_attribute:
                    d[att] = getattr(link1, att)
    return jsonify({"data": data, 'code': 200, 'msg': '请求成功'})


def get_link_type(link1):
    if link1.is_pump():
        link_type = "pump"
    elif link1.is_weir():
        link_type = 'weir'
    elif link1.is_outlet():
        link_type = 'outlet'
    elif link1.is_orifice():
        link_type = 'orifice'
    else:
        link_type = "conduit"
    return link_type


# 判断节点类型是否是需要的类型
def judge_link_type(link_type, link1):
    bl = False
    if link_type == "conduit":
        bl = link1.is_conduit()
    elif link_type == 'weir':
        bl = link1.is_weir()
    elif link_type == 'orifice':
        bl = link1.is_orifice()
    elif link_type == 'outlet':
        bl = link1.is_outlet()
    elif link_type == 'pump':
        bl = link1.is_pump()
    return bl


# 查询模拟结果   节点对应的时间序列数据
@link_bp.route('/link/results', methods=['GET'])
def get_link_sim_data():
    # 获取查询参数
    data_id = request.args.get('id')
    index = request.args.get('index')
    app.logger.info('data_id is %s', data_id)
    model_name = request.args.get('model_name')
    if index is None:
        return jsonify({"msg": "需要指定查询对象的指标名称，参数名称为index"})
    data = []
    with Simulation(app.config["MODEL_PATH"] + model_name + '.inp') as sim:
        j1 = Links(sim)[data_id]
        print(sim.start_time)
        for ind, step in enumerate(sim):
            a = getattr(j1, index)
            print(a)
            if a is not None:
                data.append(
                    {"current_time": sim.current_time.strftime("%Y-%m-%d %H:%M:%S"), index: a})
            else:
                data.append(
                    {"current_time": sim.current_time.strftime("%Y-%m-%d %H:%M:%S"), index: None})
    return jsonify({"data": data, 'code': 200, 'msg': '查询成功'})


# 更新泵的属性
@link_bp.route('/link/pump', methods=['POST'])
def update_link_data():
    # 获取查询参数
    try:
        params = request.json
        pump_id = params.get('id')
        attr_name = params.get('attribute_name')
        attr_value = params.get('attribute_value')
        model_name = params.get('model_name')
        model_path = app.config["MODEL_PATH"] + model_name + '.inp'
        inp = SwmmInput.read_file(model_path)
        inp[PUMPS][pump_id][attr_name] = attr_value
        inp.write_file(model_path)
        return jsonify({'code': 200, 'msg': '更新成功'})
    except Exception as e:
        app.logger.error("An unexpected error occurred: %s", e)
        return jsonify({'msg': '更新失败' + str(e)})
