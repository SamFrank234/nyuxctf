from models import Team, Match


a = Team.objects.filter(group='A')
b = Team.objects.filter(group='B')
c = Team.objects.filter(group='C')
d = Team.objects.filter(group='D') 
groups=[a,b,c,d]

games=[]

for group in groups:
    print(group[0].group)
    for i in range(5):
        for j in range(i+1,5):
            print("i:%s j:%s" %(i, j))
            games.append(Match.objects.create(home_team=group[i], away_team = group[j]))
            games.append(Match.objects.create(home_team=group[j], away_team = group[i]))

for game in games:
    game.save()
