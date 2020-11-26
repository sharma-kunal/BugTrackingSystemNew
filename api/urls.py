from django.urls import path
from django.conf.urls import url
from rest_framework.authtoken.views import obtain_auth_token
from .api import SignUpClient, SignUpCompany, Login, UserProject, UserProjectID, UserTicket, UserTicketID, \
    CompanyUserProject, CompanyList, ProjectWiseBugsDashboard, CompanyWiseProjectsDashboard, BugsByTypeDashboard, \
    BugsByStatus

urlpatterns = [

    # client calls
    path('api/signup/client', SignUpClient.as_view()),
    path('api/signup/company', SignUpCompany.as_view()),
    path('api/login', Login.as_view()),
    path('api/auth', obtain_auth_token),
    path('api/user/project', UserProject.as_view()),
    url(r'^api/user/project/(?P<project_id>\d+)/$', UserProjectID.as_view()),
    url(r'^api/user/project/(?P<project_id>\d+)/ticket$', UserTicket.as_view()),
    url(r'^api/user/project/(?P<project_id>\d+)/ticket/(?P<ticket_id>\d+)/$', UserTicketID.as_view()),

    # employee calls
    path('api/company/dashboard', CompanyUserProject.as_view()),

    # list of all companies
    path('api/company', CompanyList.as_view()),

    # client dashboard calls
    path('api/dashboard/projectWiseBugs', ProjectWiseBugsDashboard.as_view()),
    path('api/dashboard/companyWiseProjects', CompanyWiseProjectsDashboard.as_view()),
    path('api/dashboard/bugsByType', BugsByTypeDashboard.as_view()),
    path('api/dashboard/bugsByStatus', BugsByStatus.as_view())
]