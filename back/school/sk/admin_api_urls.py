from django.urls import path
from .admin_api_views import (
    AdminUserListAPI, AdminSetRoleAPI,
    AdminPaymentListAPI, AdminPaymentConfirmAPI, AdminBalanceGetAPI,
    AdminLessonListAPI, AdminLessonDebitAPI,
    AdminAuditLogListAPI,
)

urlpatterns = [
    # USERS
    path('users/', AdminUserListAPI.as_view()),                             # GET (фильтры: role, search, ordering)
    path('users/<int:pk>/set-role/', AdminSetRoleAPI.as_view()),            # PATCH {"role": "TEACHER"}

    # PAYMENTS / BALANCE
    path('payments/', AdminPaymentListAPI.as_view()),                       # GET/POST
    path('payments/<int:pk>/confirm/', AdminPaymentConfirmAPI.as_view()),   # POST {"lessons_to_add": 4}
    path('students/<int:student_id>/balance/', AdminBalanceGetAPI.as_view()),

    # LESSONS
    path('lessons/', AdminLessonListAPI.as_view()),                         # GET/POST
    path('lessons/<int:pk>/debit/', AdminLessonDebitAPI.as_view()),         # POST {"mark_done": true}

    # AUDIT LOG
    path('audit/', AdminAuditLogListAPI.as_view()),                         # GET (search/order)
]
