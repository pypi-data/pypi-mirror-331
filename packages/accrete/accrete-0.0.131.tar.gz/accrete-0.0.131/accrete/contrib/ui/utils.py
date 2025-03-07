from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from .context import ModalContext


def update_modal(
    request: HttpRequest,
    template: str,
    context: ModalContext | dict
) -> HttpResponse:

    if isinstance(context, ModalContext):
        context = context.dict()
    res = render(request, template, context)
    res.headers['HX-Retarget'] = f'#{context["modal_id"]}'
    res.headers['HX-Reswap'] = 'outerHTML'
    return res
