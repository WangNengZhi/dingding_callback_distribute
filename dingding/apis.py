import json
import requests
import logging

from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from common import keys

from dingding.models import DingTag
from dingding.logic import get_token
from dingding.logic import encrypt_result
from dingding.logic import result_success

logger = logging.getLogger('log')


def register_call(request):
    access_token = get_token()
    url = 'https://oapi.dingtalk.com/call_back/update_call_back?access_token=%s' % access_token
    data = {
        'call_back_tag': ['user_add_org', 'user_modify_org', 'user_leave_org', 'user_active_org', 'org_admin_add',
                          'org_admin_remove', 'org_dept_create', 'org_dept_modify', 'org_dept_remove', 'org_remove',
                          'org_change', 'label_user_change', 'label_conf_add', 'label_conf_del', 'label_conf_modify',
                          'edu_user_insert', 'edu_user_update', 'edu_user_delete', 'edu_user_relation_insert',
                          'edu_user_relation_update', 'edu_user_relation_delete', 'edu_dept_insert', 'edu_dept_update',
                          'edu_dept_delete', 'bpms_task_change', 'bpms_instance_change', 'chat_add_member',
                          'chat_remove_member', 'chat_quit', 'chat_update_owner', 'chat_update_title', 'chat_disband',
                          'check_in', 'attendance_check_record', 'attendance_schedule_change', 'attendance_overtime_duration',
                          'meetingroom_book', 'meetingroom_room_info'],
        'token': keys.TOKEN,
        'aes_key': keys.AES_KEY,
        'url': 'http://hcff.vaiwan.com/api/call_back/',
        'access_token': access_token,
    }
    res = requests.post(url, json=data)
    return HttpResponse(res)


def call_back(request):
    token = keys.TOKEN
    result_success(keys.AES_KEY, token, keys.CORP_ID)
    data = request.body

    json_data = json.loads(data)

    type_info = encrypt_result(keys.AES_KEY, keys.CORP_ID, json_data['encrypt'])
    type_name = json.loads(type_info)
    name = type_name.get('EventType')
    # 查询事件
    state = None
    ding_tag = DingTag.objects.filter(tag=name)
    for url in ding_tag:
        urls = url.url.url
        session = requests.session()
        
        try:
            if url.url.db_name:
                session.get(url=urls + 'web?db={}'.format(url.url.db_name))
                state = session.post(urls + url.url.path, json=json_data)
            else:
                state = requests.post(urls + url.url.path, json=json_data)
        except ConnectionAbortedError:
            logger.error(ConnectionAbortedError)
        if state is None:
            response = result_success(keys.AES_KEY, token, keys.CORP_ID)
            return JsonResponse(response)
    return HttpResponse(state.content)


@csrf_exempt
def get_data(request):
    """获取请求数据"""
    data = request.POST

    token = get_token()
    url = 'https://oapi.dingtalk.com/topapi/processinstance/create?access_token=%s' % token
    res = requests.post(url, data)
    response = json.loads(res.text)

    return JsonResponse(response)
