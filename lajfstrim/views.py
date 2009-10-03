from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.template import Context, loader, RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django.utils.translation import ugettext as _

from django import forms

from django.contrib.auth import authenticate, login

from lajfstrim.models import Feed, Site, Item, UserProfile, UserUserRelation
from django.contrib.auth.models import User

def smart_redirect(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/user/"+str(request.user.username)+"/")
    else:
        return HttpResponseRedirect("/")

def login_user(request):
    import django.contrib.auth.views
    if not request.user.is_authenticated():
        return django.contrib.auth.views.login(request, template_name='registration/login.html')
    else:
        return HttpResponseRedirect("/user/"+str(request.user.username)+"/")

class RegisterForm(forms.Form):
        """
        Standard registration form
        """
        login = forms.CharField(min_length=3, max_length=30)
        password1 = forms.CharField(min_length=6)
        password2 = forms.CharField(min_length=6)
        email = forms.EmailField()
        def clean(self):
                # check if passwords match
                if 'password2' in self.cleaned_data and 'password1' in self.cleaned_data and self.cleaned_data['password2'] != self.cleaned_data['password1'] :
                        raise forms.ValidationError(_("Passwords do not match."))
                # check if login is free
                try:
                        User.objects.get(username=self.cleaned_data['login'])
                except:
                        pass
                else:
                        raise forms.ValidationError(_("Login already taken"))
                # check if email isn't used already
                try:
                        User.objects.get(email=self.cleaned_data['email'])
                except:
                        pass
                else:
                        raise forms.ValidationError(_("Email already taken"))

                return self.cleaned_data

def register(request):
        """
        User registration
        """
        if not request.user.is_authenticated():
            form =  RegisterForm()
            if request.POST:
                    data = request.POST.copy()
                    data['login'] = data['login']
                    data['email'] = data['email']

                    form = RegisterForm(data)

                    if form.is_valid():
                            data = form.cleaned_data
                            try:
                                    user = User.objects.create_user(data['login'], data['email'], data['password1'])
                            except Exception:
                                    data['reply'] = ''
                                    return render_to_response(
                                            'registration/registration.html',
                                            {'form': form, 'error': True})
                            else:
                                    user.save()
                                    up = UserProfile()
                                    up.user_id = user.id
                                    up.save()
                                    user = authenticate(username=data['login'], password=data['password1'])
                                    if user is not None:
                                            login(request, user)
                                    return render_to_response('msg.html', {'user': request.user, 'msg': _('Registration compleated. You have been logged in succesfuly.'), 'redirect_to': '/user/'+str(request.user.username)+'/'})
                    else:
                            data['reply'] = ''
                            # newforms are bad... ;)
                            if '__all__' in form.errors:
                                    if str(form.errors['__all__']).find(_("Login already taken")) != -1:
                                            form.errors['login'] = [_("Login already taken"),]
                                    if str(form.errors['__all__']).find(_("Email already taken")) != -1:
                                            form.errors['email'] = [_("Email already taken"),]
                                    if str(form.errors['__all__']).find(_("Passwords do not match.")) != -1:
                                            form.errors['password1'] = [_("Passwords do not match."),]
                            return render_to_response(
                                    'registration/registration.html',
                                    {'form': form, 'error': True})

            return render_to_response(
                    'registration/registration.html',
                    {'form': form})
        else:
            return render_to_response('msg.html', {'msg': _('You are already logged in.'), 'redirect_to': '/user/'+str(request.user.username)+'/'}, context_instance=RequestContext(request))


def index(request):
    users = User.objects.all().order_by('-id')[:10]
    return render_to_response("lifestream/main.html", {'users': users},
        context_instance=RequestContext(request))

def user_mainsite(request, user, section_view=None):
    """ Main, default view. """
    owner = get_object_or_404(User, username=user)
    #section_view related stuff, looks pretty crappy for now
    if section_view == 'my':
        items = owner.item_set.all().order_by("-date")
    elif section_view == 'friends':
        friend_feeds = owner.useruserrelation_set.all()
        friend_ids = []
        for i in range(len(friend_feeds)):
            friend_ids.append(friend_feeds[i].friend_id)

        items = Item.objects.filter(user__in=friend_ids).order_by("-date")
    else:
        section_view = 'both'
        friend_feeds = owner.useruserrelation_set.all()
        friend_ids = []
        friend_ids.append(owner.id)
        for i in range(len(friend_feeds)):
            friend_ids.append(friend_feeds[i].friend_id)
        items = Item.objects.filter(user__in=friend_ids).order_by("-date")
    #end of section_view stuff
    paginator = Paginator(items, 25)
    
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        items = paginator.page(page)
    except (EmptyPage, InvalidPage):
        items = paginator.page(paginator.num_pages)

    about_owner = owner.get_profile().about_me
    #people who added you as friend
    people_who_adds_you = UserUserRelation.objects.filter(friend=owner.id)
    #people added by you as friends
    people_added_by_you = UserUserRelation.objects.filter(user=owner.id)

    if request.user.is_authenticated() == True:
        if not request.user.useruserrelation_set.filter(friend=owner.id):
            is_friend = False
        else:
            is_friend = True
    else:
        is_friend = False

    return render_to_response("lifestream/user_main.html", {'people_who_adds_you': people_who_adds_you, 'people_added_by_you': people_added_by_you, 'items': items, 'owner': owner, 'about_owner': about_owner, 'view_type': section_view, 'type': type, 'is_friend': is_friend},
        context_instance=RequestContext(request))

def user_mainsite_timeline(request, user):
    """ Main, default view. """
    import datetime
    owner = get_object_or_404(User, username=user)
    items = owner.item_set.filter(date__month=datetime.date.today().month).order_by("-date")
    item = {}
    for i in range(items.count()):
        if(item.has_key(items[i].date.day) == False):
            item[items[i].date.day] = []
            item[items[i].date.day].append(items[i])
        else:
            item[items[i].date.day].append(items[i])

    about_owner = owner.get_profile().about_me
    #people who added you as friend
    people_who_adds_you = UserUserRelation.objects.filter(friend=owner.id)
    #people added by you as friends
    people_added_by_you = UserUserRelation.objects.filter(user=owner.id)

    if request.user.is_authenticated() == True:
        if not request.user.useruserrelation_set.filter(friend=owner.id):
            is_friend = False
        else:
            is_friend = True
    else:
        is_friend = False

    return render_to_response("lifestream/user_main_timeline.html", {'people_who_adds_you': people_who_adds_you, 'people_added_by_you': people_added_by_you, 'items': item, 'owner': owner, 'about_owner': about_owner, 'is_friend': is_friend},
        context_instance=RequestContext(request))

def add_friend(request, user):
    owner = get_object_or_404(User, username=user)
    if request.user.is_authenticated() == True:
        print request.user.useruserrelation_set.filter(friend=owner.id) 
        if not request.user.useruserrelation_set.filter(friend=owner.id):
            uur = UserUserRelation()
            uur.user = request.user
            uur.friend = owner
            uur.save()
            item = Item()
            item.user = request.user
            item.type = 'friend'
            item.link = '/user/%s/' % (owner.username)
            item.body = owner.username
            item.save()
            return render_to_response("msg.html", {'msg': _('Friend added to your friendlist successfuly.'), 'redirect_to': '/user/'+str(owner.username)+'/'},
                context_instance=RequestContext(request))
        return render_to_response("msg.html", {'msg': _('You have this user in friends.'), 'redirect_to': '/user/'+str(owner.username)+'/'},
            context_instance=RequestContext(request))
    return render_to_response("msg.html", {'msg': _('You are not logged in.'), 'redirect_to': '/user/'+str(owner.username)+'/'},
        context_instance=RequestContext(request))

def remove_friend(request, user):
    owner = get_object_or_404(User, username=user)
    if request.user.is_authenticated() == True:
        if request.user.useruserrelation_set.filter(friend=owner.id):
            uur = request.user.useruserrelation_set.filter(friend=owner.id)
            uur.delete()

            return render_to_response("msg.html", {'msg': _('Friend removed from your friendlist successfuly.'), 'redirect_to': '/user/'+str(owner.username)+'/'},
                context_instance=RequestContext(request))
        return render_to_response("msg.html", {'msg': _('You have no this user in friends.'), 'redirect_to': '/user/'+str(owner.username)+'/'},
            context_instance=RequestContext(request))
    return render_to_response("msg.html", {'msg': _('You are not logged in.'), 'redirect_to': '/user/'+str(owner.username)+'/'},
        context_instance=RequestContext(request))

def remove_friend(request, user, id):
    owner = get_object_or_404(User, username=user)
    if request.user.is_authenticated() == True:
        if request.user.useruserrelation_set.filter(friend=owner.id):
            uur = request.user.useruserrelation_set.filter(friend=owner.id)
            uur.delete()

            return render_to_response("msg.html", {'msg': _('Friend removed from your friendlist successfuly.'), 'redirect_to': '/user/'+str(owner.username)+'/'},
                context_instance=RequestContext(request))
        return render_to_response("msg.html", {'msg': _('You have no this user in friends.'), 'redirect_to': '/user/'+str(owner.username)+'/'},
            context_instance=RequestContext(request))
    return render_to_response("msg.html", {'msg': _('You are not logged in.'), 'redirect_to': '/user/'+str(owner.username)+'/'},
        context_instance=RequestContext(request))

def show_id(request, user, id):
    """ Main, default view. """
    owner = get_object_or_404(User, username=user)
    item = get_object_or_404(Item, pk=id)

    about_owner = owner.get_profile().about_me
    #people who added you as friend
    people_who_adds_you = UserUserRelation.objects.filter(friend=owner.id)
    #people added by you as friends
    people_added_by_you = UserUserRelation.objects.filter(user=owner.id)

    if request.user.is_authenticated() == True:
        if not request.user.useruserrelation_set.filter(friend=owner.id):
            is_friend = False
        else:
            is_friend = True
    else:
        is_friend = False

    return render_to_response("lifestream/show_id.html", {'people_who_adds_you': people_who_adds_you, 'people_added_by_you': people_added_by_you, 'item': item, 'owner': owner, 'about_owner': about_owner, 'is_friend': is_friend},
        context_instance=RequestContext(request))

### USER ADMIN SECTION ###

def user_admin(request):
    if request.user.is_authenticated() == True:
        about_user = request.user.get_profile().about_me
        return render_to_response("lifestream/admin_main.html", {'about_user': about_user},
            context_instance=RequestContext(request))
    return render_to_response("msg.html", {'msg': _('You are not logged in.'), 'redirect_to': '/'},
        context_instance=RequestContext(request))

class UserAdminUserForm(forms.ModelForm):
    class Meta:
        # Model name
        model = UserProfile
        exclude = ('user',)

def user_admin_user(request):
    if request.user.is_authenticated() == True:
        about_user = request.user.get_profile().about_me
        if request.POST:
            data = request.POST.copy()
            form = UserAdminUserForm(data)
            if form.is_valid():
                data = form.save(commit=False)
                up = UserProfile.objects.get(user=request.user)
                if data.jid:
                    up.jid = data.jid
                if data.about_me:
                    up.about_me = data.about_me
                if data.site_title:
                    up.site_title = data.site_title
                up.save()
                return render_to_response("msg.html", {'msg': _('Changes saved successfuly.'), 'redirect_to': '/user/'+str(request.user.username)+'/'},
                    context_instance=RequestContext(request))
        else:
            up = UserProfile.objects.get(user=request.user)
            form = UserAdminUserForm(instance=up)
            return render_to_response(
                    'lifestream/admin_form.html',
                    {'form': form, 'about_user': about_user}, context_instance=RequestContext(request))
    return render_to_response("msg.html", {'msg': _('You are not logged in.'), 'redirect_to': '/'},
        context_instance=RequestContext(request))

class UserAdminFeedForm(forms.ModelForm):
    class Meta:
        # Model name
        model = Feed
        exclude = ('user', 'etag')

def user_admin_feed(request, id=None):
    if request.user.is_authenticated() == True:
        about_user = request.user.get_profile().about_me
        if request.POST:
            data = request.POST.copy()
            form = UserAdminFeedForm(data)
            if form.is_valid():
                if id != None:
                    data = form.save(commit=False)
                    feed = Feed.objects.get(pk=id)
                    if data.name:
                        feed.name = data.name
                    if data.link:
                        feed.link = data.link
                    feed.save()
                else:
                    data = form.save(commit=False)
                    data.user = request.user
                    data.save()
                return render_to_response("msg.html", {'msg': _('Changes saved successfuly.'), 'redirect_to': '/user/'+str(request.user.username)+'/'},
                    context_instance=RequestContext(request))
        else:
            if id != None:
                feed = get_object_or_404(Feed, pk=id)
                form = UserAdminFeedForm(instance=feed)
            else:
                form = UserAdminFeedForm()
            return render_to_response(
                    'lifestream/admin_form.html',
                    {'form': form, 'about_user': about_user}, context_instance=RequestContext(request))
    return render_to_response("msg.html", {'msg': _('You are not logged in.'), 'redirect_to': '/'},
        context_instance=RequestContext(request))


class UserAdminSiteForm(forms.ModelForm):
    class Meta:
        # Model name
        model = Site
        exclude = ('user',)

def user_admin_site(request, id=None):
    if request.user.is_authenticated() == True:
        about_user = request.user.get_profile().about_me
        if request.POST:
            data = request.POST.copy()
            form = UserAdminSiteForm(data)
            if form.is_valid():
                if id != None:
                    data = form.save(commit=False)
                    site = Site.objects.get(pk=id)
                    if data.username:
                        site.username = data.username
                    if data.site:
                        site.site = data.site
                    site.save()
                else:
                    data = form.save(commit=False)
                    data.user = request.user
                    data.save()
                return render_to_response("msg.html", {'msg': _('Changes saved successfuly.'), 'redirect_to': '/user/'+str(request.user.username)+'/'},
                    context_instance=RequestContext(request))
        else:
            if id != None:
                site = get_object_or_404(Site, pk=id)
                form = UserAdminSiteForm(instance=site)
            else:
                form = UserAdminSiteForm()
            return render_to_response(
                    'lifestream/admin_form.html',
                    {'form': form, 'about_user': about_user}, context_instance=RequestContext(request))
    return render_to_response("msg.html", {'msg': _('You are not logged in.'), 'redirect_to': '/'},
        context_instance=RequestContext(request))


def user_admin_site_feed_management(request, type):
    if request.user.is_authenticated() == True:
        about_user = request.user.get_profile().about_me
        if type == 'feed':
            items = Feed.objects.filter(user=request.user)
        if type == 'site':
            items = Site.objects.filter(user=request.user)
        return render_to_response(
                'lifestream/admin_management.html',
                {'type': type, 'items': items, 'about_user': about_user}, context_instance=RequestContext(request))
    return render_to_response("msg.html", {'msg': _('You are not logged in.'), 'redirect_to': '/'},
        context_instance=RequestContext(request))

