from typing import Literal, Callable
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import redirect
from django.contrib.auth import logout
from .settings import TIME_DIFFERENCE_BETWEEN_SERVER


def datetime_now() -> datetime:
    return datetime.now() + relativedelta(hours=TIME_DIFFERENCE_BETWEEN_SERVER)


def request_schema_validation(request_method: Literal["GET", "POST"], schema) -> Callable:
    def decorator(function):
        def wrapper(*args, **kwargs):
            if request_method == "GET":
                request_data = args[0].query_params
            else:
                request_data = args[0].data

            serializer = schema(data=request_data)
            serializer.is_valid(raise_exception=True)

            if request_method == "GET":
                args[0].query_params._mutable = True
                args[0].query_params.update(serializer.validated_data)
            else:
                try:
                    args[0].data._mutable = True
                except Exception as e:
                    print(e)
                    pass

                args[0].data.update(serializer.validated_data)

            return function(*args, **kwargs)
        return wrapper
    return decorator


def check_account_expiration() -> Callable:
    def decorator(function):
        def wrapper(*args, **kwargs):
            request = args[0]

            if request.user.is_authenticated and not request.user.is_superuser:
                if hasattr(request.user, "client"):
                    if request.user.client.is_expired:
                        logout(request)
                        return redirect("/")

            return function(*args, **kwargs)
        return wrapper
    return decorator
