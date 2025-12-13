from django.urls import path

from .github_webhook import GitHubWebhookView

urlpatterns = [
    path("github-webhook/", GitHubWebhookView.as_view(), name="github-webhook"),
]
