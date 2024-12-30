from flask import jsonify, request, Blueprint, current_app as app
from pyswmm import Simulation, Subcatchments

subcatchments_bp = Blueprint('subcatchments', __name__)


@subcatchments_bp.route('/subcatchment', methods=['GET'])
def get_subcatchments_data():
    # 获取查询参数
    model_name = request.args.get('model_name')
    data = []
    sim = Simulation(app.config["MODEL_PATH"] + model_name + '.inp')
    attributes = app.config["SUBCATCHMENT_ATTRIBUTE"]
    print(attributes)
    for aa in Subcatchments(sim):
        d = {"id": aa.subcatchmentid}
        data.append(d)
        for att in attributes:
            d[att] = getattr(aa, att)
    return jsonify({"data": data, 'code': 200, 'msg': '请求成功'})


# 查询结果数据
@subcatchments_bp.route('/subcatchment/results', methods=['POST'])
def get_subcatchments_sim_data(item=None):
    # 获取查询参数
    params = request.json
    model_name = params.get('model_name')
    data_id = params.get('id')
    attrs = params.get('index')
    data = []
    with Simulation(app.config["MODEL_PATH"] + model_name + '.inp') as sim:
        j1 = Subcatchments(sim)[data_id]
        for ind, step in enumerate(sim):
            d = {"current_time": sim.current_time.strftime("%Y-%m-%d %H:%M:%S")}
            for item in attrs:
                d[item] = getattr(j1, item)
            data.append(d)
    return jsonify({"data": data, 'code': 200, 'msg': '请求成功'})
