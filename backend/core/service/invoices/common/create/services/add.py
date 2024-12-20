from django.http import JsonResponse

from backend.core.api.public.types import APIRequest
from backend.core.types.requests import WebRequest
from backend.finance.models import InvoiceProduct
from backend.core.types.htmx import HtmxHttpRequest


def add(request: APIRequest | WebRequest):
    context: dict = {}
    existing_service = request.POST.get("existing_service", 0)

    existing_service_obj = InvoiceProduct.filter_by_owner(request.actor).filter(id=existing_service).first()

    list_hours = request.POST.getlist("hours[]")
    list_service_name = request.POST.getlist("service_name[]")
    list_service_description = request.POST.getlist("service_description[]")
    list_price_per_hour = request.POST.getlist("price_per_hour[]")
    list_of_current_rows = [row for row in zip(list_hours, list_service_name, list_service_description, list_price_per_hour)]

    if not existing_service:
        hours = float(request.POST.get("post_hours", "0"))  # todo add error handling rather than just plain float
        service_name = request.POST.get("post_service_name")
        service_description = request.POST.get("post_service_description")
        price_per_hour = float(request.POST.get("post_rate", "0"))  # todo add error handling rather than just plain float

        if not hours:
            return JsonResponse(
                {"status": "false", "message": "The hours field is required"},
                status=400,
            )
        if not service_name:
            return JsonResponse(
                {"status": "false", "message": "The service name field is required"},
                status=400,
            )
        if not price_per_hour:
            return JsonResponse(
                {"status": "false", "message": "The price per hour field is required"},
                status=400,
            )

    context["rows"] = []
    for row in list_of_current_rows:
        context["rows"].append(
            {
                "hours": row[0],
                "service_name": row[1],
                "service_description": row[2],
                "price_per_hour": row[3],
                "total_price": float(row[0]) * float(row[3]),
            }
        )

    if existing_service and existing_service_obj and existing_service_obj.rate is not None:
        context["rows"].append(
            {
                "hours": existing_service_obj.quantity,
                "service_name": existing_service_obj.name,
                "service_description": existing_service_obj.description,
                "price_per_hour": existing_service_obj.rate,
                "total_price": existing_service_obj.quantity * existing_service_obj.rate,
            }
        )
    else:
        context["rows"].append(
            {
                "hours": hours,
                "service_name": service_name,
                "service_description": service_description,
                "price_per_hour": price_per_hour,
                "total_price": hours * price_per_hour,
            }
        )

    return context
