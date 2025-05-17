import random

from repositories.player_repository import get_depth_chart_by_position
from repositories.team_repository import get_team_name


class Player:
    def __init__(self, id: int, name: str, skill: int):
        self.id = id
        self.name = name
        self.skill = skill
    
def get_player(team_id: int, position: str, order: int) -> Player:
    depth_chart = get_depth_chart_by_position(team_id, position)
    index = order - 1
    if depth_chart:
        player_id: int = depth_chart[index][0]
        player_name: str = depth_chart[index][1] + " " + depth_chart[index][2]
        player_skill: int = depth_chart[index][6]
        return Player(player_id, player_name, player_skill)
    return None

class Team:
    def __init__(self, team_id: int):

        self.team_id: int = team_id
        self.team_name: str = get_team_name(team_id)

        self.QB: Player = get_player(team_id, "QB", 1)
        self.RB1: Player = get_player(team_id, "RB", 1)
        self.RB2: Player = get_player(team_id, "RB", 2)
        self.WR1: Player = get_player(team_id, "WR", 1)
        self.WR2: Player = get_player(team_id, "WR", 2)
        self.WR3: Player = get_player(team_id, "WR", 3)
        self.OL1: Player = get_player(team_id, "OL", 1)
        self.OL2: Player = get_player(team_id, "OL", 2)
        self.OL3: Player = get_player(team_id, "OL", 3)
        self.OL4: Player = get_player(team_id, "OL", 4)
        self.OL5: Player = get_player(team_id, "OL", 5)
        self.DL1: Player = get_player(team_id, "DL", 1)
        self.DL2: Player = get_player(team_id, "DL", 2)
        self.DL3: Player = get_player(team_id, "DL", 3)
        self.DL4: Player = get_player(team_id, "DL", 4)
        self.LB1: Player = get_player(team_id, "LB", 1)
        self.LB2: Player = get_player(team_id, "LB", 2)
        self.LB3: Player = get_player(team_id, "LB", 3)
        self.DB1: Player = get_player(team_id, "DB", 1)
        self.DB2: Player = get_player(team_id, "DB", 2)
        self.DB3: Player = get_player(team_id, "DB", 3)
        self.DB4: Player = get_player(team_id, "DB", 4)

        # Find the highest rated returner among RBs, WRs, DBs
        candidates = [
            self.RB1, self.RB2,
            self.WR1, self.WR2, self.WR3,
            self.DB1, self.DB2, self.DB3, self.DB4
        ]
        # Remove None values in case a player is missing
        candidates = [p for p in candidates if p is not None]
        self.returner: Player = max(candidates, key=lambda p: p.skill) if candidates else None

        self.defenseRating: int = int((self.DL1.skill + self.DL2.skill + self.DL3.skill + self.DL4.skill + \
            self.LB1.skill + self.LB2.skill + self.LB3.skill + self.DB1.skill + self.DB2.skill + \
            self.DB3.skill + self.DB4.skill) * 10 / 11)
        
        self.runningGameRating: int = int((self.RB1.skill*3) + (self.RB2.skill*2) + self.OL1.skill + self.OL2.skill + \
            self.OL3.skill + self.OL4.skill + self.OL5.skill)
        
        self.passingGameRating: int = int((self.QB.skill*3) + (self.WR1.skill*1.5) + self.WR2.skill + self.WR3.skill + \
            ((self.OL1.skill + self.OL2.skill + self.OL3.skill + self.OL4.skill + self.OL5.skill + self.RB1.skill + self.RB2.skill) / 2))
        
    
    def print_lineup(self):
        print("Offense:")
        print(f"QB: {self.QB.name} Skill: {self.QB.skill}")
        print(f"RB1: {self.RB1.name} Skill: {self.RB1.skill}")
        print(f"RB2: {self.RB2.name} Skill: {self.RB2.skill}")
        print(f"WR1: {self.WR1.name} Skill: {self.WR1.skill}")
        print(f"WR2: {self.WR2.name} Skill: {self.WR2.skill}")
        print(f"WR3: {self.WR3.name} Skill: {self.WR3.skill}")
        print(f"OL1: {self.OL1.name} Skill: {self.OL1.skill}")
        print(f"OL2: {self.OL2.name} Skill: {self.OL2.skill}")
        print(f"OL3: {self.OL3.name} Skill: {self.OL3.skill}")
        print(f"OL4: {self.OL4.name} Skill: {self.OL4.skill}")
        print(f"OL5: {self.OL5.name} Skill: {self.OL5.skill}")
        print("Defense:")
        print(f"DL1: {self.DL1.name} Skill: {self.DL1.skill}")
        print(f"DL2: {self.DL2.name} Skill: {self.DL2.skill}")
        print(f"DL3: {self.DL3.name} Skill: {self.DL3.skill}")
        print(f"DL4: {self.DL4.name} Skill: {self.DL4.skill}")
        print(f"LB1: {self.LB1.name} Skill: {self.LB1.skill}")
        print(f"LB2: {self.LB2.name} Skill: {self.LB2.skill}")
        print(f"LB3: {self.LB3.name} Skill: {self.LB3.skill}")
        print(f"DB1: {self.DB1.name} Skill: {self.DB1.skill}")
        print(f"DB2: {self.DB2.name} Skill: {self.DB2.skill}")
        print(f"DB3: {self.DB3.name} Skill: {self.DB3.skill}")
        print(f"DB4: {self.DB4.name} Skill: {self.DB4.skill}")
        print("")

