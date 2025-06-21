from datetime import date
from django.shortcuts import render
from django.db.models import Q, Count
from django.contrib.auth.models import Group
from rest_framework import viewsets, permissions ,status
from .serializers import *
from .models import *
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_roles.granting import is_self
from app.roles import *
from .permissions import *

# Create your views here.

class LecturerStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecturer
        fields = ['status']


class LecturerViewSet(viewsets.ModelViewSet):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    # permission_classes = [permissions.IsAuthenticated]
    view_permissions = {
        'me': {
            'user': True,
        },
        'list': {
            'lecturer': True,
            'potential_lecturer': True,
            'it_faculty': True,
            'education_department': True,
            'supervision_department': True,
        },
        'retrieve,all': {
            'education_department': True,
            'it_faculty': True,
            'supervision_department': True
        },
        'create,update,destroy': {
          'education_department': True  
        },
        'potential_lecturers': {
            'it_faculty': True,
            'education_department': True,
        },
        'partial_update,update_status': {
            
            'education_department': True,
            'it_faculty': True,
        },
        'sign_contract,count_pending_lecturers': {
            'education_department': True,
        },
        'degree_count': {
            'anon': True,
            'user': True,
        },
        'title_count': {
            'anon': True,
            'user': True,
        },
        'count_all_lecturers': {
            'user': True
        },
        'count_potential_lecturers': {
            'user': True
        }
    }
    def list(self, request):
        lecturer_group = Group.objects.filter(name='lecturer').first()
        queryset = Lecturer.objects.filter(
            Q(user__groups=lecturer_group) |
            Q(status="Đã ký hợp đồng")
        )
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def count_all_lecturers(self, request):
        lecturer_group = Group.objects.filter(name='lecturer').first()
        queryset = Lecturer.objects.filter(
            Q(user__groups=lecturer_group) |
            Q(status="Đã ký hợp đồng")
        )
        total = queryset.count()
        return Response(total)
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        queryset = Lecturer.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def potential_lecturers(self, request):
        potential_group = Group.objects.filter(name='potential_lecturer').first()
        queryset = Lecturer.objects.filter(
            Q(status="Chưa duyệt hồ sơ") |
            Q(user__groups=potential_group)
        ).distinct()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def count_potential_lecturers(self, request):
        potential_group = Group.objects.filter(name='potential_lecturer').first()
        queryset = Lecturer.objects.filter(
            Q(status="Chưa duyệt hồ sơ") |
            Q(user__groups=potential_group)
        ).distinct()
        count = queryset.count()
        return Response(count)
    
    @action(detail=False, methods=["get"])
    def count_pending_lecturers(self, request):
        potential_group = Group.objects.filter(name='potential_lecturer').first()
        queryset = Lecturer.objects.filter(
            Q(status="Hồ sơ hợp lệ") |
            Q(user__groups=potential_group)
        ).distinct()
        count = queryset.count()
        return Response(count)
    
    @action(detail=False, methods=['get'])
    def degree_count(self, request):
        # Total number of lecturers
        lecturer_group = Group.objects.filter(name='lecturer').first()
        queryset = Lecturer.objects.filter(
            Q(user__groups=lecturer_group) |
            Q(status="Đã ký hợp đồng") 
        )
        total = queryset.count()
        # Group by degree and count lecturers
        data = (
            queryset.values('degree')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        # Calculate percentage for each degree
        result = [
            {
                "degree": item["degree"],
                "percentage": round(item["count"] / total * 100, 2) if total > 0 else 0
            }
            for item in data
        ]
        # Response format: [{"degree": "PhD", "percentage": 40.0}, ...]
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def title_count(self, request):
        # Total number of lecturers
        lecturer_group = Group.objects.filter(name='lecturer').first()
        queryset = Lecturer.objects.filter(
            Q(user__groups=lecturer_group) |
            Q(status="Đã ký hợp đồng") 
        )
        total = queryset.count()
        # Group by title and count lecturers
        data = (
            queryset.values('title')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        # Calculate percentage for each title
        result = [
            {
                "title": item["title"] if item["title"] != "" else "None",
                "percentage": round(item["count"] / total * 100, 2) if total > 0 else 0,
            }
            for item in data
        ]
        # Response format: [{"title": "Professor", "percentage": 40.0}, ...]
        return Response(result)
        

    def retrieve(self, request, pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        try:
            lecturer = self.queryset.get(pk=pk)
            serializer = self.serializer_class(lecturer, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)
        
    @action(detail=True, methods=['post'])
    def sign_contract(self, request, pk=None):
        """
        Set lecturer status to 'Đã ký hợp đồng' and add user to 'lecturer' group.
        """
        try:
            lecturer = self.get_queryset().get(pk=pk)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)

        # Set status
        lecturer.status = "Đã ký hợp đồng"
        lecturer.save()

        # Add user to 'lecturer' group if not already
        if lecturer.user:
            lecturer_group, _ = Group.objects.get_or_create(name='lecturer')
            if not lecturer.user.groups.filter(name='lecturer').exists():
                lecturer.user.groups.set([lecturer_group])
                lecturer.user.save()

        serializer = self.get_serializer(lecturer)
        return Response(serializer.data)
    
    def partial_update(self, request, pk=None):
        try:
            lecturer = self.queryset.get(pk=pk)
            serializer = LecturerStatusSerializer(lecturer, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)
    
    def destroy(self, request, pk=None):
        try:
            lecturer = self.queryset.get(pk=pk)
            lecturer.delete()
            return Response(status=204)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)
        
    @action(detail=False, methods=['get', 'put', 'patch', 'post'])
    def me(self, request):
        try:
            lecturer = Lecturer.objects.get(user=request.user)
        except Lecturer.DoesNotExist:
            # User has not been assigned to any user -> Create a new lecturer for the user
            data = request.data.copy()
            data['user'] = request.user.id
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(lecturer, data=request.data, partial=(request.method == 'PATCH'))
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        else:
            serializer = self.get_serializer(lecturer)
            return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, CanEditLecturerStatus])
    def update_status(self, request, pk=None):
        try:
            lecturer = Lecturer.objects.get(pk=pk)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)
        serializer = LecturerStatusSerializer(lecturer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    # permission_classes = [permissions.AllowAny]
    view_permissions = {
        'list': {
            'lecturer': True,
            'potential_lecturer': True,
            'it_faculty': True,
            'education_department': True,
            'supervision_department': True,
            
        },
        'retrieve,update,create,destroy': {
            'education_department': True,
        },
        'lecturer_count': {
            'user': True,
        }
    }

    def list(self, request):
        queryset = Subject.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='lecturer_count')
    def lecturer_count(self, request):
        lecturer_group = Group.objects.filter(name='lecturer').first()
        # Filter lecturers in the 'lecturer' group
        lecturer_queryset = Lecturer.objects.filter(
            Q(user__groups=lecturer_group) |
            Q(status="Đã ký hợp đồng")
        )
        # Annotate each subject with the count of lecturers in the filtered queryset
        subjects = Subject.objects.annotate(
            lecturer_count=Count(
                'lecturer',
                filter=Q(lecturer__in=lecturer_queryset)
            )
        ).values('name', 'lecturer_count')
        return Response(list(subjects))
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def retrieve(self, request, pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except Subject.DoesNotExist:
            return Response({"error": "Subject not found"}, status=404)
    
    def update(self, request, pk=None):
        try:
            subject = self.queryset.get(pk=pk)
        except Subject.DoesNotExist:
            return Response({"error": "Subject not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(subject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # Log lỗi nếu có
        print("Update failed:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        try:
            subject = self.queryset.get(pk=pk)
            subject.delete()
            return Response(status=204)
        except Subject.DoesNotExist:
            return Response({"error": "Subject not found"}, status=404)


class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    # permission_classes = [permissions.AllowAny]
    view_permissions = {
        'get_by_lecturer': {
            'it_faculty': True,
            'supervision_department': True,
        },
        'retrieve,update,create,destroy': {
            'supervision_department': True,
            'it_faculty': True,
        },
        'me': {
            'user': True
        }
    }

    def list(self, request):
        queryset = Evaluation.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def retrieve(self, request, pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except Evaluation.DoesNotExist:
            return Response({"error": "Evaluation not found"}, status=404)
    
    def update(self, request, pk=None):
        try:
            evaluation = self.queryset.get(pk=pk)
        except Evaluation.DoesNotExist:
            return Response({"error": "Evaluation not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(evaluation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # Log lỗi nếu có
        print("Update failed:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        try:
            lecturer = Lecturer.objects.get(user=request.user)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)
        evaluations = self.queryset.all()
        serializer = self.serializer_class(evaluations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path="by-lecturer/(?P<lecturer_id>[^/.]+)")
    def get_by_lecturer(self, request, lecturer_id=None):
        """
        Custom action to retrieve all lecturers for a given lecturer ID.
        """
        try:
            schedules = self.queryset.filter(lecturer_id=lecturer_id)
            serializer = self.serializer_class(schedules, many=True)
            print(request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Schedule.DoesNotExist:
            return Response(
                {"error": "Schedule not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
    
   
class ScheduleViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.AllowAny]
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    view_permissions = {
        'get_schedules_by_lecturer' :{
            'lecturer': True,
            'education_department': True,
            'supervision_department': True,
            'it_faculty': True,
        },
        'me': {
            'user': True,
        },
        'create,update,destroy,partial_update': {
            'education_department': True,
        },
        'today': {
            'anon': True,
            'user': True,
        }
    }
    
    def list(self, request):
        queryset = Schedule.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except Schedule.DoesNotExist:
            return Response({"error": "Schedule not found"}, status=404)
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        print(serializer.errors)
        return Response(serializer.errors, status=400)
    
    def update(self, request, pk=None, partial=False):
        try:
            subject = self.queryset.get(pk=pk)
        except Schedule.DoesNotExist:
            return Response({"error": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(subject, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # Log lỗi nếu có
        print("Update failed:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        try:
            subject = self.queryset.get(pk=pk)
            subject.delete()
            return Response(status=204)
        except Schedule.DoesNotExist:
            return Response({"error": "Subject not found"}, status=404)
    
    
    @action(detail=False, methods=["get"], url_path="by-lecturer/(?P<lecturer_id>[^/.]+)")
    def get_schedules_by_lecturer(self, request, lecturer_id=None):
        try:
            schedules = self.queryset.filter(lecturer_id=lecturer_id)
            serializer = self.serializer_class(schedules, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Lecturer.DoesNotExist:
            return Response(
                {"error": "Lecturer not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
    
    @action(detail=False, methods=['get'], url_path='today')
    def today(self, request):
        today = date.today()
        schedules = self.queryset.filter(start_time__date=today)
        # Prefetch lecturer to avoid N+1 queries
        schedules = schedules.select_related('lecturer')
        result = []
        for schedule in schedules:
            data = self.serializer_class(schedule).data
            # Attach lecturer name
            data['lecturer_name'] = schedule.lecturer.name if schedule.lecturer else None
            result.append(data)
        return Response(result)
    
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        try:
            lecturer = Lecturer.objects.get(user=request.user)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)
        schedules = self.queryset.filter(lecturer=lecturer)
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
    

class LecturerRecommendationViewSet(viewsets.ModelViewSet):
    queryset = LecturerRecommendation.objects.all()
    serializer_class = LecturerRecommendationSerializer
    view_permissions = {
        'list': {
            'it_faculty': True
        },
        'retrieve,update': {
            'lecturer': True,
            'it_faculty': True
        },
        'create,destroy,me': {
            'lecturer': True
        },
        'count_unchecked': {
            'it_faculty': True
        }
    }

    def list(self, request):
        queryset = self.queryset.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def count_unchecked(self, request):
        queryset = self.queryset.filter(
            status="Chưa được duyệt"
        )
        count = queryset.count()
        return Response(count)
    
    def retrieve(self, request, pk=None):
        print("Retrieve called with pk:", pk)
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except LecturerRecommendation.DoesNotExist:
            return Response({"error": "Recommendation not found"}, status=404)
    
    
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def update(self, request, pk=None):
        try:
            recommendation = self.queryset.get(pk=pk)
        except LecturerRecommendation.DoesNotExist:
            return Response({"error": "Recommendation not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(recommendation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # Log lỗi nếu có
        print("Update failed:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        try:
            recommendation = self.queryset.get(pk=pk)
            recommendation.delete()
            return Response(status=204)
        except LecturerRecommendation.DoesNotExist:
            return Response({"error": "Recommendation not found"}, status=404)
    
    @action(detail=False, methods=['get', 'post', 'put', 'patch', 'delete'])
    def me(self, request):
        try:
            lecturer = Lecturer.objects.get(user=request.user)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)

        # GET: List all recommendations by this lecturer
        if request.method == 'GET':
            recommendations = LecturerRecommendation.objects.filter(recommender=lecturer)
            serializer = self.get_serializer(recommendations, many=True)
            return Response(serializer.data)

        # POST: Create a new recommendation for this lecturer
        if request.method == 'POST':
            data = request.data.copy()
            data['recommender'] = lecturer.id
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

        # PUT/PATCH: Update a recommendation by id (must belong to this lecturer)
        if request.method in ['PUT', 'PATCH']:
            rec_id = request.data.get('id')
            if not rec_id:
                return Response({"error": "Recommendation id required"}, status=400)
            try:
                recommendation = LecturerRecommendation.objects.get(id=rec_id, recommender=lecturer)
            except LecturerRecommendation.DoesNotExist:
                return Response({"error": "Recommendation not found"}, status=404)
            serializer = self.get_serializer(recommendation, data=request.data, partial=(request.method == 'PATCH'))
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

        # DELETE: Delete a recommendation by id (must belong to this lecturer)
        if request.method == 'DELETE':
            rec_id = request.data.get('id')
            if not rec_id:
                return Response({"error": "Recommendation id required"}, status=400)
            try:
                recommendation = LecturerRecommendation.objects.get(id=rec_id, recommender=lecturer)
            except LecturerRecommendation.DoesNotExist:
                return Response({"error": "Recommendation not found"}, status=404)
            recommendation.delete()
            return Response(status=204)
    
