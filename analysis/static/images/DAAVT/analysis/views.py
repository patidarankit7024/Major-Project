from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Contact
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
import re

# Create your views here.
def index(request):
    return render(request,'home.html')

def AboutUs(request):
    return render(request,'about.html')

def  password_validdate(passwd):
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    # compiling regex 
    pat = re.compile(reg) 
    # searching regex                  
    mat = re.search(pat, passwd)
    return mat
    
    
def SignUp(request):
    if request.method=='POST':
         fname = request.POST.get('fname', 'default')
         lname = request.POST.get('lname', 'default')
         username = request.POST.get('username', 'default')  
         domain = request.POST.get('domain', 'default')
         email = request.POST.get('email', 'default')
         passw = request.POST.get('passw', 'default')
         re_pass = request.POST.get('re_pass', 'default')
         
         if len(fname)<3 or fname.isnumeric():
             messages.error(request,"First Name should be string with more than 2 character")
             return render(request,'register.html')
         if len(lname)<3 or lname.isnumeric():
             messages.error(request,"Last Name should be string with more than 2 character")
             return render(request,'register.html')
         if len(passw)<5:
             messages.error(request,'Length of password must be greater or equal to 5')
             return render(request,'register.html')
         if password_validdate(passw):
             messages.error(request,'Password must be alphanumeric')
             return render(request,'register.html')
         elif(passw != re_pass):
             messages.error(request, 'Error! Password does not match')
             return render(request,'register.html')
         else:
             try:
                 myuser= User.objects.get(username=username)
                 if(myuser.username==username):
                     messages.error(request,' User :- '+myuser.username+' already exist ! Please use another number')
                     return render(request, 'register.html')
             except User.DoesNotExist:
                 myuser=User.objects.create_user(username,email,passw)
                 myuser.first_name =fname+" "+lname
                 myuser.last_name = domain
                 myuser.save()
                 
                 user=authenticate(username=username,password=passw)
                 login(request,user)
                 messages.success(request, 'Registered Successfully')
                 return redirect('Home')
                 
    return render(request,'register.html')



def login_user(request):
    if request.method=='POST':
        number = request.POST.get('username', 'default')
        passw = request.POST.get('passw', 'default')

        user=authenticate(username=number,password=passw)
        if user is not None:
            login(request,user)
            messages.success(request,'Successfully Logged in')
            return redirect('Home')
        else:
            messages.error(request,'Error : Invalid Creadentials, Please try again')
            return redirect('login')

    return render(request,'login.html')


def logout_user(request):
    if request.method== 'POST':
        logout(request)
        messages.success(request,'Successfully Logged out')
        return redirect('Home')

def contact(request):
    if request.method=='POST':
        name = request.POST.get('name', 'default')
        email = request.POST.get('email', 'default')
        number = request.POST.get('phone', 'default')  
        message = request.POST.get('message', 'default')
        
        if len(name)<3 or name.isnumeric():
            messages.error(request,"Name should be string with more than 2 character")
        elif len(number)!=10:
            messages.error(request,"Number must contain 10 digits")
        elif len(message)<10:
            messages.error(request,"Message must contain at least 25 characters")
        elif len(email)<5:
            messages.error(request,"Email must contain at least 5 character")
        else:
            contact=Contact(name=name,email=email,number=number,message=message)
            contact.save()
            messages.success(request,"your message has been sent successfuly")
            
    return render(request,'contact.html')
