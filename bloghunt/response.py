from rest_framework.response import Response


def error_response(*messages, **kwargs):
    return Response(dict({
        'errors': [{'message': message} for message in messages],
    }, **kwargs))
