from django.shortcuts import render
from django.views.generic import DeleteView, UpdateView, CreateView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .talent_form import TalentForm, UserAccountForm

from django.urls import reverse_lazy

from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm

from Talent.models import TalentsPost, Categories, UserAccount
from Talent.filters import TalentFilter
from django.contrib import messages  # Fixed import

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Message

from django.db.models import Q, Max, Count

#______________________________________________________________________________________

#def HomePage(request):
#    posts = TalentsPost.objects.all()
#    return render(
#        request,
#        template_name="home_page.html",
#       context={"TalentsPost": posts}
#    )

### **WITHOUT RELOAD / NO-RELOAD (With AJAX):** SOON

#RELOAD
class HomePageView(ListView):
    model = TalentsPost
    template_name = 'home_page.html'
    context_object_name = 'posts'
    
    def get_queryset(self):
        queryset = TalentsPost.objects.all()
        self.filterset = TalentFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['categories'] = Categories.objects.all()
        return context
#__________________________________________________________________________________
#ADD 

class AddTalentView(LoginRequiredMixin, CreateView):
    model = TalentsPost
    form_class = TalentForm
    template_name = "add_talent.html"
    success_url = reverse_lazy('user_account')
    login_url = reverse_lazy('login')  # Redirctioneaza catre login
    
    def form_valid(self, form):
        form.instance.user = self.request.user  
        messages.success(self.request, "Talent adăugat cu succes!")
        return super().form_valid(form)


#-----------------------------------------------------------------------------------
#ACCOUNT

class UserAccountView(LoginRequiredMixin, ListView):  # Added LoginRequiredMixin
    model = TalentsPost
    template_name = "user_account.html"
#În Django, context este ca o „cutie de date” 📦 tot ce pui în ea ajunge în template (pagina HTML)
    context_object_name = "user_posts"
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return TalentsPost.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if profile exists, if not create it
        profile, created = UserAccount.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        return context
#-------------------------------------------------------------------------------------
#  EDIT -- UPDATE ----DELETE

class FormUpdateView(LoginRequiredMixin, UpdateView):  
    model = TalentsPost
    template_name = 'Form_update.html'
    form_class = TalentForm
    success_url = reverse_lazy('user_account')
    login_url = reverse_lazy('login')
    
    def get_queryset(self):
        # Ensure users can only edit their own posts
        return TalentsPost.objects.filter(user=self.request.user)


class ProfileEdit(LoginRequiredMixin, UpdateView):
    model= UserAccount
    template_name= "edit_profile.html"
    fields = ['bio', 'phone_number', 'photo']
    success_url=reverse_lazy("user_account")
    login_url=reverse_lazy("login")

    def get_object(self):
        profile, created = UserAccount.objects.get_or_create(user=self.request.user)
        if created:
            print("New profile created!")
        else:
            print("Profile already existed!")
        return profile


class FormDeleteView(LoginRequiredMixin, DeleteView): 
    model = TalentsPost
    template_name = 'form_delete.html'
    success_url = reverse_lazy('user_account')
    login_url = reverse_lazy('login')
    
    def get_object(self):
        return TalentsPost.objects.filter(user=self.request.user)

#---------------------------------------------------------------------------------

# Auth views

class CustomLoginView(LoginView):
    template_name = "form.html"
    
    def get_success_url(self):
        messages.success(self.request, "Te-ai conectat cu succes!")
        return reverse_lazy('home')


def logout_view(request):
    logout(request)
    messages.info(request, "Te-ai deconectat cu succes!")
    return redirect('login')


class CustomRegisterView(CreateView):
    template_name = 'form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    
    def form_valid(self, form):
        messages.success(self.request, "Cont creat cu succes! Acum te poți conecta.")
        return super().form_valid(form)
    
#--------------------------------------------------------------

class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        other_user_id = self.kwargs['user_id']
        other_user = get_object_or_404(User, id=other_user_id)  # Get the actual user object
        context['other_user'] = other_user  # Pass user object, not just ID
        
        # Fetch messages between us
        messages = Message.objects.filter(
            sender=self.request.user,
            receiver=other_user,  # Use other_user, not other_user_id
        ) | Message.objects.filter(
            sender=other_user,     # Use other_user, not other_user_id  
            receiver=self.request.user
        )  # You were missing a comma after other_user_id
        
        context['chat_messages'] = messages  # You forgot to add this!
        
        return context
    
    #-----------------------------------------------
class InboxView(LoginRequiredMixin, ListView):
    template_name = 'inbox.html'
    context_object_name = 'conversations'
    login_url = reverse_lazy('login')

    def get_queryset(self):
        user = self.request.user

        sent_to = Message.objects.filter(sender=user).values_list('receiver', flat=True)
        received_from = Message.objects.filter(receiver=user).values_list('sender', flat=True)

        chat_user_ids = set(list(sent_to) + list(received_from))

        conversations = []

        for other_user_id in chat_user_ids:
            other_user = User.objects.get(id=other_user_id)

            last_message = Message.objects.filter(
                Q(sender=user, receiver=other_user) |
                Q(sender=other_user, receiver=user)
            ).order_by('-timestamp').first()

            unread_count = Message.objects.filter(
                sender=other_user,
                receiver=user,
                is_read=False
            ).count()

            conversations.append({
                'user': other_user,
                'last_message': last_message,
                'unread_count': unread_count
            })

        conversations.sort(key=lambda x: x['last_message'].timestamp, reverse=True)

        return conversations