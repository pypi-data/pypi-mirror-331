import inspect
from flask import request
from functools import wraps
import mlflow

# 初始化 MLflow Tracing
mlflow.set_tracking_uri("http://mlflow.api.odin.ke.com")  # MLflow 跟踪服务器的地址
import os

os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://storage.lianjia.com'
os.environ['AWS_ACCESS_KEY_ID'] = 'U78RLW9CPMJEA1VADIVS'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'MjyeJrhNeQLrvVIGfVdhQia7HUixYGvlc6sk2vcC'
os.environ['MLFLOW_S3_BUCKET'] = 'visualize'
def api_aspect(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logId = request.headers.get('logId', 'default-logId')
            # 设置 MLflow 实验
            mlflow.set_experiment(logId)
            # 调用原始函数
            # 启动 MLflow 跟踪
            with mlflow.start_span(name=func.__name__) as span:
                try:
                    # 调用原始函数
                    span.set_inputs(request.args)
                    result = func(*args, **kwargs)
                    if isinstance(result, tuple):
                        span.set_outputs(result[0].json)
                    else:
                        span.set_outputs(result.get_data(as_text=True))
                except Exception as e:
                    span.set_outputs(e)
                    return e
            return result
        except Exception as e:
            span.set_outputs(e)
            return e
    return wrapper
def func_aspect(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # 提取函数的变量和值
            inputs = {}
            # 处理位置参数
            # 获取函数的参数名
            func_signature = inspect.signature(func)
            parameters = list(func_signature.parameters.keys())

            # 将位置参数与参数名对应
            for i, arg in enumerate(args):
                inputs[parameters[i]] = arg

            # 处理关键字参数
            inputs.update(kwargs)
            # 调用原始函数
            # 启动 MLflow 跟踪
            with mlflow.start_span(name=func.__name__) as span:
                # 调用原始函数
                span.set_inputs(inputs)
                try:
                    result = func(*args, **kwargs)
                    span.set_outputs(result)
                except Exception as e:
                    span.set_outputs(e)
                    return e
            return result
        except Exception as e:
                span.set_outputs(e)
    return wrapper

def test():
    print("test")