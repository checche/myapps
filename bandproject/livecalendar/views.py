from django.views import generic
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect, resolve_url, get_object_or_404
from django.template.loader import get_template
from .forms import *
from .models import Band, Live, CustomUser
import datetime
import calendar
from collections import deque
import datetime

User = get_user_model()


class LiveIndexView(generic.ListView):
    model = Live
    paginate_by = 5

    def get_queryset(self):
        queryset = Live.objects.order_by('date')
        queryset=queryset.filter(date__gte = datetime.date.today())#本日以降のものだけ表示
        keyword = self.request.GET.get('keyword')
        livedate=self.request.GET.get('livedate')
        if livedate:
            queryset=queryset.filter(date = livedate)
        if keyword:
            queryset=queryset.filter(Q(band__name__icontains=keyword)|Q(place__name__icontains=keyword))
        return queryset

class LiveDetailView(generic.DetailView):
    model = Live

class BandListView(generic.ListView):
    model = Band
    paginate_by = 10

    def get_queryset(self):
        keyword = self.request.GET.get('keyword')
        queryset = Band.objects.all()
        if keyword:
            queryset=queryset.filter(name__icontains=keyword)
        return queryset

class BandDetailView(generic.DetailView):
    model = Band
    def get_context_data(self, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg)
        b=Band.objects.get(pk=pk)
        context = {}
        context['follower'] = CustomUser.objects.filter(favorite_band__pk=pk).count()
        context['lives'] = Live.objects.filter(band__pk=pk)
        return super().get_context_data(**context)

"""フォロー関係"""

class FollowLiveView(generic.ListView):
    model = Live
    paginate_by = 5
    def get_queryset(self):
        """フォローしてるバンドのライブを表示"""
        user=self.request.user
        queryset = Live.objects.order_by('date')
        queryset=queryset.filter(date__gte = datetime.date.today())#本日以降のものだけ表示
        queryset=queryset.filter(band__in=user.favorite_band.all())
        return queryset

def followBand(request, pk):
    """バンドをフォローする"""
    band = get_object_or_404(Band, pk=pk)
    request.user.favorite_band.add(band)
    return redirect('livecalendar:band_list')

class FollowBandView(generic.ListView):
    model = Band
    paginate_by = 10
    def get_queryset(self):
        user=self.request.user
        queryset = user.favorite_band.all()
        return queryset


"""ユーザー管理関係"""

class LoginView(LoginView):
    form_class = LoginForm
    template_name = 'livecalendar/login.html'
    redirect_authenticated_user = True

class LogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'livecalendar/logged_out.html'

class Register(generic.CreateView):
    template_name = 'livecalendar/signup.html'
    form_class = RegisterForm

    def form_valid(self, form):
        """バリデーションOKのときに行う動作"""
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {'protocol': self.request.scheme,'domain': domain,'token': dumps(user.pk),'user': user}
        """{{ protocol }}://{{ domain }}{% url 'livecalendar:signup_complete' token %}という認証URLを送る"""

        subject_template = get_template('livecalendar/mail_template/signup/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('livecalendar/mail_template/signup/message.txt')
        message = message_template.render(context)

        user.email_user(subject, message)
        return redirect('livecalendar:signup_done')

class RegisterDone(generic.TemplateView):
    template_name='livecalendar/signup_done.html'

class RegisterComplete(generic.TemplateView):
    template_name = 'livecalendar/signup_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)

    def get(self,request, **kwargs):
        """getしたときの処理"""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        except SignatureExpired:
            return HttpResponseBadRequest()
        except BadSignature:
            return HttpResponseBadRequest()

        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class UserpassMixin(UserPassesTestMixin):
    raise_exception = True
    def test_func(self):
        """条件書く"""
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser

class EditUserInfo(UserpassMixin, generic.UpdateView):
    form_class = UserEditForm
    model = CustomUser
    template_name = 'livecalendar/edit.html'

    def get_success_url(self):
        return resolve_url('livecalendar:edit', pk=self.kwargs['pk'])



"""カレンダー関係"""

class BaseCalendarMixin:
    """カレンダー関連Mixinの、基底クラス"""
    first_weekday = 0  # 0は月曜から
    week_names = ['月', '火', '水', '木', '金', '土', '日']

    def setup(self):
        self._calendar = calendar.Calendar(self.first_weekday)

    def get_week_names(self):
        return self.week_names


class MonthCalendarMixin(BaseCalendarMixin):
    """月間カレンダーの機能を提供するMixin"""

    @staticmethod
    def get_previous_month(date):
        """前月を返す"""
        if date.month == 1:
            return date.replace(year=date.year-1, month=12, day=1)

        else:
            return date.replace(month=date.month-1, day=1)

    @staticmethod
    def get_next_month(date):
        """次月を返す"""
        if date.month == 12:
            return date.replace(year=date.year+1, month=1, day=1)

        else:
            return date.replace(month=date.month+1, day=1)

    def get_month_days(self, date):
        """その月の全ての日を返す"""
        return self._calendar.monthdatescalendar(date.year, date.month)

    def get_current_month(self):
        """現在の月を返す"""
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        if month and year:
            month = datetime.date(year=int(year), month=int(month), day=1)
        else:
            month = datetime.date.today().replace(day=1)
        return month

    def get_month_calendar(self):
        """月間カレンダー情報の入った辞書を返す"""
        self.setup()
        current_month = self.get_current_month()
        calendar_data = {
            'now': datetime.date.today(),
            'days': self.get_month_days(current_month),
            'current': current_month,
            'previous': self.get_previous_month(current_month),
            'next': self.get_next_month(current_month),
            'week_names': self.get_week_names(),
        }
        return calendar_data

class MonthCalendar(MonthCalendarMixin, generic.TemplateView):
    """月間カレンダーを表示するビュー"""
    template_name = 'livecalendar/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['month'] = self.get_month_calendar()
        return context
