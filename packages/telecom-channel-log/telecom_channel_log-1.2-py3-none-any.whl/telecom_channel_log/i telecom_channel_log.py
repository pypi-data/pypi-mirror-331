# coding:utf-8
import os
import re
import sys
import time
import uuid
import json as jsonx
import socket
import inspect
import warnings
import functools
import threading

from datetime import datetime

if os.path.basename(sys.argv[0]) != 'setup.py':
    import gqylpy_log as glog

try:
    from flask import Flask
except ImportError:
    Flask = None
else:
    from flask import g
    from flask import request
    from flask import current_app
    from flask import has_request_context

    def __new__(cls, *a, **kw):
        app = super(Flask, cls).__new__(cls)
        cls.__apps__.append(app)
        return app

    if sys.version_info.major < 3:
        __new__ = staticmethod(__new__)

    Flask.__apps__, Flask.__new__ = [], __new__

try:
    import requests
except ImportError:
    requests = None

if sys.version_info.major < 3:
    from urlparse import urlparse
    from urlparse import parse_qs
else:
    from urllib.parse import urlparse
    from urllib.parse import parse_qs

    unicode = str

co_qualname = 'co_qualname' if sys.version_info >= (3, 11) else 'co_name'

that = sys.modules[__package__]
this = sys.modules[__name__]

unique = object()


