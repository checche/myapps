from django.views import generic
from .models import Band, Live
from django.db.models import Q

# Create your views here.
class LiveIndexView(generic.ListView):
    model = Live
    paginate_by = 20

    def get_queryset(self):
        queryset = Live.objects.order_by('date')
        keyword = self.request.GET.get('keyword')
        if keyword:
            queryset=queryset.filter(Q(band__name__icontains=keyword)|Q(place__icontains=keyword))
        return queryset
