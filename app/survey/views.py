"""
Views for the survey API.
"""
from rest_framework import generics, permissions
from core.models import Survey
from survey.serializers import SurveySerializer
from survey.permissions import IsOwnerOrReadOnly, IsResearcher


class SurveyListCreateView(generics.ListCreateAPIView):
    serializer_class = SurveySerializer

    def get_queryset(self):
        return Survey.objects.all().order_by('-created_at')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsResearcher()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SurveyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating, or deleting a survey."""
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsOwnerOrReadOnly]