def __init__(
        appname,
        syscode,
        logdir=r'C:\BllLogs' if sys.platform == 'win32' else '/app/logs',
        when='D',
        interval=1,
        backup_count=7,
        stream=unique,
        output_to_terminal=None,
        enable_journallog_in=False,
        enable_journallog_out=False
):
    if hasattr(this, 'appname'):
        raise RuntimeError('repeat initialization.')

    if re.match(r'^[A-Z]\d{9}_', appname) is None:
        appname = syscode.lower() + '_' + appname

    that.appname = this.appname = appname
    that.syscode = this.syscode = syscode.upper()

    if stream is not unique:
        warnings.warn(
            'parameter "stream" will be deprecated soon, replaced to '
            '"output_to_terminal".', category=DeprecationWarning, stacklevel=2
        )
        if output_to_terminal is None:
            output_to_terminal = stream

    this.output_to_terminal = output_to_terminal

    handlers = []
    for level in 'debug', 'info', 'warning', 'error', 'critical':
        handlers.append({
            'name': 'TimedRotatingFileHandler',
            'level': level.upper(),
            'filename': '%s/%s/%s/%s_code.%d.log' % (
                logdir, appname, level, appname, os.getpid()
            ),
            'encoding': 'UTF-8',
            'when': when,
            'interval': interval,
            'backupCount': backup_count,
            'options': {'onlyRecordCurrentLevel': True}
        })

    glog.__init__('code', handlers=handlers, gname='code')

    if output_to_terminal:
        glog.__init__(
            'stream',
            formatter={
                'fmt': '[%(asctime)s] [%(levelname)s] %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            handlers=[{'name': 'StreamHandler'}],
            gname='stream'
        )

    enable_journallog = False

    if enable_journallog_in and Flask is not None:
        enable_journallog = True
        thread = threading.Thread(target=register_flask_middleware)
        thread.daemon = True
        thread.start()

    if enable_journallog_out and requests is not None:
        enable_journallog = True
        requests.Session.request = journallog_out(requests.Session.request)

    if enable_journallog:
        glog.__init__(
            'info',
            level='INFO',
            handlers=[{
                'name': 'TimedRotatingFileHandler',
                'level': 'INFO',
                'filename': '%s/%s/info/%s_info.%d.log' % (
                    logdir, appname, appname, os.getpid()
                ),
                'encoding': 'UTF-8',
                'when': when,
                'interval': interval,
                'backupCount': backup_count,
            }],
            gname='info_'
        )


def register_flask_middleware():
    start = time.time()
    while not Flask.__apps__ and time.time() - start < 30:
        time.sleep(.01)

    for app in Flask.__apps__:
        app.before_request(journallog_in_before)
        app.after_request(journallog_in)


def logger(msg, *args, **extra):
    args = tuple(OmitLongString(v) for v in args)
    extra = OmitLongString(extra)

    if sys.version_info.major < 3 and isinstance(msg, str):
        msg = msg.decode('utf8')

    if isinstance(msg, unicode):
        msg = (msg % args)[:1000]
    elif isinstance(msg, (dict, list, tuple)):
        msg = OmitLongString(msg)

    transaction_id = g.transaction_id \
        if Flask is not None and has_request_context() else uuid.uuid4().hex

    f_back = inspect.currentframe().f_back
    level = f_back.f_code.co_name
    f_back = f_back.f_back

    data = {
        'app_name': this.appname + '_code',
        'level': level.upper(),
        'log_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        'logger': __package__,
        'thread': threading.currentThread().ident,
        'code_message': msg,
        'transaction_id': transaction_id,
        'method_code': None,
        'method_name': getattr(f_back.f_code, co_qualname),
        'error_code': None,
        'tag': None,
        'host_name': socket.gethostname(),
        'filename': f_back.f_code.co_filename,
        'line': f_back.f_lineno
    }

    for k, v in extra.items():
        if data.get(k) is None:
            data[k] = v

    getattr(glog, level)(jsonx.dumps(data, ensure_ascii=False), gname='code')

    if this.output_to_terminal:
        getattr(glog, level)(msg, gname='stream')


def debug(msg, *args, **extra):
    logger(msg, *args, **extra)


def info(msg, *args, **extra):
    logger(msg, *args, **extra)


def warning(msg, *args, **extra):
    logger(msg, *args, **extra)


warn = warning


def error(msg, *args, **extra):
    logger(msg, *args, **extra)


exception = error


def critical(msg, *args, **extra):
    logger(msg, *args, **extra)


fatal = critical


def trace(**extra):
    extra = OmitLongString(extra)
    extra.update({'app_name': this.appname + '_trace', 'level': 'TRACE'})
    glog.debug(jsonx.dumps(extra, ensure_ascii=False))


def journallog_in_before():
    if request.path == '/healthcheck':
        return

    g.request_time = datetime.now()

    for name in 'Transaction-ID', 'transaction-id', 'transaction_id':
        if name in request.headers:
            g.transaction_id = request.headers[name]
            break
    else:
        g.transaction_id = uuid.uuid4().hex


def journallog_in(response):
    if request.path == '/healthcheck':
        return response

    parsed_url = urlparse(request.url)
    address = parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path

    view_func = current_app.view_functions.get(request.endpoint)
    method_name = view_func.__name__ if view_func else None

    if request.args:
        request_data = request.args.to_dict()
    else:
        try:
            request_body = request.get_data()
            request_data = jsonx.loads(request_body) if request_body else None
        except ValueError:
            request_data = None

    try:
        response_data = jsonx.loads(response.get_data())
    except ValueError:
        response_data = response_code = order_id = \
            province_code = city_code = \
            account_type = account_num = \
            response_account_type = response_account_num = None
    else:
        if isinstance(response_data, dict):
            head = response_data.get('head')
            x = head if isinstance(head, dict) else request_data
            response_code = x.get('code')
            order_id = x.get('order_id')
            province_code = x.get('province_code')
            city_code = x.get('city_code')
            account_type = x.get('account_type')
            account_num = x.get('account_num')
            response_account_type = x.get('response_account_type')
            response_account_num = x.get('response_account_num')
        else:
            response_code = order_id = \
                province_code = city_code = \
                account_type = account_num = \
                response_account_type = response_account_num = None

    response_time = datetime.now()
    response_time_str = response_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    total_time = round((response_time - g.request_time).total_seconds(), 3)

    glog.info(jsonx.dumps({
        'app_name': this.appname + '_info',
        'level': 'INFO',
        'log_time': response_time_str,
        'logger': __package__,
        'thread': threading.current_thread().ident,
        'transaction_id': g.transaction_id,
        'dialog_type': 'in',
        'address': address,
        'fcode': request.headers.get('User-Agent'),
        'tcode': this.syscode,
        'method_code': None,
        'method_name': method_name,
        'http_method': request.method,
        'request_time': g.request_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        'request_headers': dict(request.headers),
        'request_payload': OmitLongString(request_data),
        'response_time': response_time_str,
        'response_headers': dict(response.headers),
        'response_payload': OmitLongString(response_data),
        'response_code': response_code,
        'response_remark': None,
        'http_status_code': response.status_code,
        'order_id': order_id,
        'province_code': province_code,
        'city_code': city_code,
        'total_time': total_time,
        'error_code': response_code,
        'request_ip': request.remote_addr,
        'host_ip': parsed_url.hostname,
        'host_name': socket.gethostname(),
        'account_type': account_type,
        'account_num': account_num,
        'response_account_type': response_account_type,
        'response_account_num': response_account_num,
        'user': None,
        'tag': None,
        'service_line': None
    }, ensure_ascii=False), gname='info_')

    return response


def journallog_out(func):

    @functools.wraps(func)
    def inner(
            self, method, url,
            headers=None, params=None, data=None, json=None,
            **kw
    ):
        if headers is None:
            headers = {}

        if Flask is not None and has_request_context():
            transaction_id = headers['Transaction-ID'] = g.transaction_id
        else:
            for name in 'Transaction-ID', 'transaction-id', 'transaction_id':
                if name in headers:
                    transaction_id = headers[name]
                    break
            else:
                transaction_id = headers['Transaction-ID'] = uuid.uuid4().hex

        request_time = datetime.now()
        response = func(
            self, method, url,
            headers=headers, params=params, data=data, json=json,
            **kw
        )
        response_time = datetime.now()
        response_time_str = response_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        f_back = inspect.currentframe().f_back.f_back
        if f_back.f_back is not None:
            f_back = f_back.f_back

        parse_url = urlparse(url)
        address = parse_url.scheme + '://' + parse_url.netloc + parse_url.path
        query_string = {k: v[0] for k, v in parse_qs(parse_url.query).items()}

        if params is not None:
            params.update(query_string)
            request_data = params
        elif query_string:
            request_data = query_string
        elif data:
            request_data = data
            if isinstance(request_data, (str, unicode)):
                try:
                    request_data = json.loads(request_data)
                except ValueError:
                    pass
        elif json:
            request_data = json
        else:
            request_data = None

        try:
            response_data = response.json()
        except ValueError:
            response_data = response_code = order_id = \
                province_code = city_code = \
                account_type = account_num = \
                response_account_type = response_account_num = None
        else:
            if isinstance(response_data, dict):
                head = response_data.get('head')
                x = head if isinstance(head, dict) else request_data
                response_code = x.get('code')
                order_id = x.get('order_id')
                province_code = x.get('province_code')
                city_code = x.get('city_code')
                account_type = x.get('account_type')
                account_num = x.get('account_num')
                response_account_type = x.get('response_account_type')
                response_account_num = x.get('response_account_num')
            else:
                response_code = order_id = \
                    province_code = city_code = \
                    account_type = account_num = \
                    response_account_type = response_account_num = None

        total_time = round((response_time - request_time).total_seconds(), 3)

        glog.info(jsonx.dumps({
            'app_name': this.appname + '_info',
            'level': 'INFO',
            'log_time': response_time_str,
            'logger': __package__,
            'thread': threading.current_thread().ident,
            'transaction_id': transaction_id,
            'dialog_type': 'out',
            'address': address,
            'fcode': this.syscode,
            'tcode': this.syscode,
            'method_code': None,
            'method_name': getattr(f_back.f_code, co_qualname),
            'http_method': response.request.method,
            'request_time': request_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'request_headers': headers,
            'request_payload': OmitLongString(request_data),
            'response_time': response_time_str,
            'response_headers': dict(response.headers),
            'response_payload': OmitLongString(response_data),
            'response_code': response_code,
            'response_remark': None,
            'http_status_code': response.status_code,
            'order_id': order_id,
            'province_code': province_code,
            'city_code': city_code,
            'total_time': total_time,
            'error_code': response_code,
            'request_ip': parse_url.hostname,
            'host_ip': socket.gethostbyname(socket.gethostname()),
            'host_name': socket.gethostname(),
            'account_type': account_type,
            'account_num': account_num,
            'response_account_type': response_account_type,
            'response_account_num': response_account_num,
            'user': None,
            'tag': None,
            'service_line': None
        }, ensure_ascii=False), gname='info_')

        return response

    return inner


class OmitLongString(dict):

    def __init__(self, __data__=None, **data):
        if __data__ is None:
            __data__ = data
        else:
            __data__.update(data)

        for name, value in __data__.items():
            dict.__setitem__(self, name, OmitLongString(value))

    def __new__(cls, __data__={}, **data):
        if isinstance(__data__, dict):
            return dict.__new__(cls)

        if isinstance(__data__, (list, tuple)):
            return __data__.__class__(cls(v) for v in __data__)

        if sys.version_info.major < 3 and isinstance(__data__, str):
            __data__ = __data__.decode('utf8')

        if isinstance(__data__, (unicode, str)) and len(__data__) > 1000:
            __data__ = '<Ellipsis>'

        return __data__
