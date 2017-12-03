# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from django.core.urlresolvers import reverse
from .models import User, UserManager, Plan, PlanManager
from django.contrib import messages
from django.shortcuts import get_list_or_404, get_object_or_404
from checkuser import *

# Create your views here.
def main(request):   
        # @ensure_current_user
        # cannot do (if request.session["user_id"]) because python is unforgiving!
    if "user_id" in request.session:
        print request.session
        request.session.clear()
        return redirect('belt2_app:success')
    else: 
        #context={"my_message" : "Hello, I am your successesful login/registration request"}
        return render(request, 'belt2_app/main.html')
         
def register(request):
    if request.method=='POST':
        print['****************in view method****************']
        print[request.POST]
        response_from_models = User.objects.validate_user(request.POST)
        print['****************back in view method****************']

        #on successful reg validation
        if response_from_models['status']:
            request.session['user_id']= response_from_models['user'].id
            return redirect('/travels')   
        #else return redirect ('/')
        else:
            #HOW MESSAGES WORK/PASSED BACK TO CLIENT:
            # The 'messages' object's methods also require the 'request'
            # object to be passed as a first parameter...
            # These messages are then going to be inside of that 'request' 
            # object to pass them back.

            # If errors in response_from_models is not a dictionary, but a list/array:
            # for error in response_from_models['errors']:
            #     messages.error(request, error)            

            # If errors in response_from_models IS a dictionary of tags and error messages:
            for tag, error in response_from_models['errors'].items():
                print tag, error
                messages.error(request, error, extra_tags=tag)
            return redirect('/')    
    else:
        # not a post, redirect to index method?
        return redirect('/') #our main.html template
    
def login(request):
    if request.method=='POST':
        print['****************in view method****************']
        print[request.POST]
        #invoke my method from the User model manager
        response_from_models = User.objects.validate_login(request.POST)
        print "************************* in login view method*************************"
        print response_from_models
        if response_from_models["status"]:
            request.session["user_id"]=response_from_models['user'].id
            #on successful login validation
            return redirect('/travels')
        else:
            #use the error message to display; will be just one string, so no need to loop through.
            messages.error(request, response_from_models['error'])
            return redirect('/')
    else:
        # not a post, redirect to index method?
        return redirect('belt2_app:index') #our main.html template


def success(request):
    if "user_id" in request.session:
        print "************************* in travels template (successful login) view method*************************"
        # context={"success_str" : "Hello, I am your successesful login/registration request"}
        print "user id of the logged in user is: ", request.session["user_id"]
        # me_id=User.objects.filter(id=request.session["user_id"]).values_list(flat=True)
        # friends_ids=User.objects.get(id=request.session["user_id"]).friends.all().values_list(flat=True)
        # all_users_ids=User.objects.all().values_list(flat=True)
        # not_friends_ids=all_users_ids.difference(me_id, friends_ids)

        me=User.objects.filter(id=request.session["user_id"])
        # print me[0]
        my_plans_created=Plan.objects.filter(created_by=me[0])
        my_plans_joined=Plan.objects.filter(shared_by=me[0])
        all_my_plans= my_plans_created.union(my_plans_joined)
        print all_my_plans.values_list(flat=True)
        # print "My my_plans_created: ", my_plans_created.values_list(flat=True)
        # print "My my_plans_shared: ", my_plans_joined.values_list(flat=True)
        all_plans=Plan.objects.all()
        not_my_plans=Plan.objects.all().exclude(shared_by=me[0]).exclude(created_by=me[0])
        # print "Not mine: ", not_my_plans, not_my_plans.values_list(flat=True)
        #if plan in not_my_plans will evaluate to false because it is looking for that specific object we define first using get, for ex.
        #WOULD WORK if we had that if statement after the for loop statement, btw. It will find a Plan object there.        
        for plan in not_my_plans:
            print not_my_plans
            print "Print if the IF evaluates to True"
            print "Print what we are looking for in queryset: "
        if plan in not_my_plans:
            print "Trying the if plan in queryset after it has been defined in the for loop", plan
        if not_my_plans.exists():
            print "Exists? IF"
        if not_my_plans:
            print "Second IF (checking if quieryset is null or not suggested way) evaluates to true, ie, not empty after all"
        # friends=User.objects.get(id=request.session["user_id"]).friends.all()
        # all_users=User.objects.all()
        # not_friends=all_users.difference(me, friends)
        # print not_friends
        # <!-- Setting Relationships:
        # Comment.objects.create(blog=Blog.objects.get(id=1), comment="test") - create a new comment where the comment's blog points to Blog.objects.get(id=1). -->
        # Blog.objects.raw("SELECT * FROM {{app_name}}_{{class/table name}}") - performs a raw SQL query
        context = {
            'all_my_plans': all_my_plans,
            # 'not_friends': not_friends,
            # 'friends' : friends,
            'not_my_plans': not_my_plans,
            'me' : me[0]
        }
        return render(request, 'belt2_app/success.html', context)
    else:
        print request.session
        request.session.clear()
        return redirect ('/')

