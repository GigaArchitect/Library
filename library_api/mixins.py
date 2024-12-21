# all my custom mixins are defiend
from django.views.generic import CreateView

from .models import *


class UsertypeMixin(CreateView):
    def dispatch(self, request, *args, **kwargs):
        respose = super().dispatch(request, *args, **kwargs)
        if request.method == "POST":
            if request.POST.get("usertype") == "patron":
                patron_user = patron()
                patron_user.user = User.objects.get(id=request.user.id)
                patron_user.save()
            elif request.POST.get("usertype") == "author":
                author_user = author()
                author_user.user = User.objects.get(id=request.user.id)
                author_user.save()
        return respose
