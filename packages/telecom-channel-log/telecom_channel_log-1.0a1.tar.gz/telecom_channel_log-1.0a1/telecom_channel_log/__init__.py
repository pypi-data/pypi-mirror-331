# coding:utf-8


def __init__(
        appname,                     # type: str
        syscode,                     # type: str
        logdir               =None,  # type: str
        when                 =None,  # type: str, Set('W', 'D', 'H', 'M', 'S')
        interval             =None,  # type: int
        backup_count         =None,  # type: int
        stream               =None,  # type: bool
        enable_journallog_in =None,  # type: bool
        enable_journallog_out=None   # type: bool
):
    """
    初始化电渠应用服务日志。

    @param appname:
        你的应用名称，通常与 GitLab CI 文件中的 APPNAME 字段一致。
    @param syscode:
        你的应用分配的系统编码（大写）。
    @param logdir:
        指定日志目录，默认为 "/app/logs"（如果你的系统是 Windows 则默认为
        "C:\BllLogs"）。
    @param when:
        控制日志轮转周期，默认为 "D"。支持按天/小时/分钟等单位滚动。可选值有：W:周, D:天,
        H:小时, M:分钟, S:秒。
    @param interval:
        日志轮转频率，默认为 1 。同参数 `when` 一起使用（如：`when="D"` 且
        `interval=1` 表示每天滚动一次）。
    @param backup_count:
        日志保留策略，控制最大历史版本数量，默认为 7。设为 0 则永久保留。
    @param stream:
        设为 True 日志将同时输出到终端，默认为 False。流水日志和埋点日志除外。
    @param enable_journallog_in:
        设为 True 表示启用内部流水日志，默认为 False。目前仅支持 Flask 框架。
    @param enable_journallog_out:
        设为 True 表示启用外部流水日志，默认为 False。目前仅支持 requests 框架。
    """


def debug  (msg, **extra): pass
def info   (msg, **extra): pass
def warning(msg, **extra): pass
def error  (msg, **extra): pass

def trace(**extra): pass  # 埋点日志


class _xe6_xad_x8c_xe7_x90_xaa_xe6_x80_xa1_xe7_x8e_xb2_xe8_x90_x8d_xe4_xba_x91:
    import sys

    gpath = __name__ + '.i ' + __name__
    __import__(gpath)

    gpack = sys.modules[__name__]
    gcode = globals()['i ' + __name__]

    for gname in globals():
        if gname[0] != '_':
            gfunc = getattr(gcode, gname, None)
            if gfunc and getattr(gfunc, '__module__', None) == gpath:
                gfunc.__module__ = __package__
                gfunc.__doc__ = getattr(gpack, gname).__doc__
                setattr(gpack, gname, gfunc)

    gpack.__init__ = gcode.__init__
