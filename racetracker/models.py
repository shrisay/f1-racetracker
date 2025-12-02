from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    pass

class Racer(models.Model):
    name = models.CharField(max_length=64, unique=True)
    points = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    podiums = models.IntegerField(default=0)
    poles = models.IntegerField(default=0)
    races = models.IntegerField(default=0)
    wdc = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def count_positions(self, position):
        season_racers = self.season_racer.all()
        count = 0

        for season_racer in season_racers:
            count += RaceResult.objects.filter(racer=season_racer, position=position).count()

        return count

    def get_sorted(user):
        racers = Racer.objects.filter(user=user)

        def countback(racer):
            key = [-racer.wdc, -racer.points, -racer.wins]
            key.extend([-racer.count_positions(pos) for pos in range(2, 21)])
            key.append(-racer.poles)
            return tuple(key)
        return sorted(racers, key=countback)
    
    def __str__(self):
        return self.name


class Constructor(models.Model):
    name = models.CharField(max_length=64, unique=True)
    points = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    podiums = models.IntegerField(default=0)
    poles = models.IntegerField(default=0)
    wcc = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_sorted(user):
        constructors = Constructor.objects.filter(user=user)

        def key(constructor):
            racers = SeasonRacer.objects.filter(constructor=constructor)

            best_rank = float('inf')
            sorted_racers = Racer.get_sorted(user)
            for rank, racer in enumerate(sorted_racers, start=1):
                if racer in racers:
                    best_rank = rank
                    break

            return (
                -constructor.wcc,
                -constructor.points,
                -constructor.wins,
                -constructor.podiums,
                best_rank,
                -constructor.poles
            )
        return sorted(constructors, key=key)
    
    def __str__(self):
        return self.name

class Season(models.Model):
    name = models.CharField(max_length=64)
    racers = models.ManyToManyField(Racer, through="SeasonRacer", related_name="participated_seasons")
    constructors = models.ManyToManyField(Constructor, through="SeasonConstructor", related_name="participated_seasons")
    race_number = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_closed = models.BooleanField(default=False)
    wdc = models.CharField(max_length=128, null=True, blank=True)
    wcc = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"Competition: {self.name}"


class SeasonRacer(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="season_racers")
    racer = models.ForeignKey(Racer, on_delete=models.CASCADE, related_name="season_racer")
    points = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    podiums = models.IntegerField(default=0)
    poles = models.IntegerField(default=0)
    constructor = models.ForeignKey(Constructor, on_delete=models.SET_NULL, related_name="season_racers", null=True) 

    def count_positions(self, position):
        return RaceResult.objects.filter(racer=self, race__season=self.season, position=position).count()

    def get_sorted(season):
        racers = list(SeasonRacer.objects.filter(season=season))

        def countback(racer):
            key = [-racer.points, -racer.wins]
            key.extend([-racer.count_positions(pos) for pos in range(2, 21)])
            key.append(-racer.poles)
            return tuple(key)     
        return sorted(racers, key=countback)
    
    def __str__(self):
        return f"{self.racer.name} - {self.season.name}"


class SeasonConstructor(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="season_constructors")
    constructor = models.ForeignKey(Constructor, on_delete=models.CASCADE, related_name="season_constructor")
    points = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    podiums = models.IntegerField(default=0)
    poles = models.IntegerField(default=0)

    def get_sorted(season):
        constructors = list(SeasonConstructor.objects.filter(season=season))

        def key(constructor):
            racers = SeasonRacer.objects.filter(
                constructor=constructor.constructor,
                season=season
            )

            best_rank = float('inf')
            sorted_racers = SeasonRacer.get_sorted(season)
            for rank, racer in enumerate(sorted_racers, start=1):
                if racer in racers:
                    best_rank = rank
                    break

            return (
                -constructor.points,
                -constructor.wins,
                -constructor.podiums,
                best_rank,
                -constructor.poles
            )
        return sorted(constructors, key=key)
    
    def __str__(self):
        return f"{self.constructor.name} - {self.season.name}"
    

class Race(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="races")
    name = models.CharField(max_length=128, default="Race")
    participants = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Race: {self.name}"


class QualifyingResult(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name="qualifying")
    racer = models.ForeignKey(SeasonRacer, on_delete=models.CASCADE)
    position = models.IntegerField()

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"{self.racer.racer.name}: P{self.position}"


class RaceResult(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name="results")
    racer = models.ForeignKey(SeasonRacer, on_delete=models.CASCADE)
    position = models.IntegerField()
    points_awarded = models.IntegerField()
    dnf = models.BooleanField(default=False)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"{self.racer.racer.name}: P{self.position}. Season:{self.race.season.name} - Race: {self.race.name}"