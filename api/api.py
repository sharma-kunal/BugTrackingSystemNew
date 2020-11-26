from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, ProjectSerializer, TicketSerializer
from django.contrib.auth.models import User
from .models import Company, Projects, Tickets
from rest_framework.exceptions import APIException, PermissionDenied, NotFound
from django.db.utils import IntegrityError
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from uuid import uuid4
from collections import defaultdict


# api/signup/client
class SignUpClient(APIView):
    def post(self, request):
        request.POST._mutable = True
        request.data['username'] = 'client ' + uuid4().hex[:30]
        request.POST._mutable = False

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# api/signup/company
class SignUpCompany(APIView):
    def post(self, request):

        request.POST._mutable = True
        request.data['username'] = 'company ' + uuid4().hex[:30]
        try:
            company_name = request.POST['company_name']
        except KeyError:
            return Response({"company_name": ["This Field is Required"]}, status=status.HTTP_400_BAD_REQUEST)
        del request.POST['company_name']
        request.POST._mutable = False

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=request.data['username'])

            # Add this company and this user to Company table
            try:
                Company.objects.create(name=company_name, user_id=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"msg": "Company by that name is already registered"},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# api/login
class Login(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email', None)
        password = data.get('password', None)
        if email is None or password is None:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            if user.check_password(raw_password=password):
                try:
                    Token.objects.get(user=user)
                except Token.DoesNotExist:
                    # means was logged out
                    # so create Token
                    Token.objects.create(user=user)
                return Response({
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': email
                }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"msg": "Wrong Password"}, status=status.HTTP_403_FORBIDDEN)


