from django.views import generic
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect
from django.template.loader import get_template
from .forms import LoginForm, UserCreateForm
from .models import Band, Live
import datetime
import calendar
from collections import deque
import datetime

User = get_user_model()

class LiveIndexView(generic.ListView):
    model = Live
    paginate_by = 20

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


class Login(LoginView):
    """ログインページ"""
    #forms.pyのどのクラスをを使うか
    form_class = LoginForm
    template_name = 'livecalendar/login.html'
    redirect_authenticated_user=True

class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'livecalendar/live_list.html'

class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'livecalendar/signup.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject_template = get_template('livecalendar/mail_template/signup/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('livecalendar/mail_template/signup/message.txt')
        message = message_template.render(context)

        user.email_user(subject, message)
        return redirect('livecalendar:signup_done')


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録完了"""
    template_name = 'livecalendar/signup_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'livecalendar/signup_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()




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
    template_name = 'livecalendar/month.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['month'] = self.get_month_calendar()
        return context