# For Box Scores
class PassingStatLine:
    def __init__(self, attempts: int, completions: int, yards: int, td: int):
        self.attempts = attempts
        self.completions = completions
        self.yards = yards
        self.td = td

class RushingStatLine:
    def __init__(self, attempts, yards, td):
        self.attempts = attempts
        self.yards = yards
        self.td = td

class ReceivingStatLine:
    def __init__(self, receptions, yards, td):
        self.receptions = receptions
        self.yards = yards
        self.td = td
        
    


class Game:
    def __init__(self, homeTeam: Team, awayTeam: Team):
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam

        self.homeScore: int = 0
        self.awayScore: int = 0

        self.possession: Team = None
        self.defending: Team = None

        self.quarter: int = 1
        self.clock: int = 900
        self.down: int = 1
        self.yardsToTd: int = 10
        self.yardsToDown: int = 10

        self.toss_winner: Team = None
        self.toss_loser: Team = None

        self.passing_stats = {}
        self.rushing_stats = {}
        self.receiving_stats = {}

        self.lastTouch: Player = None
        self.lastPlayType: str = None # "pass" or "rush"
    
    def get_clock(self):
        """
        Get the current game clock.
        """
        if self.clock < 0:
            return "0"
        else:
            minutes = int(self.clock / 60)
            seconds = int(self.clock % 60)
            return f"{minutes:02}:{seconds:02}"

    def coin_toss(self):
        """
        Simulate a coin toss to determine possession.
        """
        if random.randint(0, 1) == 0:
            self.possession = self.homeTeam
            self.defending = self.awayTeam
        else:
            self.possession = self.awayTeam
            self.defending = self.homeTeam
        
        self.toss_winner = self.possession
        self.toss_loser = self.defending

        print(f"Coin Toss: {self.possession.team_name} team wins the toss.")
        print("They opt to receive the kickoff.")
        print("")
    
    def kickoff(self):
        """
        Simulate a kickoff.
        """
        if self.possession == self.homeTeam:
            print(f"{self.awayTeam.team_name} kicks off to {self.homeTeam.team_name}.")

        else:
            print(f"{self.homeTeam.team_name} kicks off to {self.awayTeam.team_name}.")
        
        returner: Player = self.possession.returner
        print(f"{self.possession.team_name} returner is {returner.name} with skill {returner.skill}.")
        returnYards: int = random.randint(5, 20) + returner.skill
        print(f"{returner.name} returns the kickoff for {returnYards} yards.")
        self.yardsToTd = 100 - returnYards
        self.yardsToDown = 10
        self.clock -= returnYards / 4

        # this is valid because the returner cant go over 50 yards, it will need to be ammended when the returner can go beyond that.
        print(f"{self.possession.QB.name} and the {self.possession.team_name} have the ball at their own {100 - self.yardsToTd} yard line.")
        print(f"Quarter : {self.quarter}, Clock: {self.get_clock()}")
        print("")
    
    def exec_play(self):
        if random.randint(1, 3) == 1:
            self.running_play()
        else:
            self.passing_play()

    def running_play(self):
        yardsGained: int = random.randint(-5, 10)

        if random.randint(1, 3) == 1:
            rusher: Player = self.possession.RB2
        else:
            rusher: Player = self.possession.RB1

        print(f"{rusher.name} rushes for {yardsGained} yards.")

        self.lastTouch = rusher
        self.lastPlayType = "rush"

        self.yardsToTd -= yardsGained
        self.yardsToDown -= yardsGained

        if self.yardsToDown <= 0:
            if self.yardsToTd > 0:
                print("1st Down!")
            self.yardsToDown = 10
            self.down = 1
        else:
            self.down += 1
            
            self.clock -= random.randint(25, 40)

        if rusher in self.rushing_stats:
            self.rushing_stats[rusher].attempts += 1
            self.rushing_stats[rusher].yards += yardsGained
        else:
            self.rushing_stats[rusher] = RushingStatLine(1, yardsGained, 0)

    def passing_play(self):
        CmpPercentage = 50 + (30 * self.possession.passingGameRating)/(self.possession.passingGameRating + self.defending.defenseRating)
        
        randReceiver = random.randint(1, 11)
        if randReceiver > 7:
            receiver: Player = self.possession.WR1 # 4/11 chance
        elif randReceiver > 4:
            receiver: Player = self.possession.WR2 # 3/11 chance
        elif randReceiver > 2:
            receiver: Player = self.possession.WR3 # 2/11 chance
        elif randReceiver > 1:
            receiver: Player = self.possession.RB1 # 1/11 chance
        else:
            receiver: Player = self.possession.RB2 # 1/11 chance
        
        if random.randint(1, 100) <= CmpPercentage:
            print(f"{self.possession.QB.name} completes the pass to {receiver.name}.")

            self.lastTouch = receiver
            self.lastPlayType = "pass"

            yardsGained: int = random.randint(-5, 30)

            if yardsGained > 0:
                print(f"{receiver.name} gains {yardsGained} yards.")
            else:
                print(f"{receiver.name} TFL, loses {-yardsGained} yards.")

            self.yardsToTd -= yardsGained
            self.yardsToDown -= yardsGained

            if self.yardsToDown <= 0:
                if self.yardsToTd > 0:
                    print("1st Down!")
                self.yardsToDown = 10
                self.down = 1
            else:
                self.down += 1
            
            self.clock -= random.randint(25, 40)

            if self.possession.QB in self.passing_stats:
                self.passing_stats[self.possession.QB].attempts += 1
                self.passing_stats[self.possession.QB].completions += 1
                self.passing_stats[self.possession.QB].yards += yardsGained
            else:
                self.passing_stats[self.possession.QB] = PassingStatLine(1, 1, yardsGained, 0)

            if receiver in self.receiving_stats:
                self.receiving_stats[receiver].receptions += 1
                self.receiving_stats[receiver].yards += yardsGained
            else:
                self.receiving_stats[receiver] = ReceivingStatLine(1, yardsGained, 0)
        else:
            print(f"{self.possession.QB.name} throws an incomplete pass to {receiver.name}.")

            if self.possession.QB in self.passing_stats:
                self.passing_stats[self.possession.QB].attempts += 1

            self.down += 1


    def punt(self):
        print(f"{self.possession.team_name} punts the ball.")
        yardsGained: int = random.randint(30, 60)

        if self.yardsToTd - yardsGained < 0:
            # if the punt goes into the end zone, touchback
            print(f"Touchback! {self.defending.team_name} takes over at their own 25 yard line.")
            self.yardsToTd = 25
        else:
            self.yardsToTd = self.yardsToTd - yardsGained

        # simulate possession change
        self.yardsToTd = 100 - self.yardsToTd
        self.possession, self.defending = self.defending, self.possession
        print(f"Fair Catch! {self.possession.team_name} takes over possession, {self.yardsToTd} yards from the end zone.")

        # reset the down marker
        self.yardsToDown = 10
        self.down = 1
        self.clock -= random.randint(25, 40)
        print("")

    def field_goal_attempt(self):
        print(f"{self.possession.team_name} attempts a field goal.")
        if random.randint(1,5) == 5:
            print("Missed field goal!")
            self.possession, self.defending = self.defending, self.possession
            self.yardsToTd = 100 - self.yardsToTd
            self.down = 1
            self.yardsToDown = 1
            print("")
        else:
            print("Field goal is good!")
            if self.possession == self.homeTeam:
                self.homeScore += 3
            else:
                self.awayScore += 3
            self.possession, self.defending = self.defending, self.possession
            self.yardsToDown = 10
            self.down = 1
            print(self.get_score())
            print("")
            self.kickoff()

    def get_down(self):
        if self.down == 1:
            return "1st"
        elif self.down == 2:
            return "2nd"
        elif self.down == 3:
            return "3rd"
        elif self.down == 4:
            return "4th"

    def get_score(self):
        return f"{self.homeTeam.team_name}: {self.homeScore}, {self.awayTeam.team_name}: {self.awayScore}" 
    
    def print_game_status(self):
        #print("Score:")
        #print(self.homeTeam.team_name + " " + str(self.homeScore))
        #print(self.awayTeam.team_name + " " + str(self.awayScore))
        #print("")

        if self.yardsToTd > 0:
            print("Quarter" + " " + str(self.quarter) + ", Clock: " + self.get_clock())
            print(self.possession.team_name + " has the ball, " + str(self.yardsToTd) + " yards to the end zone.")
            print(self.get_down() + " and " + str(self.yardsToDown))
        print("")

