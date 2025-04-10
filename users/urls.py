from django.urls import path
from users.views import sign_up,delete_group, edit_group,activate_account,sign_in,sign_out,user_list,admin_dashboard,assign_role,group_list,create_group

urlpatterns = [
    path('sign-up/',sign_up,name='sign-up'),
    path('sign-in/', sign_in, name='sign-in'),
    path('sign_out/',sign_out,name='sign-out'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'), 
    path('admin/dashboard/',admin_dashboard,name='admin-dashboard'),
    path('admin/<int:user_id>/assign-role/',assign_role,name='assign-role'),
    path('admin/create-group/',create_group, name='create-group'),
    path('group/delete/<int:group_id>/', delete_group, name='delete-group'),
    path('groups/edit/<int:group_id>/',edit_group, name='edit-group'),
    path('admin/group-list/',group_list,name='group-list'),
    path('admin/user_list/', user_list, name='user_list'),
    
]
