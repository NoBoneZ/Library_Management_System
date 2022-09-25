import datetime


def date_checker(request):
    context = {}
    open_time = datetime.time(9, 00, 0)
    close_time = datetime.time(20, 00, 00)
    context["open_time"] = open_time
    context["close_time"] = close_time
    if open_time <= datetime.datetime.now().time() <= close_time:
        context['is_open'] = True
        return context
    else:
        context['is_open'] = False
        return context



