from tournament import Player, Team, Tournament
from datetime import datetime
import random
import os
import pandas as pd

class TournamentManager:
    def __init__(self):
        self.tournament = None
        self.players = []
        self.teams = []

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title):
        print("\n" + "="*50)
        print(f"{title:^50}")
        print("="*50 + "\n")

    def input_players(self):
        self.clear_screen()
        self.print_header("REGISTRO DE JUGADORES")
        
        num_players = int(input("¿Cuántos jugadores participarán? (debe ser número par): "))
        while num_players % 2 != 0:
            print("El número de jugadores debe ser par")
            num_players = int(input("¿Cuántos jugadores participarán? (debe ser número par): "))

        for i in range(num_players):
            print(f"\nJugador {i+1}:")
            name = input("Nombre: ")
            ranking = int(input("Ranking (1 es el mejor): "))
            self.players.append(Player(name, ranking))

    def create_teams(self):
        self.clear_screen()
        self.print_header("CREACIÓN DE EQUIPOS")
        
        # Ordenar jugadores por ranking
        sorted_players = sorted(self.players, key=lambda x: x.ranking)
        
        # Crear equipos balanceados
        for i in range(0, len(sorted_players), 2):
            team = Team(sorted_players[i], sorted_players[i+1])
            self.teams.append(team)
            print(f"Equipo creado: {team} (Ranking promedio: {team.ranking:.1f})")

    def setup_tournament(self):
        self.clear_screen()
        self.print_header("CONFIGURACIÓN DEL TORNEO")
        
        name = input("Nombre del torneo: ")
        num_courts = int(input("Número de canchas disponibles: "))
        start_time = input("Hora de inicio (formato HH:MM): ")
        
        # Convertir hora de inicio a datetime
        hour, minute = map(int, start_time.split(':'))
        start_datetime = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        self.tournament = Tournament(name, num_courts)
        for team in self.teams:
            self.tournament.add_team(team)
        
        self.tournament.generate_schedule(start_datetime)

    def show_schedule(self):
        self.clear_screen()
        self.print_header("PROGRAMA DEL TORNEO")
        
        for i, (time, matches) in enumerate(self.tournament.schedule.items()):
            print(f"\nRonda {i+1} - {time.strftime('%H:%M')}")
            print("-" * 50)
            for match in matches:
                print(f"Cancha {match.court + 1}:")
                print(f"  {match.team1} (Ranking: {match.team1.ranking:.1f})")
                print(f"  vs")
                print(f"  {match.team2} (Ranking: {match.team2.ranking:.1f})")
                print("-" * 30)

    def input_match_results(self):
        self.clear_screen()
        self.print_header("REGISTRO DE RESULTADOS")
        
        for round_num, (time, matches) in enumerate(self.tournament.schedule.items()):
            print(f"\nRonda {round_num + 1} - {time.strftime('%H:%M')}")
            print("-" * 50)
            
            for match in matches:
                print(f"\nPartido en Cancha {match.court + 1}:")
                print(f"1. {match.team1}")
                print(f"2. {match.team2}")
                
                while True:
                    try:
                        winner = int(input("¿Quién ganó? (1 o 2): "))
                        if winner in [1, 2]:
                            break
                        print("Por favor, ingrese 1 o 2")
                    except ValueError:
                        print("Por favor, ingrese un número válido")
                
                match.play_match(match.team1 if winner == 1 else match.team2)
                print(f"Puntos obtenidos: {match.score:.2f}")

    def show_standings(self):
        self.clear_screen()
        self.print_header("CLASIFICACIÓN ACTUAL")
        
        standings = self.tournament.get_standings()
        print(standings)

    def show_prizes(self):
        self.clear_screen()
        self.print_header("PREMIO FINAL")
        self.tournament.print_prizes()

    def save_results(self):
        filename = f"{self.tournament.name.replace(' ', '_')}_resultados.csv"
        standings = self.tournament.get_standings()
        standings.to_csv(filename, index=False)
        print(f"\nResultados guardados en {filename}")

    def run(self):
        while True:
            self.clear_screen()
            self.print_header("GESTOR DE TORNEO DE DOBLES")
            print("1. Registrar jugadores")
            print("2. Crear equipos")
            print("3. Configurar torneo")
            print("4. Ver programa")
            print("5. Registrar resultados")
            print("6. Ver clasificación")
            print("7. Ver premios")
            print("8. Guardar resultados")
            print("9. Salir")
            
            choice = input("\nSeleccione una opción: ")
            
            if choice == "1":
                self.input_players()
            elif choice == "2":
                if not self.players:
                    print("Primero debe registrar los jugadores")
                    input("Presione Enter para continuar...")
                    continue
                self.create_teams()
            elif choice == "3":
                if not self.teams:
                    print("Primero debe crear los equipos")
                    input("Presione Enter para continuar...")
                    continue
                self.setup_tournament()
            elif choice == "4":
                if not self.tournament:
                    print("Primero debe configurar el torneo")
                    input("Presione Enter para continuar...")
                    continue
                self.show_schedule()
            elif choice == "5":
                if not self.tournament:
                    print("Primero debe configurar el torneo")
                    input("Presione Enter para continuar...")
                    continue
                self.input_match_results()
            elif choice == "6":
                if not self.tournament:
                    print("Primero debe configurar el torneo")
                    input("Presione Enter para continuar...")
                    continue
                self.show_standings()
            elif choice == "7":
                if not self.tournament:
                    print("Primero debe configurar el torneo")
                    input("Presione Enter para continuar...")
                    continue
                self.show_prizes()
            elif choice == "8":
                if not self.tournament:
                    print("Primero debe configurar el torneo")
                    input("Presione Enter para continuar...")
                    continue
                self.save_results()
            elif choice == "9":
                break
            else:
                print("Opción no válida")
            
            input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    manager = TournamentManager()
    manager.run() 