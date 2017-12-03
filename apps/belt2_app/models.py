#-*- coding: utf-8 -*-
# Python Tuples are Not Just Constant Lists
# () is a tuple: An immutable collection of values, usually (but not necessarily) of different types.
# [] is a list: A mutable collection of values, usually (but not necessarily) of the same type.
# {} is a dict: Use a dictionary for key value pairs.
# For the difference between lists and tuples see here. See also:

from __future__ import unicode_literals
from django.db import models
from datetime import datetime, date
import re
import bcrypt


#EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+.[a-zA-Z]+$')
#THESE WILL BE COMBINED TO ALLOW either an EMAIL or USERNAME type of string in USERNAME field:

EMAIL_REGEX = re.compile(r'^([a-zA-Z0-9]+[a-zA-Z0-9-_]?[a-zA-Z0-9]+@[a-zA-Z]+([a-zA-Z0-9-_]?[a-zA-Z0-9])*?\.+[a-zA-Z]+)$')
UNAME_REGEX = re.compile(r'^([a-zA-Z]+([0-9]*[-_]?[a-zA-Z0-9]+)*)$')
TRY_COMBO_REGEX = re.compile(EMAIL_REGEX or UNAME_REGEX)
NAME_REGEX = re.compile(r'^([a-zA-Z]+(\ ?[a-zA-Z]\ ?)*[a-zA-Z]+)$')
#PSWD_REGEX = re.compile(r'^(?=.?\d)(?=.?[A-Z])(?=.?[a-z])(?=.[$@$!%?&])[A-Za-z\d$@$!%?&]{8,}$')

# Create your models here.

#No methods in our new manager should ever catch the whole request object!!! 
# (Just parts, ex. request.POST)
class UserManager(models.Manager):
# unpacking of postData is via a * (i.e. star) if postData is a list, and ** (i.e. kwargs) if
# postData is a dictionary. Ex: def validate_user(self, **postData)
        def validate_user(self, postData):
                response_to_views = {}
                errors = {}
                # errors=[]

                print "****************In UserManager: validate_user method*****************"
                print postData
                #Validations example: error["desc"] = "Blog desc should be more than 10 characters" if using error tags.
                name = postData['name'].strip(' \t\n\r')
                print "stripped name: ",name
                reg_user_name = postData['reg_user_name'].strip(' \t\n\r')
                print "stripped reg_user_name", reg_user_name
                # name= postData['name'].strip(' \t\n\r')
                if len(name)<3:
                        # errors.append("Name is required!")
                        errors["name"]="Name is required!"
                elif not NAME_REGEX.match(name):
                        print (NAME_REGEX.match(name))
                        errors["name"]="Your entered Name has either numeric or special characters. \nOnly alphabetic characters and spaces are allowed in the Name field."                
                if len(reg_user_name)<3:
                        errors["reg_user_name"]="Username is required to be 3 or more characters!"
                elif not TRY_COMBO_REGEX:
                        errors["reg_user_name"]="Username format is incorrect via TRY_COMBO_REGEX."
                        print errors["reg_user_name"]
                elif not (EMAIL_REGEX.match(reg_user_name) or UNAME_REGEX.match(reg_user_name)):
                        errors["reg_user_name"]="Username format is incorrect. \nEmail can be used for a username or a combination of alphanumberic characters, space and underscore characters.\nCannot start with a number."
                        print errors["reg_user_name"]
                if self.filter(user_name=reg_user_name):
                        errors["reg_user_name"]="There is a already a user registered with this username.\n Would you like to login instead? :)"
                if len(postData['reg_pwd'])<8:
                        errors["reg_pwd"] ="Password must be at least 8 chars long!"
                if len(postData['conf_pwd'])<1:
                        errors["conf_pwd"] = "Please confirm your password!"
                if not postData['reg_pwd'] == postData['conf_pwd']:
                        if errors["conf_pwd"]:
                                errors["conf_pwd"] = errors["conf_pwd"] + "Form passwords must match!"
                        else:
                                errors["conf_pwd"]="Form passwords must match!"
                #check the errors [] or errors{} for failed validations:
                if errors:
                        response_to_views['status']= False
                        response_to_views['errors']= errors
                        print ("post validations in the if_errors statement, and printing the recorded errors: ", response_to_views['errors'])
                else:
                        response_to_views['status']= True
                        h_reg_pwd = bcrypt.hashpw(postData['reg_pwd'].encode("utf-8"), bcrypt.gensalt())
                        response_to_views['user']=self.create(name=name, user_name=reg_user_name, password=h_reg_pwd)
                return response_to_views

        def validate_login(self, postData):
        # So now the request.POST (a dict type object) 
        # can be accessed like this:
        # postData['form_field'] or postData['password'] etc..
        # .get gets 1 back (an actual object)
        # .get freaks out if 1) you get more than one
        # AND if 2) you get 0.  LOL!!
        # .find returns a list! So does .filter! :)
        # Can do this:
        # user = self.find(email=postData['email'])
        # BUT NOT: user = User.find(email=postData['email'])  ( UserManager class which 
        # inherits from "models.Manager" does not have any reference or knowledge of User class outside of the 'self' object!)
        # ...and an empty or non-empty list sent back to us as result.        
                print "************************* in login_validation Manager method*************************"
                response_to_views= {} #as a dictionary
                # the .get() method would give us an error if the email does not exist in the User table!
                # so we user .filter(), like " usr = self.filter(email = postData['l_email']) "
                
                l_user_name = postData['l_user_name'].strip(' \t\n\r')
                l_user_name = l_user_name.lower()
                u = self.filter(user_name = l_user_name)
                u = self.filter(user_name = l_user_name) 
                print ("Shown object, if found user with this email: ", u)  
                
                if u:
                        print "this is the original field: " + postData['l_user_name']
                        print "this is the stripped user_name: "+ l_user_name  
                        print "entered password: ", postData['l_pwd']
                        stored_hash = u[0].password
                        print ("this is the hashed pwd in db: " + stored_hash)
                        if not bcrypt.checkpw(postData['l_pwd'].encode("utf-8"), stored_hash.encode("utf-8")):
                        # could also encrypt same and compare:
                        # input_hash = bcrypt.hashpw(postData['l_pwd'].encode("utf-8"), bcrypt.gensalt())
                        # if not input_hash == stored_hash:
                                response_to_views['status']=False
                                response_to_views['error']="Invalid Password on Login. Please try again."
                        else:
                                response_to_views['status']=True
                                response_to_views['user']=u[0]
                else: #invalid l_user_name
                        response_to_views["status"]=False
                        response_to_views['error']="Login E-mail is not recognized. Please re-enter."
                return response_to_views

