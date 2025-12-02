import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.urls import reverse

from .models import *

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    racers = Racer.get_sorted(request.user)
    seasons = Season.objects.filter(user=request.user)
    constructors = Constructor.get_sorted(request.user)

    return render(request, "racetracker/details.html", {
        "alltime": True,
        "seasons": seasons,
        "racers": racers,
        "constructors": constructors
    })

def season_details(request, season_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    try:
        season = Season.objects.get(pk=season_id)
    except Season.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))

    if request.user != season.user:
        return HttpResponseForbidden('You do not have permission to view this competition.')
    
    racers = SeasonRacer.get_sorted(season)
    constructors = SeasonConstructor.get_sorted(season)
    races = season.races.all()

    return render(request, "racetracker/details.html", {
        "alltime": False,             ### Defines whether the statistics are for all-time or the season only
        "season": season,
        "racers": racers,
        "constructors": constructors,
        "races": races,
        "can_close": RaceResult.objects.filter(race__season=season).exists()
    })

def create(request, context):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if context == "racer":
        if request.method == "POST":
            name = request.POST["name"]

            if Racer.objects.filter(name=name).exists():
                messages.error(request, f"Racer '{name}' already exists.")
                return render(request, "racetracker/create.html", {
                    "context": "racer",
                    "competition": False,
                    "name": name
                })

            Racer.objects.create(name=name, user=request.user)
            messages.success(request, f"Racer '{name}' created successfully!")
            return HttpResponseRedirect(reverse("create", kwargs = {
                "context": "racer"
            }))
        
        return render(request, "racetracker/create.html", {
            "context": "racer",
            "competition": False
        })


    elif context == "constructor":
        if request.method == "POST":
            name = request.POST["name"]    

            if Constructor.objects.filter(name=name).exists():
                messages.error(request, f"Constructor '{name}' already exists.")
                return render(request, "racetracker/create.html", {
                    "context": "constructor",
                    "competition": False,
                    "name": name
                })
            
            Constructor.objects.create(name=name, user=request.user)
            messages.success(request, f"Constructor '{name}' created successfully!")
            return HttpResponseRedirect(reverse("create", kwargs = {
                "context": "constructor"
            }))
        
        return render(request, "racetracker/create.html", {
            "context": "constructor",
            "competition": False
        })

    elif context == "competition":
        if request.method == "POST":
            name = request.POST["name"]
            season = Season.objects.create(name=name, user=request.user)

            messages.success(request, f"Competition '{name}' created successfully!")
            return HttpResponseRedirect(reverse("add_constructors", kwargs = {
                "season_id": season.id
            }))
        return render(request, "racetracker/create.html", {
            "context": "competition",
            "competition": True
        })
    
def add_constructors_to_season(request, season_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    
    try:
        season = Season.objects.get(pk=season_id, user=request.user)
    except Season.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))
    
    if season.is_closed:
        messages.error(request, "This season is closed. You cannot modify constructors or racers.")
        return HttpResponseRedirect(reverse('view_season', kwargs={"season_id": season.id}))

    if request.method == "POST":
        selected_constructor_ids = request.POST.getlist('constructors')
        for cons_id in selected_constructor_ids:
            constructor = Constructor.objects.get(pk=cons_id)
            SeasonConstructor.objects.get_or_create(constructor=constructor, season=season)

        return HttpResponseRedirect(reverse('add_racers', kwargs = {
            "season_id": season.id
        }))

    available_constructors = Constructor.objects.filter(user=request.user).exclude(season_constructor__season=season)

    return render(request, "racetracker/add_constructors.html", {
        "season": season,
        "constructors": available_constructors
    })

