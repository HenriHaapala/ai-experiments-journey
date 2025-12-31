from django.urls import path
from .views import (
    RoadmapSectionListView,
    PublicLearningEntryListView,
    AIChatView,
    RoadmapProgressView,
    RAGSearchView,
    LearningEntryListCreateView,
)
from .views_security import LogSecurityEventView

urlpatterns = [
    path("roadmap/sections/", RoadmapSectionListView.as_view(), name="roadmap-sections"),
    path("roadmap/progress/", RoadmapProgressView.as_view(), name="roadmap-progress"),
    path("roadmap/learning-entries/", LearningEntryListCreateView.as_view(), name="learning-entries"),
    path(
        "learning/public/",
        PublicLearningEntryListView.as_view(),
        name="public-learning-entries",
    ),
    path("ai/chat/", AIChatView.as_view(), name="ai-chat"),
    path("rag/search/", RAGSearchView.as_view(), name="rag-search"),
    path("security/audit/", LogSecurityEventView.as_view(), name="security-audit-log"),
]
