from django.urls import path
from django.conf.urls import url
from rest_framework.authtoken.views import obtain_auth_token
from .api import SignUpClient, SignUpCompany, Login, UserProject, UserProjectID, UserTicket, UserTicketID, \
    CompanyUserProject, CompanyList

urlpatterns = [
    path('api/signup/client', SignUpClient.as_view()),
    path('api/signup/company', SignUpCompany.as_view()),
    path('api/login', Login.as_view()),
    path('api/auth', obtain_auth_token),
    path('api/user/project', UserProject.as_view()),
    url(r'^api/user/project/(?P<project_id>\d+)/$', UserProjectID.as_view()),
    url(r'^api/user/project/(?P<project_id>\d+)/ticket$', UserTicket.as_view()),
    url(r'^api/user/project/(?P<project_id>\d+)/ticket/(?P<ticket_id>\d+)/$', UserTicketID.as_view()),

    path('api/company/dashboard', CompanyUserProject.as_view()),

    path('api/company', CompanyList.as_view())
]