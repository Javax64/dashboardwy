from django.shortcuts import render
from django.core.mail import send_mail
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect
from applications.users.mixins import AdminPermisoMixin
from django.views.generic import (
    View,
    CreateView,
    ListView,
    UpdateView,
    DeleteView
)

from django.views.generic.edit import (
    FormView
)

from .forms import (
    UserRegisterForm, 
    LoginForm,
    UserUpdateForm,
    UpdatePasswordForm,
)
#
from .models import User
# 


class UserRegisterView(AdminPermisoMixin,FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('users_app:user-lista')
    

    def form_valid(self, form):
        #
        User.objects.create_user(
            form.cleaned_data['username'],
            form.cleaned_data['password1'],
            full_name=form.cleaned_data['full_name'],
            ocupation=form.cleaned_data['ocupation'],
            genero=form.cleaned_data['genero'],
            date_birth=form.cleaned_data['date_birth'],
        )
        # enviar el codigo al email del user
        
        return super(UserRegisterView, self).form_valid(form)
    
    


class LoginUser(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('venta_app:venta-menu')

    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        login(self.request, user)
        if user.is_superuser:
            print("si es superuser")
            return HttpResponseRedirect(reverse('admin_app:admin-dashboard'))
        # Redirigir según la ocupación del usuario
        if user.ocupation == User.VENTAS:
            return HttpResponseRedirect(reverse('venta_app:venta-menu'))  # Redirigir a la página de ventas
        elif user.ocupation == User.ALMACEN:
            return HttpResponseRedirect(reverse('producto_app:producto-lista'))  # Redirigir a la página de almacén
        elif user.ocupation == User.ADMINISTRADOR:
            return HttpResponseRedirect(reverse('admin_app:admin-dashboard'))  # Redirigir a la página de admin
        else:
            return super(LoginUser, self).form_valid(form)
        

class LogoutView(View):

    def get(self, request, *args, **kargs):
        logout(request)
        return HttpResponseRedirect(
            reverse(
                'users_app:user-login'
            )
        )



class UserUpdateView(AdminPermisoMixin,UpdateView):
    template_name = "users/update.html"
    model = User
    form_class = UserUpdateForm
    success_url = reverse_lazy('users_app:user-lista')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el objeto de usuario
        user = self.get_object()
        
        # Asegúrate de que el formulario está correctamente inicializado con el objeto del usuario
        form = self.form_class(instance=user)
        
        # Pasar tanto el formulario como el objeto del usuario al contexto
        context['form'] = form
        context['user'] = user
        
        return context

class UserDeleteView(AdminPermisoMixin, DeleteView):
    model = User
    success_url = reverse_lazy('users_app:user-lista')


class UpdatePasswordView(AdminPermisoMixin, FormView):
    template_name = 'users/update_pass.html'
    form_class = UpdatePasswordForm
    success_url = reverse_lazy('users_app:user-lista')

    def form_valid(self, form):
        user_id = self.kwargs['user_id']

        # Busca al usuario por su ID
        try:
            usuario = User.objects.get(id=user_id)
        except User.DoesNotExist:
            # Si no se encuentra el usuario, redirige a la lista de usuarios o muestra un mensaje
            return redirect('users_app:user-lista')

        # Cambia la contraseña del usuario
        new_password = form.cleaned_data['password1']
        usuario.set_password(new_password)
        usuario.save()
        update_session_auth_hash(self.request, usuario)
       
        return super(UpdatePasswordView, self).form_valid(form)


class UserListView(AdminPermisoMixin,ListView):
    template_name = "users/lista.html"
    context_object_name = 'usuarios'

    def get_queryset(self):
        return User.objects.usuarios_sistema()
    

