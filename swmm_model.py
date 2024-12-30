import os
import glob
from flask import jsonify, request, Blueprint, current_app as app

swmm_model_bp = Blueprint('swmm_model', __name__)
code_success = 200


def find_files_with_extension(folder_path, extension):
    file_list = glob.glob(os.path.join(folder_path, f"*.{extension}"))
    return [os.path.splitext(os.path.basename(file))[0] for file in file_list]


@swmm_model_bp.route('/model', methods=['GET'])
def get_model_list():
    try:
        model_path = app.config["MODEL_PATH"]
        extension = 'inp'
        data = find_files_with_extension(model_path, extension)
        return jsonify({'data': data, 'msg': '查询成功', 'code': code_success})
    except Exception as e:
        return jsonify({'msg': '查询失败' + str(e)})
