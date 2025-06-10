from repositories.player_repository import get_passing_leaders, get_rushing_leaders, get_receiving_leaders

print("Passing Leaders:")
passing_leaders = get_passing_leaders(7)
for leader in passing_leaders:
    print(f"{leader[1]} :  att: {leader[2]}, cmp: {leader[3]}, yards: {leader[4]}, td: {leader[5]}")

print("")
print("Rushing Leaders:")
rushing_leaders = get_rushing_leaders(7)
for leader in rushing_leaders:
    print(f"{leader[1]} :  att: {leader[2]}, yards: {leader[3]}, td: {leader[4]}")

print("")
print("Receiving Leaders:")
receiving_leaders = get_receiving_leaders(7)
for leader in receiving_leaders:
    print(f"{leader[1]} :  rec: {leader[2]}, yards: {leader[3]}, td: {leader[4]}")