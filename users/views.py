from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import Group,Permission
from users.forms import LoginForm,CustomPasswordChangeForm,CustomPasswordResetConfirmForm,CustomPasswordResetForm,CustomRegistrationForm,AssignRoleForm,CreateGroupForm,EditGroupForm,EditProfileForm
from django.contrib.auth import  login,logout,get_user_model
from django.db.models import Prefetch,Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.urls import reverse,reverse_lazy
from django.views.generic.edit import CreateView,DeleteView,UpdateView
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import  PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from datetime import datetime



User = get_user_model()

def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def sign_up(request):
    form = CustomRegistrationForm()  
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))  
            user.is_active = False  
            user.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_url = request.build_absolute_uri(
                reverse('activate', kwargs={'uidb64': uid, 'token': token})
            )
            subject = "Activate Your Account"
            message = f"""
            Hi {user.username},
            Please activate your account by clicking the link below:
            {activation_url}
            If you did not request this, please ignore this email.
            Regards,
            Event Management Team
            """
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            try:
                send_mail(subject, message, from_email, recipient_list)
                messages.success(request, 'A confirmation email has been sent. Please check your inbox.')  
            except Exception as e:
                messages.error(request, f"Email sending failed: {e}") 
            return redirect('sign-in')   #sign-in hobe
        else:
            messages.error(request, "Form is not valid. Please correct the errors.") 
    return render(request, 'registration/register.html', {"form": form})


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated! You can now log in.")
        participant_group, created = Group.objects.get_or_create(name='Participant')
        user.groups.add(participant_group)
        return redirect('sign-in') #sign in hobe
    else:
        messages.error(request, "Invalid or expired activation link.")
        return redirect('sign-up')
    


@never_cache
@require_http_methods(["GET", "POST"])
def sign_in(request):
    if request.user.is_authenticated:
        messages.info(request, "You're already logged in!")
        return redirect('event_list')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)  
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next') or 'event_list'
            return redirect(next_url)
        
        messages.error(request, "Invalid credentials. Please try again.")
    else:
        form = LoginForm(request)
    
    return render(request, 'registration/login.html', {
        'form': form,
        'next': request.GET.get('next', '')
    })


@login_required
def sign_out(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('home') #  home hobe

@user_passes_test(is_admin, login_url='no-permission')
def admin_dashboard(request):
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    )
    for user in users:
        user.group_name = user.all_groups[0].name if user.all_groups else "No Group Assigned"
    
    return render(request, 'admin/dashboard.html', {"users": users})

@user_passes_test(is_admin, login_url='no-permission')
def assign_role(request, user_id):
    user = get_object_or_404(User, id=user_id)  
    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')  
            if isinstance(role, Group):  
                user.groups.clear()  
                user.groups.add(role) 
                messages.success(request, f"User {user.username} has been assigned to the '{role.name}' role.")
                return redirect('admin-dashboard')  
            else:
                messages.error(request, "Invalid role selection. Please try again.")
    else:
        form = AssignRoleForm()
    return render(request, 'admin/assign_role.html', {'form': form, 'user': user})



# @user_passes_test(is_admin, login_url='no-permission')
# def create_group(request):
#     if request.method == 'POST':
#         form = CreateGroupForm(request.POST)
#         if form.is_valid():
#             group = form.save()
#             messages.success(request, f"Group '{group.name}' created successfully")
#             return redirect('group-list') 
#     else:
#         form = CreateGroupForm()  
    
#     return render(request, 'admin/create_group.html', {'form': form})

class CreateGroupView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Group
    form_class = CreateGroupForm
    template_name = 'admin/create_group.html'
    success_url = reverse_lazy('group-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Group '{form.instance.name}' created successfully")
        return response
    def test_func(self):
        return self.request.user.is_superuser 
    def handle_no_permission(self):
        return redirect('no-permission')


@user_passes_test(is_admin, login_url='no-permission')
def group_list(request):
    # Only fetch the fields you need
    groups = Group.objects.only('id', 'name').prefetch_related(
        Prefetch('permissions', queryset=Permission.objects.only('id', 'name', 'codename'))
    )
    return render(request, 'admin/group_list.html', {'groups': groups})



# @user_passes_test(is_admin, login_url='no-permission')
# def delete_group(request, group_id):
#     group = get_object_or_404(Group, id=group_id)   
#     if request.method == 'POST':
#         group_name = group.name
#         group.delete()
#         messages.success(request, f"Group '{group_name}' has been deleted successfully")
#         return redirect('group-list')
#     return render(request, 'admin/confirm_delete_group.html', {'group': group})

class DeleteGroupView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Group
    template_name = 'admin/confirm_delete_group.html'
    context_object_name = 'group'
    success_url = reverse_lazy('group-list')
    pk_url_kwarg = 'group_id'

    def form_valid(self, form):
        group_name = self.object.name
        messages.success(self.request, f"Group '{group_name}' has been deleted successfully")
        return super().form_valid(form)
    def test_func(self):
        return self.request.user.is_superuser  
    def handle_no_permission(self):
        return redirect('no-permission')



@login_required
@user_passes_test(is_admin, login_url='no-permission')
def user_list(request):
    search_query = request.GET.get('q', '')
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.filter(name='Organizer'))
    ).order_by('date_joined')
    if search_query:
        sers = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    page_obj = Paginator(users, 10).get_page(request.GET.get('page'))
    for user in page_obj:
        user.group_name = (
            "Admin" if user.is_superuser else
            "Organizer" if hasattr(user, '_prefetched_objects_cache') and 
                          user._prefetched_objects_cache.get('groups') else
            "Participant"
        )
    return render(request, 'admin/user_list.html', {
        'users': page_obj,
        'search_query': search_query,
        })

@user_passes_test(is_admin, login_url='no-permission')
def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        form = EditGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, f"Group '{group.name}' updated successfully")
            return redirect('group-list')
    else:
        form = EditGroupForm(instance=group)
    permissions = Permission.objects.select_related('content_type').order_by('content_type__app_label', 'content_type__model')
    grouped_permissions = {}
    for perm in permissions:
        key = f"{perm.content_type.app_label}.{perm.content_type.model}"
        if key not in grouped_permissions:
            grouped_permissions[key] = {
                'app': perm.content_type.app_label.title(),
                'model': perm.content_type.model.title(),
                'perms': []
            }
        grouped_permissions[key]['perms'].append(perm)
    return render(request, 'admin/edit_group.html', {
        'form': form,
        'group': group,
        'grouped_permissions': grouped_permissions
        })

class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()
        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        context['phone_number'] = user.phone_number
        context['profile_image'] = user.profile_image
        context['bio'] = user.bio

        return context

class EditProfileView(UpdateView):
    model=User
    form_class=EditProfileForm
    template_name='accounts/update_profile.html'
    context_object_name='form'

    def get_object(self):
        return self.request.user
    def form_valid(self,form):
        form.save()
        return redirect('profile')

class ChangePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')
    html_email_template_name = 'registration/reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        context['year'] = datetime.now().year 
        print(context)
        return context

    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset email sent. Please check your email')
        return super().form_valid(form)
    

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')
    html_email_template_name = 'registration/reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        context['year'] = datetime.now().year 
        print(context)
        return context

    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset email sent. Please check your email')
        return super().form_valid(form)
    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        messages.success(
            self.request, 'Password reset successfully')
        return super().form_valid(form)