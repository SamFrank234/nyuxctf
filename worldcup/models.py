from enum import Enum
from django.db import models
from django.db.models import F, Q, Value
from django.utils import timezone
# Create your models here.


class Team(models.Model):
    
    #Team Info
    f_name = models.CharField(max_length=25)
    l_name = models.CharField(max_length=25)
    country = models.CharField(max_length=25, unique=True)
    group = models.CharField(max_length=1, default='0')

    matches = models.ManyToManyField("Match", blank=True)

    def __str__(self) -> str:
        return self.f_name+" "+self.l_name


class MatchManager(models.Manager):
    
    #Result of Match: 1 if Home wins, 2 is Away wins, 3 if draw
    def with_result (self):
        result =3
        match = F('home_goals')-F('away_goals')
        if(match>Value(0)):
            result=1
        elif(match<Value(0)):
            result=2    

        return self.annotate(result = result)

class Match(models.Model):
    home_team = models.ForeignKey(Team, related_name="home_game", on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name="away_game", on_delete=models.CASCADE)
    date =models.DateTimeField(default=timezone.now)

    home_goals = models.PositiveIntegerField(default=0)
    away_goals = models.PositiveIntegerField(default=0)

    groupstage = models.BooleanField(default=True)
    live = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)

    objects = MatchManager()

    def __str__(self) -> str:
        result = "%s at %s" %(self.away_team, self.home_team)
        return result

    
    @property
    def result(self) -> int:
        if(self.home_goals>self.away_goals):
            return 1
        elif(self.home_goals<self.away_goals):
            return 2
        else:
            return 3




'''

class TeamMatch(models.Model):

    class Result(Enum):
        WIN = 3
        DRAW = 1
        LOSS = 0

    team = models.ForeignKey(Team, related_name='result', on_delete=models.PROTECT)
    match = models.ForeignKey(Match, on_delete=models.PROTECT)
    
    goals = models.PositiveIntegerField(default=0)
    allowed = models.PositiveIntegerField(default=0)
    fairplay_pts = models.PositiveIntegerField(default=0)

    groupstage = models.BooleanField(default=True)

    @property
    def result(self) -> Result:
        if(self.goals>self.allowed):
            return Result.WIN
        elif(self.goals < self.allowed):
            return Result.LOSS
        else:
            return Result.DRAW

    class Meta():
        unique_together = ['team', 'match']


'''


'''

class MatchManager(models.Manager):
    def create_match(self, home_team, away_team, home_goals, away_goals, date, complete):
        match = self.create(home_team=home_team, away_team=away_team, home_goals=home_goals, away_goals=away_goals, date=date, complete=complete)
        if (complete):
            home = Team.objects.filter(f_name=home_team.f_name)
            away = Team.objects.filter(l_name=away_team.l_name)
            home.update(goals_for=F('goals_for')+home_goals, goals_against=F('goals_against')+away_goals)
            away.update(goals_for=F('goals_for')+away_goals, goals_against=F('goals_against')+home_goals)
            
        return match

    def get_matches(self, team):
        match_list = self.get_queryset().filter(Q(home_team = team) | Q(away_team = team))
        return match_list
        '''