def show(request, id):
    if "user_id" in request.session:
        print "************************* in SHOW_PLAN_DETAILS method*************************"
        print "user id of the logged in user is: ", request.session["user_id"]
        me = User.objects.filter(id=request.session["user_id"])
        # print me
        plan = Plan.objects.filter(id=id)[0]
        print plan
        shared_by = plan.shared_by
        print shared_by.all()
        print shared_by.all().values_list(flat=True)
        shared_by_others= shared_by.all().difference(me)
        # shared_by_others=Plan.objects.get(id=id).shared_by.exclude(id=User.objects.get(id=me[0].id).id) 
        context = {
            'shared_by_others':shared_by_others,
            'plan': plan, 
        }

        return render(request, 'belt2_app/profile.html', context)
    else:
        return redirect('belt2_app: logout')

def add_page(request):
    if "user_id" in request.session:
        print "************************* in ADD_PLAN_PAGE VIEW method*************************"
        # context={"success_str" : "Hello, I am your successesful login/registration request"}
        print "user id of the logged in user is: ", request.session["user_id"]
        # me_id=User.objects.filter(id=request.session["user_id"]).values_list(flat=True)
        # friends_ids=User.objects.get(id=request.session["user_id"]).friends.all().values_list(flat=True)
        # all_users_ids=User.objects.all().values_list(flat=True)
        # not_friends_ids=all_users_ids.difference(me_id, friends_ids)

        me=User.objects.filter(id=request.session["user_id"])
        # friends=User.objects.get(id=request.session["user_id"]).friends.all()
        # all_users=User.objects.all()
        # not_friends=all_users.difference(me, friends)
        # print not_friends
        # <!-- Setting Relationships:
        # Comment.objects.create(blog=Blog.objects.get(id=1), comment="test") - create a new comment where the comment's blog points to Blog.objects.get(id=1). -->
        # Blog.objects.raw("SELECT * FROM {{app_name}}_{{class/table name}}") - performs a raw SQL query
        context = {
            # 'not_friends': not_friends,
            # 'friends' : friends,
            'me' : me[0]
        }
        return render(request, 'belt2_app/create.html', context)
    else:
        print request.session
        request.session.clear()
        return redirect ('/')

def create(request):
    if request.method=='POST':
        print['****************in view Create Trip method****************']
        print[request.POST]
        response_from_models = Plan.objects.validate_plan(request.POST, request.session['user_id'] )
        print['****************back in view Create Trip method****************']

        #on successful reg validation
        if response_from_models['status']:
            print['****************Back in View Create Trip method. Successfully received response from PlanModel****************']
            # request.session['plan_id']= response_from_models['plan'].id
            return redirect('/travels')   
        #else return redirect ('/')
        else:
            # If errors in response_from_models is not a dictionary, but a list/array:
            # for error in response_from_models['errors']:
            #     messages.error(request, error)            

            # If errors in response_from_models IS a dictionary of tags and error messages:
            for tag, error in response_from_models['errors'].items():
                print tag, error
                messages.error(request, error, extra_tags=tag)
            return redirect('/travels/add')    
    else:
        # not a post, redirect to index method?
        return redirect('/travels/add') #our main.html template 

def join(request, id):
    print "Someone just called the 'JOIN' method"
    to_join=get_object_or_404(Plan, id=id)
    # to_friend=User.objects.get(id=id)
    logged_user=User.objects.get(id=request.session["user_id"])
    join_result=logged_user.going_on.add(to_join)
    print join_result
    return redirect('belt2_app:success')

def logout(request):
    print "Someone just called the 'logout' method "
    #Need to clear that cookie/session dictionary/table =) !
    request.session.clear()
    return redirect('belt2_app:index')