def add_racers_to_season(request, season_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    
    try:
        season = Season.objects.get(pk=season_id, user=request.user)
    except Season.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))
    
    if season.is_closed:
        messages.error(request, "This season is closed. You cannot modify constructors or racers.")
        return HttpResponseRedirect(reverse('view_season', kwargs={"season_id": season.id}))

    if request.method == "POST":
        selected_racers = request.POST.getlist('racers')

        for racer_id in selected_racers:
            racer = Racer.objects.get(pk=racer_id)
            constructor_id = request.POST.get(f'constructor_for_{racer_id}')
            
            if constructor_id:
                constructor = Constructor.objects.get(pk=constructor_id)
                SeasonRacer.objects.get_or_create(racer=racer, constructor=constructor, season=season)
            else:
                SeasonRacer.objects.get_or_create(racer=racer, season=season)
 
        return HttpResponseRedirect(reverse('view_season', kwargs = {
                "season_id": season.id
            }))

    available_racers = Racer.objects.filter(user=request.user).exclude(season_racer__season=season)
    available_constructors = Constructor.objects.filter(season_constructor__season=season)

    return render(request, "racetracker/add_racers.html", {
        "season": season,
        "racers": available_racers,
        "constructors": available_constructors
    })

def race_details(request, race_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    
    try:
        race = Race.objects.get(pk=race_id)
    except Race.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))
    
    if request.user != race.season.user:
        return HttpResponseForbidden('You do not have permission to view this race.')

    return render(request, "racetracker/race_results.html", {
        "race": race,
        "qualifying_results": race.qualifying.all(),
        "race_results": race.results.all()
    })

def set_participants(request, race_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    
    try:
        race = Race.objects.get(pk=race_id)
    except Race.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))
    max_racers = SeasonRacer.objects.filter(season=race.season).count()

    next_url = request.GET.get("next")
    if request.method == "POST":
        num = request.POST.get("num_participants")
        if num and num.isdigit() and 1 <= int(num) <= max_racers:
            race.participants = int(num)
            race.save()

            # Redirect back to where user came from (quali or race)
            if next_url:
                return redirect(next_url)
            return HttpResponseRedirect(reverse('index'))
        messages.error(request, "Please enter a valid number.")

    return render(request, "racetracker/set_participants.html", {
        "race": race,
        "max_racers": max_racers,
        "next_url": next_url
    })

def save_qualifying_results(request, race_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    try:
        race = Race.objects.get(pk=race_id)
    except Race.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))
    
    season_racers = SeasonRacer.objects.filter(season=race.season)

    race_racer_ids = RaceResult.objects.filter(race=race).values_list("racer_id", flat=True)
    if race_racer_ids:
        season_racers = season_racers.filter(id__in=race_racer_ids)
    else:
        if race.participants is None:
            return redirect(f"{reverse('set_participants', kwargs={'race_id': race.id})}?next={request.path}")

    if not season_racers.exists():
        messages.error(request, "Add racers and constructors to the competition first!")
        return HttpResponseRedirect(reverse('add_constructors', kwargs = {
            "season_id": race.season.id
        }))
    
    if QualifyingResult.objects.filter(race=race).exists():
        return HttpResponseRedirect(reverse('view_race', kwargs = {
            "season_id": race.id
        }))

    if request.method == "POST":
        selected_racers = []
        qualifying_results = []

        for position in range(1, race.participants + 1):
            racer_id = request.POST[f"racer_{position}"]

            if racer_id == "":
                messages.error(request, "All positions must have a racer selected.")
                return render(request, "racetracker/qualifying_form.html", {
                    "race": race,
                    "season_racers": season_racers,
                    "positions": range(1, race.participants + 1)
                })
            
            if racer_id in selected_racers:
                messages.error(request, "Duplicate racers detected. Each racer must have a unique position.")
                return render(request, "racetracker/qualifying_form.html", {
                    "race": race,
                    "season_racers": season_racers,
                    "positions": range(1, race.participants + 1),
                })
            selected_racers.append(racer_id)

        for position in range(1, race.participants + 1):
            racer_id = request.POST[f"racer_{position}"]
            season_racer = SeasonRacer.objects.get(pk=racer_id)
            
            qualifying_results.append(QualifyingResult(
                race=race,
                racer=season_racer,
                position=position
            ))

            if position == 1:
                racer = season_racer.racer

                constructor = season_racer.constructor
                season_constructor = SeasonConstructor.objects.filter(constructor=constructor, season=race.season).first()
                if constructor:
                    constructor.poles += 1
                    constructor.save()
                    season_constructor.poles +=1
                    season_constructor.save()
                
                season_racer.poles += 1
                racer.poles += 1                    
                season_racer.save()
                racer.save()

        QualifyingResult.objects.filter(race=race).delete() 
        QualifyingResult.objects.bulk_create(qualifying_results)
        return HttpResponseRedirect(reverse('view_race', kwargs = { 
            "race_id": race.id
        }))

    return render(request, "racetracker/qualifying_form.html", {
        "race": race,
        "season_racers": season_racers,
        "positions": range(1, race.participants + 1),
    })

