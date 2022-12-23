from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponse, redirect

# Authenticate user using email
class EmailAuthBackend():
	def authenticate(self, request, username, password):
		try:
			user = User.objects.get(email=username)
			if user.check_password(password):
				return user

		except:
			print("not logged in")
			return None
		return None

	def get_user(self,user_id):
		try:
			return User.objects.get(pk=user_id)
		except:
			return None