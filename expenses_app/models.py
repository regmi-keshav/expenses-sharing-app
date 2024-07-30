from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$')],
        unique=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'mobile_number']

    objects = BaseUserManager()

    def __str__(self):
        return self.email

    @staticmethod
    def create_user(email, name, mobile_number, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = BaseUserManager().normalize_email(email)
        user = User(email=email, name=name,
                    mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using='default')
        return user

    @staticmethod
    def create_superuser(email, name, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return User.create_user(email, name, mobile_number, password, **extra_fields)


class Expense(models.Model):
    SPLIT_METHOD_CHOICES = [
        ('equal', 'Equal'),
        ('exact', 'Exact'),
        ('percentage', 'Percentage'),
    ]

    payer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='expenses_paid')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    split_method = models.CharField(
        max_length=10, choices=SPLIT_METHOD_CHOICES)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()

    def __str__(self):
        return f"Expense {self.id} - {self.description}"


class ExpenseSplit(models.Model):
    expense = models.ForeignKey(
        Expense, on_delete=models.CASCADE, related_name='splits')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
