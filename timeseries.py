from flask import jsonify, request, Blueprint, current_app as app
from swmm_api.input_file.section_labels import TIMESERIES, RAINGAGES
from swmm_api import read_inp_file
from pyswmm import Simulation, RainGages

timeseries_bp = Blueprint('timeseries', __name__)

error_msg = '请求异常，请联系管理员'
success_msg = '请求成功'


# 根据类型查询对应类型的时间序列的对象名称，返回list
@timeseries_bp.route('/ts/rain', methods=["GET"])
def get_timeseries_list():
    model_name = request.args.get('model_name')
    path = app.config["MODEL_PATH"] + model_name + '.inp'
    names = []
    with Simulation(path) as sim:
        for c in RainGages(sim):
            names.append(c.raingageid)
    inp = read_inp_file(path)
    rain_gages = inp[RAINGAGES]
    data = []
    for name in names:
        rain = rain_gages[name]
        d = {'name': name, 'form': rain.form, 'interval': rain.interval, 'SCF': rain.SCF, 'source': rain.source,
             'timeseries': rain.timeseries, 'filename': rain.filename, 'station': rain.station, 'units': rain.units}
        # d['FORMATS'] = rain.FORMATS
        # d['SOURCES'] = rain.SOURCES
        # d['UNITS'] = rain.UNITS
        data.append(convert_nan_to_none(d))
    return jsonify({'msg': success_msg, 'data': data})


def convert_nan_to_none(data):
    for key, value in data.items():
        if str(value) == 'nan':
            data[key] = None
    return data


# 根据类型查询对应类型的时间序列的对象名称，返回list
@timeseries_bp.route('/ts/rain/detail', methods=["GET"])
def get_rains():
    model_name = request.args.get('model_name')
    rain_id = request.args.get('name')
    format_time = "%Y-%m-%d %H:%M:%S"
    path = app.config["MODEL_PATH"] + model_name + '.inp'
    inp = read_inp_file(path)
    ori_data = inp[TIMESERIES][rain_id].data
    data = []
    for d in ori_data:
        data.append({'time': d[0].strftime(format_time), 'rain': d[1]})
    return jsonify(
        {'msg': success_msg, 'data': {'name': rain_id, 'list': data}})


# 更新降雨数据
@timeseries_bp.route('/ts/rain', methods=["POST"])
def update_rain():
    params = request.json
    model_name = params.get('model_name')
    rain_id = params.get('name')
    path = app.config["MODEL_PATH"] + model_name + '.inp'
    inp = read_inp_file(path)


