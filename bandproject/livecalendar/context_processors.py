from .models import Live

def common(request):
    """テンプレートに毎回読ませるデータ"""
    context = {
        'live_list_et':Live.objects.all(),
    }
    return context