def simulate_game(homeTeamId: int, awayTeamId: int):
    """
    Simulate a game between two teams.
    """

    homeTeam: Team = Team(homeTeamId)
    awayTeam: Team = Team(awayTeamId)

    game: Game = Game(homeTeam, awayTeam)

    # Start the game
    # COIN TOSS
    # Coin toss, set possession to the winning team, defending to the the losing team
    game.coin_toss()
    # Set clock to 15mins (900), quarter to 1.
    game.clock = 900
    game.quarter = 1
    # KICKOFF
    # Defending team kicks ball off to possession team, possession returner returns ball,
    # Ball marked (100 - distance of return) from touchdown, reset downs (1st and 10)
    game.kickoff()
    # OFFENSIVE POSSESSION
    # Run random passing or running plays until 4th down OR Touchdown OR End Of Quarter (Clock = 0),
    # After each play, reduce the yards to td AND yards to down by number of yards gained.
    # Reduce time on clock by 30 seconds for each complete pass or run.
    # If yards to down < 0, reset downs(1st and 10)
    while game.quarter < 5:
        while (game.down < 4 and game.yardsToTd > 0 and game.clock > 0):
            game.exec_play()
            game.print_game_status()
        if game.yardsToTd <= 0:
            # TOUCHDOWN
            print(f"{game.possession.team_name} TOUCHDOWN!")
            if game.lastPlayType == "pass":
                print(f"{game.possession.QB.name} -> {game.lastTouch.name}")
            elif game.lastPlayType == "rush":
                print(game.lastTouch.name)
            if game.possession == homeTeam:
                game.homeScore += 7
            else:
                game.awayScore += 7
            print(game.get_score())
            print("")

            # add touchdown to the stats
            if game.lastPlayType == "pass":
                if game.lastTouch in game.receiving_stats:
                    game.receiving_stats[game.lastTouch].td += 1
                else:
                    game.receiving_stats[game.lastTouch] = ReceivingStatLine(0, 0, 1)

                if game.possession.QB in game.passing_stats:
                    game.passing_stats[game.possession.QB].td += 1
                else:
                    game.passing_stats[game.possession.QB] = PassingStatLine(0, 0, 0, 1)
            
            elif game.lastPlayType == "rush":
                if game.lastTouch in game.rushing_stats:
                    game.rushing_stats[game.lastTouch].td += 1
                else:
                    game.rushing_stats[game.lastTouch] = RushingStatLine(0, 0, 1)
            game.possession, game.defending = game.defending, game.possession
            game.down = 1
            game.yardsToTd = 100
            game.kickoff()
        elif game.clock <= 0:
            # END OF QUARTER
            if game.quarter == 1:
                print("2nd Quarter")
                game.quarter = 2
                game.clock = 900
            elif game.quarter == 2:
                print("End of 1st half")
                print("3rd Quarter")
                game.quarter = 3
                game.clock = 900
                game.possession = game.toss_loser
                game.defending = game.toss_winner
                game.kickoff()
            elif game.quarter == 3:
                print("4th Quarter")
                game.quarter = 4
                game.clock = 900
            elif game.quarter == 4:
                break
        elif game.down == 4:
            if game.yardsToTd < 50:
                game.field_goal_attempt()
            else:
                game.punt()
    print("")
    print("END OF GAME")
    print("Score: ")
    print(game.homeTeam.team_name + " " + str(game.homeScore))
    print(game.awayTeam.team_name + " " + str(game.awayScore))
    print("")
    print("BOX SCORE")
    print("----------------------")
    print("Passing Stats")
    print(game.homeTeam.team_name)
    for player, stats in game.passing_stats.items():
        if player == game.homeTeam.QB:
            print(f"{player.name}: {stats.attempts} attempts, {stats.completions} completions, {stats.yards} yards, {stats.td} TDs")
    print("")
    print(game.awayTeam.team_name)
    for player, stats in game.passing_stats.items():
        if player == game.awayTeam.QB:
            print(f"{player.name}: {stats.attempts} attempts, {stats.completions} completions, {stats.yards} yards, {stats.td} TDs")
    print("-----------------------")
    print("Rushing Stats")
    print(game.homeTeam.team_name)
    for player, stats in game.rushing_stats.items():
        if player == game.homeTeam.RB1 or player == game.homeTeam.RB2:
            print(f"{player.name}: {stats.attempts} attempts, {stats.yards} yards, {stats.td} TDs")
    print("")
    print(game.awayTeam.team_name)
    for player, stats in game.rushing_stats.items():
        if player == game.awayTeam.RB1 or player == game.awayTeam.RB2:
            print(f"{player.name}: {stats.attempts} attempts, {stats.yards} yards, {stats.td} TDs")
    print("-----------------------")
    print("Receiving Stats")
    print(game.homeTeam.team_name)
    for player, stats in game.receiving_stats.items():
        if player == game.homeTeam.WR1 or player == game.homeTeam.WR2 or player == game.homeTeam.WR3 or player == game.homeTeam.RB1 or player == game.homeTeam.RB2:
            print(f"{player.name}: {stats.receptions} receptions, {stats.yards} yards, {stats.td} TDs")
    print("")
    print(game.awayTeam.team_name)
    for player, stats in game.receiving_stats.items():
        if player == game.awayTeam.WR1 or player == game.awayTeam.WR2 or player == game.awayTeam.WR3 or player == game.awayTeam.RB1 or player == game.awayTeam.RB2:
            print(f"{player.name}: {stats.receptions} receptions, {stats.yards} yards, {stats.td} TDs")
    print("-----------------------")
    print("")

    

simulate_game(1, 2)
    