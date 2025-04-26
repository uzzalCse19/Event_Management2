from django.urls import path
from users.views import sign_up,EditProfileView,CustomPasswordResetView,CustomPasswordResetConfirmView,ProfileView,ChangePassword,DeleteGroupView,edit_group,activate_account,sign_in,sign_out,user_list,admin_dashboard,assign_role,group_list,CreateGroupView
from django.contrib.auth.views import PasswordChangeDoneView
urlpatterns = [
    path('sign-up/',sign_up,name='sign-up'),
    path('sign-in/', sign_in, name='sign-in'),
    path('sign_out/',sign_out,name='sign-out'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'), 
    path('admin/dashboard/',admin_dashboard,name='admin-dashboard'),
    path('admin/<int:user_id>/assign-role/',assign_role,name='assign-role'),
    path('admin/create-group/',CreateGroupView.as_view(), name='create-group'),
    path('group/delete/<int:group_id>/',DeleteGroupView.as_view(), name='delete-group'),
    path('groups/edit/<int:group_id>/',edit_group, name='edit-group'),
    path('admin/group-list/',group_list,name='group-list'),
    path('admin/user_list/', user_list, name='user_list'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-change/', ChangePassword.as_view(), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'), name='password_change_done'),
    path('password-reset/',CustomPasswordResetView.as_view(),name='password-reset'),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('edit-profile/', EditProfileView.as_view(), name='edit_profile'),
    
    
]
