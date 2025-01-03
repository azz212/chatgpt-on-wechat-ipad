# encoding:utf-8
import json
from quart import Blueprint
from quart import request, jsonify, render_template
import os
from collections import OrderedDict

from common.log import logger
from .decorators import login_required
import requests
import threading
import time
from plugins import *

from plugins.event import Event, EventContext

# 创建蓝图对象
plugins_bp = Blueprint('plugins', __name__)

# 事件机制，用于等待和通知
result_event = threading.Event()
result_data = None  # 用于存储回调结果



@plugins_bp.route('/settings', methods=['GET', 'POST'])
@login_required
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
@login_required
async def get_plugin_config(plugin_name):
    config = load_pconfig(plugin_name)
    return jsonify(config)


def load_plugins_list():
    plugins_file = os.path.join(os.getcwd(), 'plugins', 'plugins.json')
    with open(plugins_file, 'r', encoding='utf-8') as file:
        plugins_data = json.load(file)

    enabled_plugins = {}
    for plugin_name, plugin_info in plugins_data.get('plugins', {}).items():
        if plugin_name.lower() in ["admin", "godcmd", "finish"]:
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
        return json.load(file, object_pairs_hook=OrderedDict)


def save_config(plugin_name, new_config):
    config_file = os.path.join(os.getcwd(), 'plugins', plugin_name, 'config.json')
    current_config = load_pconfig(plugin_name)

    for key, value in new_config.items():
        if key in current_config:
            if isinstance(value["value"], str) and value["value"].lower() in ['true', 'false']:
                value["value"] = value["value"].lower() == 'true'
            current_config[key]['value'] = value["value"]
        else:
            current_config[key] = value

    with open(config_file, 'w', encoding='utf-8') as file:
        json.dump(current_config, file, indent=4, ensure_ascii=False)

    # 触发配置更新事件
    e_context = EventContext(Event.ON_CONFIG_CHANGED)
    e_context["plugin_name"] = plugin_name
    e_context["config"] = new_config
    PluginManager().emit_event(e_context)