def save_race_results(request, race_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    try:
        race = Race.objects.get(pk=race_id)
    except Race.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))
    
    season_racers = SeasonRacer.objects.filter(season=race.season)

    qualifying_racer_ids = QualifyingResult.objects.filter(race=race).values_list("racer_id", flat=True)
    if qualifying_racer_ids:
        season_racers = season_racers.filter(id__in=qualifying_racer_ids)
    else:
        if race.participants is None:
            return redirect(f"{reverse('set_participants', kwargs={'race_id': race.id})}?next={request.path}")

    if not season_racers.exists():
        messages.error(request, "Add racers and constructors to the competition first!")
        return HttpResponseRedirect(reverse('add_constructors', kwargs = {
            "season_id": race.season.id
        }))
    
    if RaceResult.objects.filter(race=race).exists():
        return HttpResponseRedirect(reverse('view_race', kwargs = {
            "season_id": race.id
        }))

    if request.method == "POST":
        selected_racers = []
        race_results = []

        for position in range(1, race.participants + 1):
            racer_id = request.POST[f"racer_{position}"]

            if racer_id == "":
                messages.error(request, "All positions must have a racer selected.")
                return render(request, "racetracker/race_form.html", {
                    "race": race,
                    "season_racers": season_racers,
                    "positions": range(1, race.participants + 1)
                })
            
            if racer_id in selected_racers:
                messages.error(request, "Duplicate racers detected. Each racer must have a unique position.")
                return render(request, "racetracker/race_form.html", {
                    "race": race,
                    "season_racers": season_racers,
                    "positions": range(1, race.participants + 1)
                })
            
            selected_racers.append(racer_id)

        highest_dnf_position = None
        for position in range(1, race.participants + 1):
            racer_id = request.POST[f"racer_{position}"]
            dnf = f"dnf_{position}" in request.POST
            if dnf:
                if highest_dnf_position is None or position < highest_dnf_position:
                    highest_dnf_position = position

        if highest_dnf_position:
            for position in range(1, race.participants + 1):
                racer_id = request.POST[f"racer_{position}"]
                dnf = f"dnf_{position}" in request.POST
                if not dnf and position > highest_dnf_position:
                    season_racer = SeasonRacer.objects.get(pk=racer_id)
                    messages.error(request, f"{season_racer.racer.name} (Finished) cannot be placed behind a DNF racer.")
                    return render(request, "racetracker/race_form.html", {
                        "race": race,
                        "season_racers": season_racers,
                        "positions": range(1, race.participants + 1)
                    })
            
        points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
        for position in range(1, race.participants + 1):
            racer_id = request.POST[f"racer_{position}"]
            dnf = f"dnf_{position}" in request.POST
            season_racer = SeasonRacer.objects.get(pk=racer_id)

            if position <= 10 and not dnf:
                points_awarded = points[position-1]
            else:
                points_awarded = 0
            
            race_results.append(RaceResult(
                race=race,
                racer=season_racer,
                position=position,
                points_awarded=points_awarded,
                dnf=dnf
            ))

            racer = season_racer.racer
            constructor = season_racer.constructor
            season_constructor = SeasonConstructor.objects.filter(constructor=constructor, season=race.season).first()

            if position == 1:
                season_racer.wins += 1
                racer.wins += 1
                if constructor:
                    constructor.wins += 1
                    season_constructor.wins += 1
            if position <= 3:
                season_racer.podiums += 1
                racer.podiums += 1
                if constructor:
                    constructor.podiums += 1
                    season_constructor.podiums += 1
                
            racer.points += points_awarded
            racer.races += 1
            season_racer.points += points_awarded

            if constructor:
                constructor.points += points_awarded
                season_constructor.points += points_awarded
                constructor.save()
                season_constructor.save()
            racer.save()
            season_racer.save()

        RaceResult.objects.filter(race=race).delete() 
        RaceResult.objects.bulk_create(race_results)
        messages.success(request, "Race results saved successfully.")
        return HttpResponseRedirect(reverse('view_race', kwargs = { 
            "race_id": race.id
        }))
    return render(request, "racetracker/race_form.html", {
        "race": race,
        "season_racers": season_racers,
        "positions": range(1, race.participants + 1),
    })

