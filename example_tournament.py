from tournament import Player, Team, Tournament
from datetime import datetime
import random

def print_round_details(tournament: Tournament, round_num: int):
    """Print detailed information about a specific round"""
    print(f"\n{'='*50}")
    print(f"Ronda {round_num + 1}")
    print(f"{'='*50}")
    
    # Get matches for this round
    time_slot = list(tournament.schedule.keys())[round_num]
    matches = tournament.schedule[time_slot]
    
    for match in matches:
        print(f"Cancha {match.court + 1}:")
        print(f"  {match.team1} (Ranking: {match.team1.ranking:.1f})")
        print(f"  vs")
        print(f"  {match.team2} (Ranking: {match.team2.ranking:.1f})")
        print("-" * 30)

def main():
    # Crear jugadores con rankings (1 siendo el mejor)
    players = [
        Player("Juan", 1),    # Mejor ranking
        Player("María", 2),
        Player("Carlos", 3),
        Player("Ana", 4),
        Player("Pedro", 5),
        Player("Laura", 6),
        Player("Miguel", 7),
        Player("Sofía", 8),
        Player("David", 9),
        Player("Elena", 10),
        Player("Jorge", 11),
        Player("Marta", 12),
        Player("Pablo", 13),
        Player("Lucía", 14),
        Player("Antonio", 15),
        Player("Isabel", 16)  # Peor ranking
    ]

    # Crear equipos (parejas de jugadores)
    teams = []
    for i in range(0, len(players), 2):
        teams.append(Team(players[i], players[i+1]))

    # Crear torneo
    tournament = Tournament("Torneo de Dobles Americano")
    for team in teams:
        tournament.add_team(team)

    # Generar horario comenzando a las 9:00 AM
    start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    tournament.generate_schedule(start_time)

    # Imprimir información detallada de cada ronda
    print("\nPROGRAMA DEL TORNEO")
    print("=" * 50)
    for i in range(len(tournament.schedule)):
        print_round_details(tournament, i)

    # Simular los partidos
    print("\nSIMULACIÓN DE RESULTADOS")
    print("=" * 50)
    for match in tournament.matches:
        # Simular resultado basado en rankings (equipo con mejor ranking tiene más probabilidad de ganar)
        team1_prob = 0.5 + (match.team2.ranking - match.team1.ranking) * 0.05
        winner = match.team1 if random.random() < team1_prob else match.team2
        match.play_match(winner)
        
        print(f"\nPartido: {match.team1} vs {match.team2}")
        print(f"Ganador: {winner}")
        print(f"Puntos obtenidos: {match.score:.2f}")

    # Imprimir clasificación final
    print("\nCLASIFICACIÓN FINAL")
    print("=" * 50)
    standings = tournament.get_standings()
    print(standings)

    # Imprimir premios
    print("\nPREMIO FINAL")
    print("=" * 50)
    tournament.print_prizes()

if __name__ == "__main__":
    main() 