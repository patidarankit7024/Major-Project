# -*- coding: utf-8 -*-

from . import views
from django.urls import path
from . import plot

urlpatterns = [
    
        path('',views.index,name="Home"),
        path('about/',views.AboutUs,name="about"),
        path('contact/',views.contact,name="contact"),
        path('signup/',views.SignUp,name="signup"),
        path('login/',views.login_user,name="login"),
        path('logout/',views.logout_user,name="logout"),
        path('plot/',plot.show,name="show"),
        path('countplot/',plot.countplot,name="countplot"),
        path('insights/',plot.insights,name="insights"),
        path('correlationplot/',plot.correlationplot,name="correlationplot"),
        
		path('histogramplot/',plot.allhistogramplot,name="allhistogramplot"),
		path('barplot/',plot.allbarplot,name="allbarplot"),
		path('boxplot/',plot.allboxplot,name="allboxplot"),
		path('piechart/',plot.allpiechart,name="allpiechart"),
		path('scatterplot/',plot.allscatterplot,name="allscatterplot"),
		path('lineplot/',plot.alllineplot,name="alllineplot"),
        path('report/',plot.report,name="report"),
    ]