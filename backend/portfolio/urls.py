from django.urls import path
from .views import (
    RoadmapSectionListView,
    PublicLearningEntryListView,
    AIChatView,
)

urlpatterns = [
    path("roadmap/sections/", RoadmapSectionListView.as_view(), name="roadmap-sections"),
    path(
        "learning/public/",
        PublicLearningEntryListView.as_view(),
        name="public-learning-entries",
    ),
    path("ai/chat/", AIChatView.as_view(), name="ai-chat"),
]