# Create your models here.
class User(models.Model):
        # Django has pre-built validations, such as specifying a field to
        # be unique. Ex: name = models.CharField(max_length = 255, uniquefield)
        name = models.CharField(max_length=255)
        user_name = models.CharField(max_length=255)
        # btw SQLite has also a special:
        # email = models.EmailField()
        # instead of the regex formatting, can use this for properly 
        # formatted emails!
        password = models.CharField(max_length=255)
        created_at = models.DateTimeField(auto_now_add = True)
        updated_at = models.DateTimeField(auto_now = True)
        objects = UserManager() # (only needed if you need custom model methods such as validations)
        def __repr__(self):
                return "<User object:   Name: {}, UserName: {}, \n Password: {}, Created: {}, Updated: {}>".format(self.name, self.user_name, self.password, self.created_at, self.updated_at)
        
        # DEBUGGING:
        # If you have this unicode code in place, then when you print an object in the terminal, 
        # it will display with the information
        # you have specified (useful for debugging)
        #     def __unicode__(self):
        #             return "id: " + str(self.id) + ", email: " + self.email 
        # We could also create __str__ or __repr__ method in the class to handle how we want the objects to print =) !!


class PlanManager(models.Manager):
# unpacking of postData is via a * (i.e. star) if postData is a list, and ** (i.e. kwargs) if
# postData is a dictionary. Ex: def validate_user(self, **postData)
        def validate_plan(self, postData, logged_user):
                response_to_views = {}
                errors = {}
                # errors=[]

                print "****************In PlanManager: validate_plan method*****************"
                print postData
                #Validations example: error["desc"] = "Blog desc should be more than 10 characters" if using error tags.
                dest = postData['dest'].strip(' \t\n\r')
                if len(dest)<3:
                # errors.append("Name is required!")
                        errors["dest"]="Destination is required!"                
                if not postData['start_date']:
                        errors["start_date"] ="You have to select a start date."
                if not postData['start_date'] > unicode(date.today()):
                        errors["start_date"] ="Start Date has to be in the future! Please re-select."
                if not postData['end_date']:
                            errors["end_date"] ="You have to select an End Date."
                if not postData['end_date'] > postData['start_date']:
                        errors["end_date"] ="End Date can not be before the Start Date!"
                if len(postData['desc'])<1:
                    # errors.append("Name is required!")
                        errors["desc"]="Description field cannot be left blank."
                if errors:
                        response_to_views['status']= False
                        response_to_views['errors']= errors
                        print ("Post the validations in the if_errors statement of PlanManager. Errors are: ", response_to_views['errors'])
                else:
                        response_to_views['status']= True
                        new_plan=self.create(dest=postData['dest'], start_date=postData['start_date'], end_date=postData['end_date'], desc=postData['desc'], created_by=User.objects.get(id=logged_user))
                        # new_plan={'dest':postData['dest'], 'start_date':postData['start_date'], 'end_date':postData['end_date'], 'desc':postData['desc']}
                        # response_to_views['new_plan']=new_plan

                return response_to_views


class Plan(models.Model):
        dest = models.CharField(max_length=255)
        start_date = models.DateField()
        end_date= models.DateField()
        desc = models.TextField()
        created_by = models.ForeignKey(User, related_name="created_it")
        shared_by = models.ManyToManyField(User, related_name="going_on")
        created_at = models.DateTimeField(auto_now_add = True)
        updated_at = models.DateTimeField(auto_now = True)
        objects = PlanManager() # (only needed if you need custom model methods such as validations)
        def __repr__(self):
                return "<Plan object:   Dest: {}, Start_Date: {}, End_Date: {}, Desc: {}, Created_By: {}, Shared_By: {}, Created_at: {}, Updated_at: {}>".format(self.dest, self.start_date, self.end_date, self.desc, self.created_by, self.shared_by, self.created_at, self.updated_at)
