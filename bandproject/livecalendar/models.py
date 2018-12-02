from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator


# Create your models here.
class Band(models.Model):
    """バンド情報"""
    name = models.CharField('バンド名', max_length = 50)

    def __str__(self):
        return self.name

class Place(models.Model):
    """ライブハウス情報"""
    name = models.CharField('名前',max_length = 30)
    address = models.CharField('住所',max_length=100)

    def __str__(self):
        return self.name

class Live(models.Model):
    """ライブ情報"""
    date = models.DateField('日程')
    title = models.CharField('イベントタイトル', max_length = 50)
    place = models.ForeignKey(Place, verbose_name='ライブハウス', on_delete=models.PROTECT)
    band = models.ManyToManyField(Band, verbose_name='出演バンド',blank=True)
    open = models.TimeField('OPEN',blank=True,null=True)
    start = models.TimeField('START',blank=True,null=True)
    door = models.IntegerField('当日料金',blank=True,null=True)
    adv = models.IntegerField('前売料金',blank=True,null=True)

    def __str__(self):
        return self.title

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username or not email:
            raise ValueError('The given username or email must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
        'unique': _("A user with that email already exists."),
        },
    )

    favorite = models.ManyToManyField(Band,verbose_name='お気に入り', blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']#createsuperuserコマンドのときにemailを使う

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