# api/logout
class LogOut(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request.user.auth_token.delete()
        return Response({}, status=status.HTTP_200_OK)


# api/user/project
class UserProject(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # If user is employee

        # 1. get the company details using request.user (employee)
        # 2. get the client_id from header, to find all project of this client
        if user.username.split()[0] == 'company':
            client_id = self.request.query_params.get('client_id', None)
            if client_id is None:
                return Response({"msg": "Please provide client details"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                company_table = Company.objects.get(user_id=user)
                client = User.objects.get(id=client_id)

                # find projects for user and company name

                # also return no of tickets in each project

                projects = Projects.objects.filter(company_id=company_table, user_id=client)
            except Company.DoesNotExist:
                return Response({"msg": "Company Does Not Exist"}, status=status.HTTP_204_NO_CONTENT)
            except User.DoesNotExist:
                return Response({"msg": "Client does not exist"}, status=status.HTTP_204_NO_CONTENT)

        else:
            try:
                projects = Projects.objects.filter(user_id=user.id)
            except Projects.DoesNotExist:
                return Response({"msg": "Projects Does not Exist"}, status=status.HTTP_204_NO_CONTENT)

            # Problem is, these projects does not contain company name, but contain company ID to which they are linked to
            # So we will just create a list of data, at each index project details + company name

        response = []
        for project in projects:
            response.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'company_name': project.company_id.name,
                'tickets': len(Tickets.objects.filter(project_id=project))
            })
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        user = request.user
        if user.username.split()[0] == 'company':
            return Response({"msg": "Company is not allowed to open a project"}, status=status.HTTP_400_BAD_REQUEST)
        name = data.get('name', None)
        description = data.get('description', None)
        company_name = data.get('company_name', None)

        if None in (name, description, company_name):
            return Response({"msg": "Name, Description and Company Name all are required fields"},
                            status=status.HTTP_400_BAD_REQUEST)

        # find company with that company name

        try:
            company = Company.objects.get(name=company_name)
        except Company.DoesNotExist:
            return Response({"msg": "Company Does Not Exist"}, status=status.HTTP_204_NO_CONTENT)

        Projects.objects.create(name=name, description=description, company_id=company,
                                user_id=user)
        return Response({
            "name": name,
            "description": description,
            "company_name": company.name
        }, status=status.HTTP_201_CREATED)


# api/user/project/<project_id>/
class UserProjectID(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        user = request.user

        if user.username.split()[0] == 'company':
            return Response("Company not yet coded", status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Projects.objects.get(id=project_id)
            return Response({
                'id': project_id,
                'name': project.name,
                'description': project.description,
                'company': project.company_id.name
            }, status=status.HTTP_200_OK)
        except Projects.DoesNotExist:
            return Response({"msg": "No Such Project Exist"}, status=status.HTTP_204_NO_CONTENT)


# api/user/project/<project_id>/ticket
class UserTicket(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        user = request.user

        try:
            # find the project
            project = Projects.objects.get(id=project_id)

            # find all tickets in that project
            tickets = Tickets.objects.filter(project_id=project)
            serializer = TicketSerializer(tickets, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Projects.DoesNotExist:
            return Response({"msg": "Project Does Not Exist"}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request, project_id):
        user = request.user
        data = request.data

        try:
            project = Projects.objects.get(id=project_id)
        except Projects.DoesNotExist:
            return Response({"msg": "Project Does Not Exist"}, status=status.HTTP_204_NO_CONTENT)

        title = data.get('title', None)
        description = data.get('description', None)
        priority = {v: k for k, v in Tickets.PRIORITY_CHOICES}.get(data.get('priority', None))
        status_ = {v: k for k, v in Tickets.STATUS_CHOICES}.get(data.get('status', None))
        type = {v: k for k, v in Tickets.TICKET_TYPE_CHOICES}.get(data.get('type', None))

        if None in (title, description, priority, status_, type):
            return Response({"msg": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        ticket = Tickets.objects.create(
            title=title,
            description=description,
            priority=priority,
            status=status_,
            type=type,
            project_id=project
        )
        return Response({
            'id': ticket.id,
            'title': title,
            'description': description,
            'priority': priority,
            'status': status_,
            'type': type
        }, status=status.HTTP_201_CREATED)


# api/user/project/<project_id>/ticket/<ticket_id>
class UserTicketID(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, ticket_id):
        user = request.user

        try:
            Projects.objects.get(id=project_id)

            ticket = Tickets.objects.get(id=ticket_id)
            serializer = TicketSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Projects.DoesNotExist:
            return Response({"msg": "Project Does Not Exist"}, status=status.HTTP_204_NO_CONTENT)
        except Tickets.DoesNotExist:
            return Response({"msg": "Ticket Does Not Exist"}, status=status.HTTP_204_NO_CONTENT)


# api/company/dashboard
class CompanyUserProject(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # we will find all the clients linked to this company and no of their projects under this company

        user = request.user

        try:
            company = Company.objects.get(user_id=user.id)

            projects = Projects.objects.filter(company_id=company.id)
            response = defaultdict(int)
            for project in projects:
                response[str(project.user_id.id) + '-' + project.user_id.first_name + '-' + project.user_id.last_name] += 1
            return Response(response, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response({"msg": "No Such Employee Exists. Please Register your company first"},
                            status=status.HTTP_400_BAD_REQUEST)
        except Projects.DoesNotExist:
            return Response({"msg": "No Clients Exist"}, status=status.HTTP_204_NO_CONTENT)


# api/company
class CompanyList(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        companies = Company.objects.all()
        response = [company.name for company in companies]
        return Response(response, status=status.HTTP_200_OK)


# api/dashboard/projectWiseBugs
class ProjectWiseBugsDashboard(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:

            # find projects of the user
            user_projects = Projects.objects.filter(user_id=user)

            # now find tickets corresponding to each project
            tickets = dict()
            for project in user_projects:
                tickets[project.name] = len(Tickets.objects.filter(project_id=project))
            return Response(tickets, status=status.HTTP_200_OK)
        except Projects.DoesNotExist:
            return Response({"msg": "No Project exists for the user"}, status=status.HTTP_204_NO_CONTENT)


# api/dashboard/companyWiseProjects
class CompanyWiseProjectsDashboard(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        companies = Projects.objects.filter(user_id=user)

        response = defaultdict(int)
        for company in companies:
            response[company.company_id.name] += 1
        return Response(response, status=status.HTTP_200_OK)


# api/dashboard/bugsByType
class BugsByTypeDashboard(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # first find project of this user

        projects = Projects.objects.filter(user_id=user)

        # now find the bugs for these projects and classify them into three types
        # Feature/Request, Bug/Error, Others

        response = {
            'Feature/Request': 0,
            'Bug/Error': 0,
            'Others': 0
        }
        for project in projects:
            tickets = Tickets.objects.filter(project_id=project)
            for ticket in tickets:
                if ticket.type == "Feature/Request":
                    response['Feature/Request'] += 1
                elif ticket.type == "Bug/Error":
                    response['Bug/Error'] += 1
                else:
                    response['Others'] += 1
        return Response(response, status=status.HTTP_200_OK)


# api/dashboard/bugsByStatus
class BugsByStatus(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # first find project of this user

        projects = Projects.objects.filter(user_id=user)

        # now find the bugs for these projects and classify them into three types
        # Feature/Request, Bug/Error, Others

        response = {
            'Open': 0,
            'Closed': 0
        }
        for project in projects:
            tickets = Tickets.objects.filter(project_id=project)
            for ticket in tickets:
                if ticket.status == "Open":
                    response['Open'] += 1
                else:
                    response['Closed'] += 1
        return Response(response, status=status.HTTP_200_OK)
