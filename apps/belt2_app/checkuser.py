from django.http import HttpResponseRedirect
from django.contrib import messages

# @ensure_current_user
def ensure_current_user(function):
  def wrap(req, *args, **kwargs):
    if not 'user_id' in req.session:
      messages.error(req, 'Please log in first.')
      return HttpResponseRedirect('/')
    else:
      return function(req, *args, **kwargs)
  wrap.__doc__ = function.__doc__
  wrap.__name__ = function.__name__
  return wrap
