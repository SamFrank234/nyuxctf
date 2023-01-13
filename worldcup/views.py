from colorsys import hls_to_rgb
from itertools import chain
from operator import attrgetter
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from .models import *

# Create your views here.

def index(request):
    
    grp_a = Team.objects.filter(group='A')
    grp_b = Team.objects.filter(group='B')
    grp_c = Team.objects.filter(group='C')
    grp_d = Team.objects.filter(group='D')

    groups = [grp_a, grp_b, grp_c, grp_d]
    recent_results = Match.objects.filter(complete=True).order_by('-date')[:5]
    upcoming = Match.objects.filter(complete=False).order_by('-date')

    context={
        'A': [],
        'B': [],
        'C': [],
        'D': [],
        'results':recent_results,
        'upcoming':upcoming
    }
    
    for group in groups:
        list =[]

        for team in group:
            stats = get_stats(team)
            team_info = {
                'name': team.f_name,
                'gp': stats['games_played'],
                'w': stats['wins'],
                'l': stats['losses'],
                'd': stats['draws'],
                'gd': stats['goals_for']-stats['goals_against'],
                'pts': 3*stats['wins']+stats['draws']
            }
            list.append(team_info)
        
        list = sorted(list, key=lambda k:k['gd'], reverse=True)
        list = sorted(list, key=lambda k:k['pts'], reverse=True)
        context[group[0].group] = list

    return render(request, 'worldcup/index.html', context)


def team(request, team_name):
    team = Team.objects.get(f_name__iexact=team_name)
    if not team:
        return HttpResponse(f'')
    else:

        #get group info and sort for standings
        group = Team.objects.filter(group=team.group)
        list=[]
        for player in group:
            stats = get_stats(player)
            player_info = {
                'name': player.f_name,
                'gp': stats['games_played'],
                'w': stats['wins'],
                'l': stats['losses'],
                'd': stats['draws'],
                'gd': stats['goals_for']-stats['goals_against'],
                'pts': 3*stats['wins']+stats['draws']
            }
            list.append(player_info)
        list = sorted(list, key=lambda k:k['gd'], reverse=True)
        list = sorted(list, key=lambda k:k['pts'], reverse=True)

        #get team specific info
        h_games = team.home_game.filter(complete=True)
        a_games = team.away_game.filter(complete=True)
        h_upcoming = team.home_game.filter(complete=False)
        a_upcoming = team.away_game.filter(complete=False)

        match_list = sorted(
            chain(h_games, a_games),
            key=attrgetter('date'),
            reverse=True
        )
        upcoming_list = sorted(
            chain(h_upcoming, a_upcoming),
            key=attrgetter('date'),
            reverse=True
        )
        stats = get_stats(team)
        context = {
            'team': team,
            'results': match_list,
            'upcoming': upcoming_list,
            'points': 3*stats['wins']+stats['draws'],
            'group':list
        }
        return render(request, 'worldcup/team.html', context=context)

    
        

def schedule(request):
    past = Match.objects.filter(complete = True).filter(live=False).order_by('-date')
    upcoming = Match.objects.filter(complete=False).filter(live=False)
    live = Match.objects.filter(live=True)
    return render(request, 'worldcup/schedule.html', context={'live':live, 'upcoming':upcoming, 'past':past})


def match(request, match_id):
    match = Match.objects.get(id=match_id)
    if not match:
        return HttpResponse(404)
    elif match.live:
         return HttpResponseRedirect(reverse('live', args=(match_id,)))
    else:
        return render(request, 'worldcup/match.html', context={'match':match})


def live(request, match_id):
    try:
        match = Match.objects.get(id=match_id)
    except ObjectDoesNotExist:
        return HttpResponse(404)
    if match.live:
        return render(request, 'worldcup/live.html', context={'match':match})
    else:
        return HttpResponseRedirect(reverse('match', args=(match_id,)))

def bracket(request):
    return HttpResponse("Bracket View")


def get_stats(team):
    h_games = team.home_game.filter(complete=True)
    a_games = team.away_game.filter(complete=True)
    h_results = h_games.aggregate(
        wins=Count('pk', filter=Q(home_goals__gt=F('away_goals'))),
        losses=Count('pk', filter=Q(home_goals__lt=F('away_goals'))),
        draws=Count('pk', filter=Q(home_goals=F('away_goals'))),
        total_goals = Coalesce(Sum('home_goals'),0),
        total_allowed = Coalesce(Sum('away_goals'), 0)
    )
    a_results = a_games.aggregate(
        wins=Count('pk', filter=Q(home_goals__lt=F('away_goals'))),
        losses=Count('pk', filter=Q(home_goals__gt=F('away_goals'))),
        draws=Count('pk', filter=Q(home_goals=F('away_goals'))),
        total_goals = Coalesce(Sum('away_goals'), 0),
        total_allowed = Coalesce(Sum('home_goals'),0)
    )

    stats = {
        'games_played': h_games.count()+a_games.count(),
        'wins': h_results['wins']+a_results['wins'],
        'losses': h_results['losses']+a_results['losses'],
        'draws': h_results['draws']+a_results['draws'],
        'goals_for': h_results['total_goals']+a_results['total_goals'],
        'goals_against': h_results['total_allowed']+a_results['total_allowed']
    }
    return stats

