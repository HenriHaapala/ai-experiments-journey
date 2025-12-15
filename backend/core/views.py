from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def health(request):
    db_ok = False
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False

    return Response({
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "error",
    })
