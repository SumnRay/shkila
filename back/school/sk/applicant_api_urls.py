from django.urls import path
from .applicant_api_views import (
    ApplicantCoursesListAPI,
    ApplicantBalanceAPI,
    ApplicantPaymentsListAPI,
    ApplicantCreatePaymentAPI,
)

urlpatterns = [
    path('courses/', ApplicantCoursesListAPI.as_view()),          # GET курсы
    path('balance/', ApplicantBalanceAPI.as_view()),              # GET баланс
    path('payments/', ApplicantPaymentsListAPI.as_view()),        # GET история оплат
    path('payments/create/', ApplicantCreatePaymentAPI.as_view()) # POST создать оплату
]
