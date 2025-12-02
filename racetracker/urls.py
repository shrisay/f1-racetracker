from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),

    path('create/<str:context>', views.create, name="create"),

    path("season/<int:season_id>/addracers", views.add_racers_to_season, name="add_racers"),
    path("season/<int:season_id>/addconstructors", views.add_constructors_to_season, name="add_constructors"),
    path("race/<int:race_id>/setparticipants", views.set_participants, name="set_participants"),

    path('view/season/<int:season_id>', views.season_details, name="view_season"),
    path('view/race/<int:race_id>', views.race_details, name="view_race"),

    path('season/<int:season_id>/delete', views.delete_season, name='delete_season'),
    path('race/<int:race_id>/delete', views.delete_race, name='delete_race'),

    path('save/qualifying/<int:race_id>', views.save_qualifying_results, name="save_quali"),
    path('save/race/<int:race_id>', views.save_race_results, name="save_race"),

    path('api/race/<int:race_id>/rename/', views.rename_race, name="rename_race"),
    path("api/season/<int:season_id>/reopen/", views.reopen_season, name="reopen_season"),
    path('api/season/<int:season_id>/close/', views.close_season, name="close_season"),
    path('api/season/<int:season_id>/add/', views.add_race, name='add_race'),
    
    path('login', views.login_view, name="login"),
    path('logout', views.logout_view, name="logout"),
    path('register', views.register, name="register")
]