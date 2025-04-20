import streamlit as st
import pandas as pd
import plotly.express as px
from tournament import Player, Team, Tournament, Match
from datetime import datetime
import random
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from config import CLUB_NAME, CLUB_LOGO
from supabase import create_client, Client
import os
from typing import Tuple, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase setup with error handling
def init_supabase() -> Optional[Client]:
    try:
        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

        if not SUPABASE_URL or not SUPABASE_KEY:
            st.error("❌ Error: SUPABASE_URL and SUPABASE_KEY environment variables are not set")
            logger.error("Supabase credentials not found in environment variables")
            return None

        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"❌ Error connecting to Supabase: {str(e)}")
        logger.error(f"Supabase connection error: {str(e)}")
        return None

supabase = init_supabase()
if not supabase:
    st.stop()

def handle_db_error(e: Exception, operation: str) -> None:
    """Handle database errors and display appropriate messages"""
    error_msg = f"❌ Error during {operation}: {str(e)}"
    st.error(error_msg)
    logger.error(error_msg)

# Configuración de la página
st.set_page_config(
    page_title=f"Torneo de Dobles - {CLUB_NAME}",
    page_icon="🎾",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .header {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 2rem;
    }
    .header img {
        height: 100px;
        margin-right: 1rem;
    }
    .header h1 {
        color: #1e3a8a;
        margin: 0;
    }
    .team-card {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .court-container {
        position: relative;
        width: 100%;
        height: 300px;
        margin-bottom: 1rem;
    }
    .court-number {
        position: absolute;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 48px;
        font-weight: bold;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        opacity: 0.2;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialización del estado de la sesión
if 'tournament' not in st.session_state:
    st.session_state.tournament = None
if 'players' not in st.session_state:
    st.session_state.players = []
if 'teams' not in st.session_state:
    st.session_state.teams = []

def generate_players() -> Tuple[List[Player], List[Player]]:
    """Genera un conjunto predefinido de 40 jugadores (20 hombres y 20 mujeres) con rankings aleatorios"""
    try:
        male_names = [
            "Juan", "Carlos", "Pedro", "Miguel", "David", "Jorge", "Pablo", "Antonio",
            "Fernando", "Javier", "Manuel", "José", "Francisco", "Ángel", "Alberto", "Sergio",
            "Diego", "Raúl", "Rubén", "Adrián"
        ]
        
        female_names = [
            "María", "Ana", "Laura", "Sofía", "Elena", "Marta", "Lucía", "Isabel",
            "Carmen", "Rosa", "Teresa", "Patricia", "Silvia", "Cristina", "Nuria", "Marina",
            "Beatriz", "Victoria", "Claudia", "Natalia"
        ]
        
        # Generar rankings aleatorios para hombres (1-20)
        male_rankings = list(range(1, 21))
        random.shuffle(male_rankings)
        
        # Generar rankings aleatorios para mujeres (21-40)
        female_rankings = list(range(21, 41))
        random.shuffle(female_rankings)
        
        # Crear jugadores hombres
        male_players = []
        for name, ranking in zip(male_names, male_rankings):
            try:
                data = supabase.table('players').insert({
                    "name": name,
                    "gender": "M",
                    "ranking": ranking
                }).execute()
                player_id = data.data[0]['id']
                male_players.append(Player(name=name, ranking=ranking, gender="M", id=player_id))
            except Exception as e:
                handle_db_error(e, f"creating male player {name}")
                continue
        
        # Crear jugadoras mujeres
        female_players = []
        for name, ranking in zip(female_names, female_rankings):
            try:
                data = supabase.table('players').insert({
                    "name": name,
                    "gender": "F",
                    "ranking": ranking
                }).execute()
                player_id = data.data[0]['id']
                female_players.append(Player(name=name, ranking=ranking, gender="F", id=player_id))
            except Exception as e:
                handle_db_error(e, f"creating female player {name}")
                continue
        
        if not male_players or not female_players:
            raise Exception("No se pudieron crear los jugadores")
            
        return male_players, female_players
        
    except Exception as e:
        handle_db_error(e, "generating players")
        raise

def create_mixed_teams(male_players: List[Player], female_players: List[Player]) -> List[Team]:
    """Crea 20 parejas mixtas (un hombre y una mujer)"""
    try:
        if len(male_players) != len(female_players):
            raise ValueError("Debe haber el mismo número de jugadores hombres y mujeres")
        
        # Mezclar los jugadores de cada género
        random.shuffle(male_players)
        random.shuffle(female_players)
        
        # Crear equipos mixtos
        teams = []
        for i, (male, female) in enumerate(zip(male_players, female_players)):
            try:
                team_name = f"Equipo {i+1}"
                average_ranking = (male.ranking + female.ranking) / 2
                
                data = supabase.table('teams').insert({
                    "name": team_name,
                    "player1_id": male.id,
                    "player2_id": female.id,
                    "average_ranking": average_ranking
                }).execute()
                team_id = data.data[0]['id']
                
                team = Team(player1=male, player2=female, id=team_id)
                teams.append(team)
            except Exception as e:
                handle_db_error(e, f"creating team {i+1}")
                continue
        
        if not teams:
            raise Exception("No se pudieron crear los equipos")
            
        return teams
        
    except Exception as e:
        handle_db_error(e, "creating teams")
        raise

def main():
    st.title("🎾 Gestor de Torneo de Dobles Americano")
    
    # Menú lateral
    menu = st.sidebar.selectbox(
        "Menú Principal",
        ["Inicio", "Registro de Jugadores", "Creación de Equipos", 
         "Configuración del Torneo", "Programa de Partidos", 
         "Registro de Resultados", "Clasificación", "Premios"]
    )

    if menu == "Inicio":
        show_home()
    elif menu == "Registro de Jugadores":
        register_players()
    elif menu == "Creación de Equipos":
        create_teams()
    elif menu == "Configuración del Torneo":
        setup_tournament()
    elif menu == "Programa de Partidos":
        show_schedule()
    elif menu == "Registro de Resultados":
        input_results()
    elif menu == "Clasificación":
        show_standings()
    elif menu == "Premios":
        show_prizes()

def load_existing_players() -> Tuple[List[Player], List[Player]]:
    """Carga los jugadores existentes de la base de datos"""
    try:
        # Cargar jugadores hombres
        male_data = supabase.table('players').select("*").eq('gender', 'M').execute()
        male_players = [
            Player(name=p['name'], ranking=p['ranking'], gender=p['gender'], id=p['id'])
            for p in male_data.data
        ]
        
        # Cargar jugadoras mujeres
        female_data = supabase.table('players').select("*").eq('gender', 'F').execute()
        female_players = [
            Player(name=p['name'], ranking=p['ranking'], gender=p['gender'], id=p['id'])
            for p in female_data.data
        ]
        
        return male_players, female_players
    except Exception as e:
        handle_db_error(e, "loading existing players")
        return [], []

def load_existing_teams(male_players: List[Player], female_players: List[Player]) -> List[Team]:
    """Carga los equipos existentes de la base de datos"""
    try:
        teams_data = supabase.table('teams').select("*").execute()
        teams = []
        
        for team_data in teams_data.data:
            # Encontrar los jugadores por sus IDs
            player1 = next((p for p in male_players if p.id == team_data['player1_id']), None)
            player2 = next((p for p in female_players if p.id == team_data['player2_id']), None)
            
            if player1 and player2:
                team = Team(player1=player1, player2=player2, id=team_data['id'])
                team.points = team_data.get('points', 0)
                team.matches_played = team_data.get('matches_played', 0)
                team.matches_won = team_data.get('matches_won', 0)
                teams.append(team)
        
        return teams
    except Exception as e:
        handle_db_error(e, "loading existing teams")
        return []

def load_existing_tournament() -> Optional[Tournament]:
    """Carga el último torneo existente de la base de datos"""
    try:
        # Obtener el último torneo
        tournament_data = supabase.table('tournaments').select("*").order('start_date', desc=True).limit(1).execute()
        
        if not tournament_data.data:
            return None
            
        tournament_info = tournament_data.data[0]
        
        # Cargar jugadores y equipos
        male_players, female_players = load_existing_players()
        teams = load_existing_teams(male_players, female_players)
        
        if not teams:
            return None
            
        # Crear instancia del torneo
        tournament = Tournament(
            name=tournament_info['name'],
            num_courts=tournament_info['number_of_courts'],
            id=tournament_info['id']
        )
        
        # Agregar equipos al torneo
        for team in teams:
            tournament.add_team(team)
            
        # Generar el horario de partidos
        start_datetime = datetime.fromisoformat(tournament_info['start_date'])
        tournament.generate_schedule(start_datetime)
            
        # Cargar partidos jugados
        try:
            matches_data = supabase.table('matches').select("*").not_.is_('winner_id', 'null').execute()
            
            for match_data in matches_data.data:
                team1 = next((t for t in teams if t.id == match_data['team1_id']), None)
                team2 = next((t for t in teams if t.id == match_data['team2_id']), None)
                
                if team1 and team2:
                    match = Match(team1=team1, team2=team2, court=match_data['court_number'] - 1, id=match_data['id'])
                    winner = team1 if match_data['winner_id'] == team1.id else team2
                    match.play_match(winner)
                    tournament.matches.append(match)
        except Exception as e:
            logger.warning(f"Could not load played matches: {str(e)}")
        
        return tournament
    except Exception as e:
        handle_db_error(e, "loading existing tournament")
        return None

def show_home():
    st.markdown(f"""
        <div class="header">
            <img src="{CLUB_LOGO}" alt="Club Logo">
            <h1>Torneo de Tenis Mixto - {CLUB_NAME}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        ## 🎾 Bienvenido al Sistema de Gestión de Torneos
        
        Este sistema te permite:
        - Generar equipos mixtos aleatorios
        - Programar partidos
        - Registrar resultados
        - Visualizar estadísticas
    """)
    
    # Verificar si hay un torneo existente
    tournament = load_existing_tournament()
    
    if tournament:
        st.session_state.tournament = tournament
        st.info("📢 Hay un torneo en curso. Puedes ver los detalles a continuación.")
        
        # Mostrar información del torneo
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Nombre del Torneo", tournament.name)
        with col2:
            st.metric("Número de Canchas", tournament.num_courts)
        
        # Cargar jugadores y equipos del torneo
        male_players = [p for p in tournament.teams if p.player1.gender == 'M']
        female_players = [p for p in tournament.teams if p.player1.gender == 'F']
        show_teams_and_stats(male_players, female_players, tournament.teams)
        
        # Mostrar estado del torneo
        st.subheader("Estado del Torneo")
        matches_played = sum(1 for m in tournament.matches if m.winner is not None)
        total_matches = len(tournament.matches)
        progress = matches_played / total_matches if total_matches > 0 else 0
        st.progress(progress)
        st.write(f"Partidos jugados: {matches_played} de {total_matches}")
        
    else:
        # Intentar cargar jugadores existentes
        male_players, female_players = load_existing_players()
        
        if not male_players or not female_players:
            # Si no hay jugadores, mostrar el botón para generar nuevos
            if st.button("Generar Nuevos Jugadores y Equipos"):
                try:
                    players = generate_players()
                    teams = create_mixed_teams(players[0], players[1])
                    st.session_state.players = players[0] + players[1]
                    st.session_state.teams = teams
                    st.success("¡Equipos mixtos generados exitosamente!")
                    show_teams_and_stats(players[0], players[1], teams)
                except Exception as e:
                    st.error(f"Error al generar jugadores y equipos: {str(e)}")
        else:
            # Si hay jugadores existentes, cargar los equipos y mostrar los datos
            teams = load_existing_teams(male_players, female_players)
            if teams:
                st.session_state.players = male_players + female_players
                st.session_state.teams = teams
                show_teams_and_stats(male_players, female_players, teams)
            else:
                st.warning("Se encontraron jugadores pero no equipos. Por favor, contacta al administrador.")

def show_teams_and_stats(male_players: List[Player], female_players: List[Player], teams: List[Team]):
    """Muestra los equipos y estadísticas"""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Jugadores Totales", len(male_players) + len(female_players))
    with col2:
        st.metric("Jugadores Masculinos", len(male_players))
    with col3:
        st.metric("Jugadoras Femeninas", len(female_players))
    
    # Mostrar equipos en una tabla
    teams_data = []
    for team in teams:
        teams_data.append({
            "Equipo": team.name,
            "Jugador 1": f"{team.player1.name} ({team.player1.gender})",
            "Ranking 1": team.player1.ranking,
            "Jugador 2": f"{team.player2.name} ({team.player2.gender})",
            "Ranking 2": team.player2.ranking,
            "Ranking Promedio": team.average_ranking
        })
    
    df = pd.DataFrame(teams_data)
    st.dataframe(df, use_container_width=True)
    
    # Mostrar estadísticas
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="team-card">', unsafe_allow_html=True)
        st.subheader("Estadísticas de Rankings por Género")
        
        # Calcular promedios solo si hay jugadores
        if male_players:
            avg_male_ranking = sum(p.ranking for p in male_players) / len(male_players)
            st.write(f"👨 Ranking promedio hombres (1-20): {avg_male_ranking:.1f}")
            
            st.write("\n**Mejores Hombres:**")
            for p in sorted(male_players, key=lambda x: x.ranking)[:3]:
                st.write(f"👨 {p.name} (Ranking: {p.ranking})")
        
        if female_players:
            avg_female_ranking = sum(p.ranking for p in female_players) / len(female_players)
            st.write(f"👩 Ranking promedio mujeres (21-40): {avg_female_ranking:.1f}")
            
            st.write("\n**Mejores Mujeres:**")
            for p in sorted(female_players, key=lambda x: x.ranking)[:3]:
                st.write(f"👩 {p.name} (Ranking: {p.ranking})")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="team-card">', unsafe_allow_html=True)
        st.subheader("Distribución de Equipos")
        
        if teams:
            team_rankings = [team.average_ranking for team in teams]
            avg_team_ranking = sum(team_rankings) / len(team_rankings)
            st.write(f"Ranking promedio de equipos: {avg_team_ranking:.1f}")
            
            st.write("\n**Mejores Equipos Mixtos:**")
            for i, team in enumerate(sorted(teams, key=lambda x: x.average_ranking)[:3]):
                st.write(f"{i+1}. 👨 {team.player1.name} & 👩 {team.player2.name} (Ranking: {team.average_ranking:.1f})")
            
            st.write("\n**Equipos Mixtos Más Equilibrados:**")
            balanced_teams = sorted(teams, 
                                  key=lambda x: abs(x.player1.ranking - x.player2.ranking))[:3]
            for i, team in enumerate(balanced_teams):
                diff = abs(team.player1.ranking - team.player2.ranking)
                st.write(f"{i+1}. 👨 {team.player1.name} & 👩 {team.player2.name} (Diferencia: {diff})")
        else:
            st.warning("No hay equipos disponibles para mostrar estadísticas.")
        st.markdown('</div>', unsafe_allow_html=True)

def register_players():
    st.header("👥 Registro de Jugadores")
    
    # Intentar cargar jugadores existentes
    male_players, female_players = load_existing_players()
    
    if not male_players and not female_players:
        st.info("No hay jugadores registrados. Los jugadores se generan automáticamente al hacer clic en 'Generar Jugadores y Equipos' en la pantalla de Inicio.")
        return
    
    # Mostrar jugadores hombres
    st.subheader("Jugadores Hombres")
    if male_players:
        male_data = []
        for player in sorted(male_players, key=lambda x: x.ranking):
            male_data.append({
                "Nombre": f"👨 {player.name}",
                "Ranking": player.ranking
            })
        
        st.dataframe(pd.DataFrame(male_data), use_container_width=True)
    else:
        st.warning("No hay jugadores hombres registrados")
    
    # Mostrar jugadoras mujeres
    st.subheader("Jugadoras Mujeres")
    if female_players:
        female_data = []
        for player in sorted(female_players, key=lambda x: x.ranking):
            female_data.append({
                "Nombre": f"👩 {player.name}",
                "Ranking": player.ranking
            })
        
        st.dataframe(pd.DataFrame(female_data), use_container_width=True)
    else:
        st.warning("No hay jugadoras mujeres registradas")
    
    # Mostrar estadísticas
    st.markdown('<div class="team-card">', unsafe_allow_html=True)
    st.subheader("Estadísticas Generales")
    col1, col2 = st.columns(2)
    with col1:
        if male_players:
            avg_male_ranking = sum(p.ranking for p in male_players) / len(male_players)
            st.write(f"👨 Ranking promedio hombres: {avg_male_ranking:.1f}")
            st.write(f"Mejor ranking: {min(p.ranking for p in male_players)}")
            st.write(f"Peor ranking: {max(p.ranking for p in male_players)}")
        else:
            st.write("👨 No hay datos de jugadores hombres")
    
    with col2:
        if female_players:
            avg_female_ranking = sum(p.ranking for p in female_players) / len(female_players)
            st.write(f"👩 Ranking promedio mujeres: {avg_female_ranking:.1f}")
            st.write(f"Mejor ranking: {min(p.ranking for p in female_players)}")
            st.write(f"Peor ranking: {max(p.ranking for p in female_players)}")
        else:
            st.write("👩 No hay datos de jugadoras mujeres")
    st.markdown('</div>', unsafe_allow_html=True)

def create_teams():
    st.header("🤝 Creación de Equipos")
    
    # Intentar cargar jugadores y equipos existentes
    male_players, female_players = load_existing_players()
    teams = load_existing_teams(male_players, female_players)
    
    if not teams:
        st.info("No hay equipos registrados. Los equipos se generan automáticamente al hacer clic en 'Generar Jugadores y Equipos' en la pantalla de Inicio.")
        return
    
    # Mostrar todos los equipos
    teams_data = []
    for i, team in enumerate(teams):
        male_player = team.player1 if team.player1.gender == 'M' else team.player2
        female_player = team.player2 if team.player1.gender == 'M' else team.player1
        
        teams_data.append({
            "Equipo": i + 1,
            "Jugador 1": f"👨 {male_player.name}",
            "Ranking 1": male_player.ranking,
            "Jugador 2": f"👩 {female_player.name}",
            "Ranking 2": female_player.ranking,
            "Ranking Promedio": team.average_ranking
        })
    
    st.dataframe(pd.DataFrame(teams_data), use_container_width=True)
    
    # Mostrar estadísticas de equipos
    st.markdown('<div class="team-card">', unsafe_allow_html=True)
    st.subheader("Estadísticas de Equipos")
    
    # Mejores equipos
    st.write("**Mejores Equipos (por ranking promedio):**")
    for i, team in enumerate(sorted(teams, key=lambda x: x.average_ranking)[:3]):
        male_player = team.player1 if team.player1.gender == 'M' else team.player2
        female_player = team.player2 if team.player1.gender == 'M' else team.player1
        st.write(f"{i+1}. 👨 {male_player.name} & 👩 {female_player.name} (Ranking: {team.average_ranking:.1f})")
    
    # Equipos más equilibrados
    st.write("\n**Equipos Más Equilibrados:**")
    balanced_teams = sorted(teams, 
                          key=lambda x: abs(x.player1.ranking - x.player2.ranking))[:3]
    for i, team in enumerate(balanced_teams):
        male_player = team.player1 if team.player1.gender == 'M' else team.player2
        female_player = team.player2 if team.player1.gender == 'M' else team.player1
        diff = abs(male_player.ranking - female_player.ranking)
        st.write(f"{i+1}. 👨 {male_player.name} & 👩 {female_player.name} (Diferencia: {diff})")
    
    # Distribución de rankings
    team_rankings = [team.average_ranking for team in teams]
    st.write(f"\n**Ranking promedio de todos los equipos:** {sum(team_rankings) / len(team_rankings):.1f}")
    st.write(f"**Equipo más fuerte:** {min(team_rankings):.1f}")
    st.write(f"**Equipo más débil:** {max(team_rankings):.1f}")
    st.markdown('</div>', unsafe_allow_html=True)

def setup_tournament():
    st.header("⚙️ Configuración del Torneo")
    
    # Cargar equipos existentes
    male_players, female_players = load_existing_players()
    teams = load_existing_teams(male_players, female_players)
    
    # Cargar torneo existente
    tournament = load_existing_tournament()
    
    if tournament:
        st.info("📢 Ya existe un torneo activo. No se puede crear uno nuevo mientras haya un torneo en curso.")
        st.metric("Nombre del Torneo", tournament.name)
        st.metric("Número de Canchas", tournament.num_courts)
        return
    
    if not teams:
        st.warning("Primero debes crear los equipos")
        return
    
    with st.form("tournament_form"):
        name = st.text_input("Nombre del torneo")
        num_courts = st.number_input("Número de canchas disponibles", min_value=1, max_value=8, value=8)
        start_time = st.time_input("Hora de inicio")
        
        if st.form_submit_button("Configurar Torneo"):
            try:
                start_datetime = datetime.now().replace(
                    hour=start_time.hour,
                    minute=start_time.minute,
                    second=0,
                    microsecond=0
                )
                
                # Save tournament to Supabase
                data = supabase.table('tournaments').insert({
                    "name": name,
                    "number_of_courts": num_courts,
                    "start_date": start_datetime.isoformat(),
                    "end_date": None
                }).execute()
                tournament_id = data.data[0]['id']
                
                # Crear instancia del torneo
                tournament = Tournament(
                    name=name,
                    num_courts=num_courts,
                    id=tournament_id
                )
                
                # Agregar equipos al torneo
                for team in teams:
                    tournament.add_team(team)
                
                # Generar el programa de partidos
                tournament.generate_schedule(start_datetime)
                
                # Guardar el torneo en el estado de la sesión
                st.session_state.tournament = tournament
                
                st.success("✅ Torneo configurado exitosamente!")
                
            except Exception as e:
                handle_db_error(e, "setting up tournament")
                st.error("No se pudo configurar el torneo. Por favor, intenta nuevamente.")

def draw_tennis_court(court_number):
    """Dibuja una cancha de tenis con el número de cancha como marca de agua"""
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Color de la cancha (polvo de ladrillo)
    court_color = '#D2691E'
    
    # Dibujar la cancha
    court = patches.Rectangle((0, 0), 10, 5, facecolor=court_color, edgecolor='white', linewidth=2)
    ax.add_patch(court)
    
    # Líneas de la cancha
    # Línea central
    ax.plot([5, 5], [0, 5], color='white', linewidth=2)
    # Líneas de servicio
    ax.plot([0, 10], [1.25, 1.25], color='white', linewidth=2)
    ax.plot([0, 10], [3.75, 3.75], color='white', linewidth=2)
    # Líneas laterales
    ax.plot([0, 0], [0, 5], color='white', linewidth=2)
    ax.plot([10, 10], [0, 5], color='white', linewidth=2)
    
    # Número de cancha como marca de agua
    ax.text(5, 2.5, f"Cancha {court_number}", 
            fontsize=20, color='white', alpha=0.2,
            ha='center', va='center')
    
    # Configurar el aspecto
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')
    
    return fig

def show_schedule():
    st.header("📅 Programa de Partidos")
    
    # Cargar el último torneo
    tournament = load_existing_tournament()
    
    if not tournament:
        st.warning("No hay torneos activos. Por favor, configura un torneo primero.")
        return
    
    # Mostrar información del torneo
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Nombre del Torneo", tournament.name)
    with col2:
        st.metric("Número de Canchas", tournament.num_courts)
    
    # Cargar la imagen de la cancha
    court_img = Image.open('static/images/tennis_court.png')
    
    # Verificar si hay partidos programados
    if not tournament.schedule:
        st.warning("No hay partidos programados para este torneo.")
        return
    
    # Organizar partidos por ronda
    for time, matches in sorted(tournament.schedule.items()):
        st.subheader(f"Ronda {time.strftime('%H:%M')}")
        
        # Crear columnas para las canchas
        num_columns = min(2, tournament.num_courts)  # Máximo 2 canchas por fila
        cols = st.columns(num_columns)
        
        # Mostrar partidos de esta ronda
        for i, match in enumerate(matches):
            col = cols[i % num_columns]
            
            with col:
                # Verificar si el partido ya fue jugado
                played_match = next((m for m in tournament.matches if m.id == match.id), None)
                
                # Crear un contenedor para la cancha con el número y nombres superpuestos
                st.markdown(f"""
                <div style="position: relative; width: 100%;">
                    <img src="data:image/png;base64,{get_base64_image(court_img)}" style="width: 100%; border-radius: 10px;">
                    <div style="position: absolute; top: 20%; left: 50%; transform: translate(-50%, -50%); 
                               font-size: 72px; color: white; font-weight: bold; 
                               text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">
                        {match.court + 1}
                    </div>
                    <div style="position: absolute; top: 50%; left: 20%; transform: translate(-50%, -50%); 
                               font-size: 23px; color: white; font-weight: bold; 
                               text-shadow: 1px 1px 2px rgba(0,0,0,0.8); text-align: right;">
                        <div style="display: flex; align-items: center; justify-content: flex-end; margin-bottom: 5px;">
                            <span style="font-size: 1.1em; margin-right: 5px;">👨</span>
                            <span>{match.team1.player1.name}</span>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: flex-end;">
                            <span style="font-size: 1.1em; margin-right: 5px;">👩</span>
                            <span>{match.team1.player2.name}</span>
                        </div>
                    </div>
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                               font-size: 24px; color: white; font-weight: bold; 
                               text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">
                        VS
                    </div>
                    <div style="position: absolute; top: 50%; left: 80%; transform: translate(-50%, -50%); 
                               font-size: 23px; color: white; font-weight: bold; 
                               text-shadow: 1px 1px 2px rgba(0,0,0,0.8); text-align: left;">
                        <div style="display: flex; align-items: center; margin-bottom: 5px;">
                            <span style="font-size: 1.1em; margin-right: 5px;">👨</span>
                            <span>{match.team2.player1.name}</span>
                        </div>
                        <div style="display: flex; align-items: center;">
                            <span style="font-size: 1.1em; margin-right: 5px;">👩</span>
                            <span>{match.team2.player2.name}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar información adicional
                st.markdown(f"""
                <div style="background-color: rgba(0,0,0,0.7); color: white; padding: 10px; border-radius: 5px; margin-top: 10px;">
                    <p style="margin: 0;"><strong>Diferencia de Ranking:</strong> {abs(match.team1.average_ranking - match.team2.average_ranking):.1f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar resultado si el partido ya fue jugado
                if played_match and played_match.winner:
                    winner_name = f"👨 {played_match.winner.player1.name} & 👩 {played_match.winner.player2.name}"
                    st.success(f"✅ Ganador: {winner_name}")
                    st.write(f"Puntos obtenidos: {played_match.score:.1f}")
                else:
                    st.info("⏳ Partido pendiente")
                
                # Espacio entre partidos
                st.markdown("---")

def get_base64_image(img):
    """Convierte una imagen PIL a base64 para mostrarla en HTML"""
    import base64
    from io import BytesIO
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def input_results():
    st.header("📝 Registro de Resultados")
    
    if not st.session_state.tournament:
        st.warning("Primero debes configurar el torneo")
        return
    
    for round_num, (time, matches) in enumerate(st.session_state.tournament.schedule.items()):
        with st.expander(f"Ronda {round_num + 1} - {time.strftime('%H:%M')}"):
            for match in matches:
                st.markdown('<div class="team-card">', unsafe_allow_html=True)
                st.subheader(f"Cancha {match.court + 1}")
                
                # Mostrar los equipos
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    ### 👨 {match.team1.player1.name} & 👩 {match.team1.player2.name}
                    **Ranking promedio:** {match.team1.average_ranking:.1f}
                    """)
                with col2:
                    st.markdown(f"""
                    ### 👨 {match.team2.player1.name} & 👩 {match.team2.player2.name}
                    **Ranking promedio:** {match.team2.average_ranking:.1f}
                    """)
                
                # Input para el resultado
                st.markdown("---")
                st.subheader("Resultado del Partido")
                
                # Selección del ganador
                winner = st.radio(
                    "Equipo Ganador",
                    [
                        f"👨 {match.team1.player1.name} & 👩 {match.team1.player2.name}",
                        f"👨 {match.team2.player1.name} & 👩 {match.team2.player2.name}"
                    ],
                    key=f"winner_{round_num}_{match.court}"
                )
                
                # Input para los games
                col1, col2 = st.columns(2)
                with col1:
                    games_team1 = st.number_input(
                        "Games del Equipo 1",
                        min_value=0,
                        max_value=6,
                        value=0,
                        key=f"games_team1_{round_num}_{match.court}"
                    )
                with col2:
                    games_team2 = st.number_input(
                        "Games del Equipo 2",
                        min_value=0,
                        max_value=6,
                        value=0,
                        key=f"games_team2_{round_num}_{match.court}"
                    )
                
                # Validación del resultado
                if games_team1 > 0 or games_team2 > 0:
                    if abs(games_team1 - games_team2) < 2:
                        st.error("❌ La diferencia debe ser de al menos 2 games")
                    elif max(games_team1, games_team2) < 6:
                        st.error("❌ El ganador debe tener al menos 6 games")
                    else:
                        # Registrar el resultado
                        if st.button("Registrar Resultado", key=f"register_{round_num}_{match.court}"):
                            try:
                                winning_team = match.team1 if winner.startswith(match.team1.player1.name) else match.team2
                                
                                # Save match result to Supabase
                                data = supabase.table('matches').insert({
                                    "round_number": round_num + 1,
                                    "court_number": match.court + 1,
                                    "team1_id": match.team1.id,
                                    "team2_id": match.team2.id,
                                    "start_time": time.isoformat(),
                                    "winner_id": winning_team.id,
                                    "score_team1": games_team1,
                                    "score_team2": games_team2
                                }).execute()
                                
                                match.play_match(winning_team)
                                
                                # Calcular puntos bonus por diferencia de games
                                games_diff = abs(games_team1 - games_team2)
                                if games_diff >= 4:
                                    match.score += 0.5  # Bonus por victoria contundente
                                
                                st.success(f"""
                                ✅ Resultado registrado:
                                - Ganador: {winner}
                                - Resultado: {max(games_team1, games_team2)}-{min(games_team1, games_team2)}
                                - Puntos obtenidos: {match.score:.2f}
                                """)
                                
                            except Exception as e:
                                handle_db_error(e, "saving match result")
                                st.error("❌ No se pudo guardar el resultado. Por favor, intenta nuevamente.")
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")

def show_standings():
    st.header("🏆 Clasificación")
    
    if not st.session_state.tournament:
        st.warning("Primero debes configurar el torneo")
        return
    
    standings = st.session_state.tournament.get_standings()
    
    # Gráfico de barras de puntos
    fig = px.bar(
        standings,
        x='Team',
        y='Points',
        title='Puntos por Equipo',
        color='Points',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de clasificación
    st.dataframe(
        standings.style.background_gradient(cmap='YlOrRd'),
        use_container_width=True
    )

def show_prizes():
    st.header("🏅 Premios")
    
    if not st.session_state.tournament:
        st.warning("Primero debes configurar el torneo")
        return
    
    prizes = st.session_state.tournament.get_prizes()
    
    # Premios principales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        ### 🥇 Campeón
        """)
        st.success(f"**{prizes['Champion'][0]}**")
    
    with col2:
        st.markdown("""
        ### 🥈 Subcampeón
        """)
        st.info(f"**{prizes['Runner-up'][0]}**")
    
    with col3:
        st.markdown("""
        ### 🥉 Tercer Lugar
        """)
        st.warning(f"**{prizes['Third Place'][0]}**")
    
    # Premios especiales
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 🌟 Mejor Equipo de Menor Ranking
        """)
        st.success(f"**{prizes['Most Improved'][0]}**")
    
    with col2:
        st.markdown("""
        ### ⭐ Mejor Revelación
        """)
        st.success(f"**{prizes['Best Underdog'][0]}**")

if __name__ == "__main__":
    main() 