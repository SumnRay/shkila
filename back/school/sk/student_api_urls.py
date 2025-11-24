from django.urls import path
from .student_api_views import (
    StudentDashboardAPI,
    StudentCoursesListAPI,
    StudentLessonsListAPI,
    StudentBalanceAPI,
    StudentPaymentsListAPI,
    StudentCreatePaymentAPI,
    StudentSeasonSummaryAPI,
)

urlpatterns = [
    path('dashboard/', StudentDashboardAPI.as_view()),           # GET
    path('courses/', StudentCoursesListAPI.as_view()),           # GET
    path('lessons/', StudentLessonsListAPI.as_view()),           # GET
    path('balance/', StudentBalanceAPI.as_view()),               # GET
    path('payments/', StudentPaymentsListAPI.as_view()),         # GET
    path('payments/create/', StudentCreatePaymentAPI.as_view()), # POST
    path('season/summary/', StudentSeasonSummaryAPI.as_view()),  # GET
]
