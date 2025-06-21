from django.shortcuts import render
from rest_framework import generics
from rest_framework import viewsets, permissions ,status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from .serializers import *
from .models import *
from rest_framework.response import Response
# Create your views here.

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    # permission_classes = [permissions.IsAuthenticated]  # Adjust as needed
    view_permissions = {
        'list': {
            'user': True,
            'anon': NotAuthenticated,
        },
        'retrieve,update,create,destroy': {
            'education_department': True,
            'it_faculty': True,
        } 
    }

    def list(self, request):
        queryset = Document.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        try:
            document = self.queryset.get(pk=pk)
            serializer = self.serializer_class(document, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)

    def destroy(self, request, pk=None):
        try:
            document = self.queryset.get(pk=pk)
            document.delete()
            return Response(status=204)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)


