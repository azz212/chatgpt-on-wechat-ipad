# encoding:utf-8
import json
from quart import Blueprint
from quart import request, jsonify, render_template
import os

from common.log import logger
# 创建蓝图对象
plugins_bp = Blueprint('plugins', __name__)
@plugins_bp.route('/settings', methods=['GET', 'POST'])
async def settings():
    if request.method == 'POST':
        data = await request.json
        plugin_name = data.get('plugin_name')
        config_data = data.get('config')
        save_config(plugin_name, config_data)
        return jsonify({'status': 'success'})

    # Load plugins list and render the template
    plugins = load_plugins_list()
    return await render_template('settings.html', plugins=plugins)


@plugins_bp.route('/get_plugin_config/<plugin_name>', methods=['GET'])
async def get_plugin_config(plugin_name):
    config = load_pconfig(plugin_name)
    return jsonify(config)


def load_plugins_list():
    plugins_file = os.path.join(os.getcwd(), 'plugins', 'plugins.json')
    with open(plugins_file, 'r', encoding='utf-8') as file:
        plugins_data = json.load(file)

    enabled_plugins = {}
    for plugin_name, plugin_info in plugins_data.get('plugins', {}).items():
        if plugin_name.lower()  in ["admin","godcmd","finish"]:
            continue
        if plugin_info.get('enabled', False):
            enabled_plugins[plugin_name] = plugin_info

    return enabled_plugins


def load_pconfig(plugin_name):
    config_file = os.path.join(os.getcwd(), 'plugins', plugin_name, 'config.json')
    logger.info(f'Loading config{config_file}')
    if not os.path.exists(config_file):
        return {}
    with open(config_file, 'r', encoding='utf-8') as file:
        #logger.info(json.load(file))
        return json.load(file)


def save_config(plugin_name, new_config):
    config_file = os.path.join(os.getcwd(), 'plugins', plugin_name, 'config.json')
    current_config = load_pconfig(plugin_name)

    for key, value in new_config.items():
        if key in current_config:
            if isinstance(value["value"], str) and value["value"].lower() in ['true', 'false']:
                value["value"] = value["value"].lower() == 'true'
            current_config[key]['value'] = value["value"]
        else:
            current_config[key]["value"] =  value["value"]

    with open(config_file, 'w', encoding='utf-8') as file:
        json.dump(current_config, file, indent=4, ensure_ascii=False)
