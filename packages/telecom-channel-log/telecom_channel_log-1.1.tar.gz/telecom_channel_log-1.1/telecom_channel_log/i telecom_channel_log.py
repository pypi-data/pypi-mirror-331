# coding:utf-8
import os
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
    from urllib import urlencode
else:
    from urllib.parse import urlencode
    unicode = str

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
    this.appname = appname
    this.syscode = syscode

    if stream is not unique:
        warnings.warn(
            'parameter "stream" will be deprecated soon, replaced to '
            '"output_to_terminal".', category=DeprecationWarning, stacklevel=2
        )
        if output_to_terminal is None:
            output_to_terminal = stream

    this.output_to_terminal = output_to_terminal

    handlers = []
    for level in 'debug', 'info', 'warning', 'error':
        handlers.append({
            'name': 'TimedRotatingFileHandler',
            'level': level.upper(),
            'filename': '%s/%s/%s/%s.%d.log' % (
                logdir, appname, level, level, os.getpid()
            ),
            'encoding': 'UTF-8',
            'when': when,
            'interval': interval,
            'backupCount': backup_count,
            'options': {'onlyRecordCurrentLevel': True}
        })

    glog.__init__(__package__, handlers=handlers, gname=__package__)

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

    if enable_journallog_in and Flask is not None:
        thread = threading.Thread(target=register_flask_middleware)
        thread.daemon = True
        thread.start()

    if enable_journallog_out and requests is not None:
        requests.Session.request = journallog_out(requests.Session.request)


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

    f_back = inspect.currentframe().f_back
    level = f_back.f_code.co_name
    f_back = f_back.f_back

    data = {
        'app_name': this.appname + '_code',
        'level': level.upper(),
        'logger': __package__,
        'log_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        'code_message': msg,
        'HOSTNAME': socket.gethostname(),
        'pathName': f_back.f_code.co_filename,
        'funcName': f_back.f_code.co_name,
        'lineNo': f_back.f_lineno
    }

    for k, v in extra.items():
        if k not in data:
            data[k] = v

    getattr(glog, level)(jsonx.dumps(data, ensure_ascii=False))

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


def trace(**extra):
    extra = OmitLongString(extra)
    extra.update({'app_name': this.appname + '_trace', 'level': 'TRACE'})
    glog.debug(jsonx.dumps(extra, ensure_ascii=False))


def journallog_in_before():
    g.request_time = datetime.now()


def journallog_in(response):
    if request.path == '/healthcheck':
        return response

    view_func = current_app.view_functions.get(request.endpoint)
    method_code = view_func.__name__ if view_func else None

    try:
        request_body = request.get_data()
        request_data = jsonx.loads(request_body) if request_body else None
    except ValueError:
        request_data = None
    else:
        request_data = OmitLongString(request_data)

    try:
        response_data = jsonx.loads(response.get_data())
    except ValueError:
        response_data = response_code = None
    else:
        response_data = OmitLongString(response_data)
        try:
            response_code = response_data.get('code')
        except AttributeError:
            response_code = None

    response_time = datetime.now()
    response_time_str = response_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    glog.info(jsonx.dumps({
        'host_name': socket.gethostname(),
        'host': request.remote_addr,
        'app_name': this.appname + '_info',
        'level': 'INFO',
        'logger': __package__,
        'log_time': response_time_str,
        'transaction_id': uuid.uuid4().hex,
        'dialog_type': 'in',
        'address': request.url,
        'fcode': request.headers.get('User-Agent'),
        'tcode': this.syscode,
        'method_code': method_code,
        'http_method': request.method,
        'request_time': g.request_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        'request_headers': dict(request.headers),
        'request_payload': request_data,
        'response_headers': dict(response.headers),
        'response_payload': response_data,
        'response_time': response_time_str,
        'response_code': response_code,
        'response_remark': None,
        'http_status_code': response.status_code,
        'order_id': None,
        'account_type': None,
        'account_num': None,
        'province_code': None,
        'city_code': None,
        'key_type': None,
        'key_param': None,
        'total_time': round((response_time - g.request_time).total_seconds(), 3)
    }, ensure_ascii=False))

    return response


def journallog_out(func):

    @functools.wraps(func)
    def inner(
            self, method, url,
            headers=None, params=None, data=None, json=None,
            **kw
    ):
        request_time = datetime.now()
        response = func(self, method, url, **kw)
        response_time = datetime.now()
        response_time_str = response_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        f_back = inspect.currentframe().f_back.f_back
        if f_back.f_back is not None:
            f_back = f_back.f_back

        if params:
            tag = '&' if '?' in url else '?'
            url += tag + urlencode(OmitLongString(params))

        if data:
            if isinstance(data, (str, unicode)):
                try:
                    request_data = jsonx.loads(data)
                except ValueError:
                    request_data = data[:3000]
            else:
                request_data = data
        elif json:
            request_data = json
        else:
            request_data = None
        request_data = OmitLongString(request_data)

        try:
            response_data = response.json()
        except ValueError:
            response_data = response_code = None
        else:
            response_data = OmitLongString(response_data)
            try:
                response_code = response_data.get('code')
                if response_code is None:
                    response_code = response_data.get('head', {}).get('code')
            except AttributeError:
                response_code = None

        glog.info(jsonx.dumps({
            'host_name': socket.gethostname(),
            'app_name': this.appname + '_info',
            'level': 'INFO',
            'logger': __package__,
            'log_time': response_time_str,
            'transaction_id': uuid.uuid4().hex,
            'dialog_type': 'out',
            'address': url,
            'fcode': this.syscode,
            'tcode': this.syscode,
            'method_code': f_back.f_code.co_name,
            'http_method': response.request.method,
            'request_time': request_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'request_headers': headers,
            'request_payload': request_data,
            'response_headers': dict(response.headers),
            'response_payload': response_data,
            'response_time': response_time_str,
            'response_code': response_code,
            'response_remark': None,
            'http_status_code': response.status_code,
            'order_id': None,
            'account_type': None,
            'account_num': None,
            'province_code': None,
            'city_code': None,
            'key_type': None,
            'key_param': None,
            'total_time':
                round((response_time - request_time).total_seconds(), 3)
        }, ensure_ascii=False))

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
