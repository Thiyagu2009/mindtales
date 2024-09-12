from django.urls import path

from employee.views.signup_views import EmployeeSignUpView
from employee.views.voting_views import SubmitVoteView, VoteResultsView


urlpatterns = [
    path("signup/", EmployeeSignUpView.as_view(), name="employee-signup"),
    path("vote/", SubmitVoteView.as_view(), name="submit-vote"),
    path("vote/results/", VoteResultsView.as_view(), name="vote-results"),
]
