from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('question/<int:question_id>/', views.question_view, name='question_view'),
    path('question/admin/<int:user_id>/<int:question_id>/', views.admin_question_view, name='admin_question_view'),
    
    path('run_code/', views.run_code, name='run_code'),  # Add this line
    # path('question/save_timer/<int:question_id>', views.save_timer, name='save_timer'),
    path('question/get_timer/', views.get_timer, name='get_timer'),
    path('error/', views.error, name='error'),
    path('finish/', views.finish, name='finish'),
    
    path('users/', views.user_list, name='user_list'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    
    # path('next_question/', views.next_question_view, name='next_question'),  # Logique à définir
]