def delete_season(request, season_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    try:
        season = Season.objects.get(pk=season_id)
    except Season.DoesNotExist:
        messages.error(request, "Season does not exist.")
        return HttpResponseRedirect(reverse('index'))

    races = Race.objects.filter(season=season)

    for race in races:
        if QualifyingResult.objects.filter(race=race).exists() or RaceResult.objects.filter(race=race).exists():
            messages.error(request, "Cannot delete season. It contains races with qualifying or race results.")
            return HttpResponseRedirect(reverse('view_season', kwargs={
                "season_id": season_id
            }))

    for race in races:
        pole = QualifyingResult.objects.filter(race=race, position=1).first()
        if pole:
            season_racer = pole.racer
            racer = season_racer.racer
            constructor = season_racer.constructor

            if constructor:
                season_constructor = SeasonConstructor.objects.filter(constructor=constructor, season=season).first()
                if season_constructor:
                    season_constructor.poles -= 1
                    season_constructor.save()
                constructor.poles -= 1
                constructor.save()

            season_racer.poles -= 1
            season_racer.save()
            racer.poles -= 1
            racer.save()

    season.delete()

    messages.success(request, "Competition deleted successfully.")
    return HttpResponseRedirect(reverse('index'))

def delete_race(request, race_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    try:
        race = Race.objects.get(pk=race_id)
    except Race.DoesNotExist:
        messages.error(request, "Race does not exist.")
        return HttpResponseRedirect(reverse('index'))
    
    if race.season.is_closed:
        messages.error(request, "Cannot delete race. The season is closed.")
        return HttpResponseRedirect(reverse('view_season', kwargs = {
            "season_id": race.season.id
        }))

    if RaceResult.objects.filter(race=race).exists():
        race_results = race.results.all()

        for result in race_results:
            season_racer = result.racer
            racer = season_racer.racer
            constructor = season_racer.constructor
            season_constructor = None

            if constructor:
                season_constructor = SeasonConstructor.objects.filter(constructor=constructor, season=race.season).first()

            racer.points -= result.points_awarded
            season_racer.points -= result.points_awarded

            if constructor:
                constructor.points -= result.points_awarded
                if season_constructor:
                    season_constructor.points -= result.points_awarded

            if result.position == 1:
                racer.wins -= 1
                season_racer.wins -= 1
                if constructor and season_constructor:
                    constructor.wins -= 1
                    season_constructor.wins -= 1

            if result.position <= 3:
                racer.podiums -= 1
                season_racer.podiums -= 1
                if constructor and season_constructor:
                    constructor.podiums -= 1
                    season_constructor.podiums -= 1

            racer.save()
            season_racer.save()
            if constructor:
                constructor.save()
                if season_constructor:
                    season_constructor.save()

        # ✅ Delete results and race after all rollbacks
        race_results.delete()

    # Handle pole rollback
    pole = QualifyingResult.objects.filter(race=race, position=1).first()
    if pole:
        season_racer = pole.racer
        racer = season_racer.racer
        constructor = season_racer.constructor
        if constructor:
            season_constructor = SeasonConstructor.objects.filter(constructor=constructor, season=race.season).first()
            constructor.poles -= 1
            constructor.save()
            if season_constructor:
                season_constructor.poles -= 1
                season_constructor.save()

        season_racer.poles -= 1
        racer.poles -= 1
        season_racer.save()
        racer.save()

    race_name = race.name
    season_id = race.season.id
    race.delete()

    # Update race count
    season = Season.objects.get(pk=season_id)
    season.race_number -= 1
    season.save()

    messages.success(request, f'Race "{race_name}" deleted successfully.')
    return HttpResponseRedirect(reverse('view_season', kwargs={
        "season_id": season_id
    }))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "racetracker/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "racetracker/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "racetracker/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "racetracker/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "racetracker/register.html")
    

######## API VIEWS ########
@csrf_exempt
def rename_race(request, race_id):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    try:
        data = json.loads(request.body)
        new_name = data.get("new_name", "").strip()
        
        race = Race.objects.get(pk=race_id)
        race.name = new_name
        race.save()

        return JsonResponse({"message": "Race name updated successfully.", "new_name": new_name}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
def close_season(request, season_id):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    
    try:
        season = Season.objects.get(pk=season_id)
    except Season.DoesNotExist:
        return JsonResponse({"success": False, "error": "Competition not found."}, status=404)

    incomplete_races = []
    for race in season.races.all():
        if not race.results.exists():
            incomplete_races.append(race)

    if incomplete_races:
        return JsonResponse({
            "error": f"Cannot close the competition. The following races are empty: {', '.join(race.name for race in incomplete_races)}"
        }, status=400)

    sorted_racers = SeasonRacer.get_sorted(season)
    top_racer = sorted_racers[0] if sorted_racers else None
    if top_racer:
        top_racer.racer.wdc += 1
        top_racer.racer.save()

    sorted_constructors = SeasonConstructor.get_sorted(season)
    top_constructor = sorted_constructors[0] if sorted_constructors else None
    if top_constructor:
        top_constructor.constructor.wcc += 1
        top_constructor.constructor.save()

    season.is_closed = True
    season.wdc = top_racer.racer.name if top_racer else None
    season.wcc = top_constructor.constructor.name if top_constructor else None
    season.save()

    return JsonResponse({
        "success": True
    }, status=200)

@csrf_exempt
def reopen_season(request, season_id):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    try:
        season = Season.objects.get(pk=season_id)
    except Season.DoesNotExist:
        return JsonResponse({"success": False, "error": "Competition not found."}, status=404)

    if not season.is_closed:
        return JsonResponse({"error": "This competition is already open."}, status=400)

    sorted_racers = SeasonRacer.get_sorted(season)
    top_racer = sorted_racers[0] if sorted_racers else None
    if top_racer:
        top_racer.racer.wdc = max(0, top_racer.racer.wdc - 1)
        top_racer.racer.save()

    sorted_constructors = SeasonConstructor.get_sorted(season)
    top_constructor = sorted_constructors[0] if sorted_constructors else None
    if top_constructor:
        top_constructor.constructor.wcc = max(0, top_constructor.constructor.wcc - 1)
        top_constructor.constructor.save()

    season.is_closed = False
    season.wdc = None
    season.wcc = None
    season.save()

    return JsonResponse({
        "success": True,
    }, status=200)

@csrf_exempt
def add_race(request, season_id):
    if request.method == 'POST':
        try:
            season = Season.objects.get(pk=season_id)
        except Season.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No such competition found'}, status=404)
        
        race = Race.objects.create(season=season, name=f"Race {season.races.count() + 1}")
        season.race_number += 1
        season.save()
        
        if season.is_closed:
            return JsonResponse({"error": "This season is closed. You cannot add races."}, status=403)

        return JsonResponse({'success': True}, status=200)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
