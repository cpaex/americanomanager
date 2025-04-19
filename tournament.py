import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import random

class Player:
    def __init__(self, name: str, ranking: int):
        self.name = name
        self.ranking = ranking

class Team:
    def __init__(self, player1: Player, player2: Player):
        self.players = [player1, player2]
        self.ranking = (player1.ranking + player2.ranking) / 2
        self.points = 0
        self.matches_played = 0
        self.matches_won = 0

    def __str__(self):
        return f"{self.players[0].name} & {self.players[1].name}"

class Match:
    def __init__(self, team1: Team, team2: Team, court: int, start_time: datetime):
        self.team1 = team1
        self.team2 = team2
        self.court = court
        self.start_time = start_time
        self.end_time = start_time + timedelta(hours=1)
        self.winner = None
        self.score = None

    def play_match(self, winner: Team):
        self.winner = winner
        self.score = self.calculate_score()
        winner.matches_won += 1
        winner.points += self.score
        self.team1.matches_played += 1
        self.team2.matches_played += 1

    def calculate_score(self) -> float:
        if self.winner == self.team1:
            higher_ranked = self.team2
            lower_ranked = self.team1
        else:
            higher_ranked = self.team1
            lower_ranked = self.team2

        base_points = 1.0
        if lower_ranked.ranking < higher_ranked.ranking:
            ranking_difference = higher_ranked.ranking - lower_ranked.ranking
            bonus_multiplier = 1 + (ranking_difference * 0.1)
            return base_points * bonus_multiplier
        return base_points

class Tournament:
    def __init__(self, name: str, num_courts: int = 8):
        self.name = name
        self.num_courts = num_courts
        self.teams: List[Team] = []
        self.matches: List[Match] = []
        self.schedule: Dict[datetime, List[Match]] = {}
        self.start_time = None
        self.end_time = None

    def add_team(self, team: Team):
        self.teams.append(team)

    def rotate_teams(self, teams: List[Team]) -> List[Team]:
        """Rotate teams clockwise, keeping the first team fixed"""
        if len(teams) <= 2:
            return teams
        return [teams[0]] + [teams[-1]] + teams[1:-1]

    def generate_round_robin_matches(self) -> List[Tuple[Team, Team]]:
        """Generate all matches using the clock method"""
        matches = []
        num_teams = len(self.teams)
        
        if num_teams % 2 != 0:
            raise ValueError("Number of teams must be even for round-robin tournament")

        # Create initial circle of teams
        circle = self.teams.copy()
        fixed_team = circle[0]
        rotating_teams = circle[1:]

        # Number of rounds needed
        num_rounds = num_teams - 1

        for round_num in range(num_rounds):
            # Generate matches for current round
            for i in range(num_teams // 2):
                team1 = rotating_teams[i]
                team2 = rotating_teams[-(i+1)]
                matches.append((team1, team2))

            # Rotate teams for next round
            rotating_teams = self.rotate_teams(rotating_teams)

        return matches

    def generate_schedule(self, start_time: datetime):
        """Generate schedule using round-robin method"""
        self.start_time = start_time
        current_time = start_time

        # Generate all matches using round-robin
        matches_to_schedule = self.generate_round_robin_matches()
        
        # Shuffle matches within each round to randomize court assignments
        matches_per_round = len(self.teams) // 2
        rounds = [matches_to_schedule[i:i + matches_per_round] 
                 for i in range(0, len(matches_to_schedule), matches_per_round)]
        
        for round_matches in rounds:
            # Shuffle matches within the round
            random.shuffle(round_matches)
            
            # Assign courts to matches
            available_courts = list(range(min(self.num_courts, len(round_matches))))
            current_round = []
            
            for match in round_matches:
                if available_courts:
                    court = available_courts.pop(0)
                    new_match = Match(match[0], match[1], court, current_time)
                    current_round.append(new_match)
                    self.matches.append(new_match)
            
            self.schedule[current_time] = current_round
            current_time += timedelta(hours=1)

        self.end_time = current_time

    def get_standings(self) -> pd.DataFrame:
        data = []
        for team in self.teams:
            data.append({
                'Team': str(team),
                'Points': team.points,
                'Matches Played': team.matches_played,
                'Matches Won': team.matches_won,
                'Win Rate': team.matches_won / team.matches_played if team.matches_played > 0 else 0
            })
        
        df = pd.DataFrame(data)
        return df.sort_values('Points', ascending=False)

    def get_prizes(self) -> Dict[str, List[Team]]:
        standings = self.get_standings()
        prizes = {
            'Champion': [self.teams[0]],
            'Runner-up': [self.teams[1]],
            'Third Place': [self.teams[2]],
            'Most Improved': [min(self.teams, key=lambda x: x.ranking)],
            'Best Underdog': [max(self.teams, key=lambda x: x.matches_won / x.matches_played if x.matches_played > 0 else 0)]
        }
        return prizes

    def print_schedule(self):
        for time, matches in self.schedule.items():
            print(f"\nTime: {time.strftime('%H:%M')}")
            for match in matches:
                print(f"Court {match.court + 1}: {match.team1} vs {match.team2}")

    def print_prizes(self):
        prizes = self.get_prizes()
        print("\nTournament Prizes:")
        for prize, teams in prizes.items():
            print(f"{prize}: {teams[0]}") 