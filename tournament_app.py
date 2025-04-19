import streamlit as st
import pandas as pd
import plotly.express as px
from tournament import Player, Team, Tournament
from datetime import datetime
import random
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Torneo de Dobles - Club San Martín",
    page_icon="🎾",
    layout="wide"
)

# Cargar el logo
logo = Image.open('static/images/logo.png')

# Estilos CSS personalizados con los colores del Club San Martín
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #1a3e72;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2a4e82;
    }
    .header {
        color: #1a3e72;
        text-align: center;
        padding: 20px;
    }
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #e0e0e0;
    }
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stMarkdown h1 {
        color: #1a3e72;
        text-align: center;
    }
    .stMarkdown h2 {
        color: #1a3e72;
    }
    .stMarkdown h3 {
        color: #1a3e72;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-message {
        background-color: #cce5ff;
        color: #004085;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
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

def generate_players():
    """Genera un conjunto predefinido de 40 jugadores (20 hombres y 20 mujeres) con rankings aleatorios"""
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
        male_players.append(Player(name, ranking))
    
    # Crear jugadoras mujeres
    female_players = []
    for name, ranking in zip(female_names, female_rankings):
        female_players.append(Player(name, ranking))
    
    return male_players, female_players

def create_mixed_teams(male_players, female_players):
    """Crea 20 parejas mixtas (un hombre y una mujer)"""
    if len(male_players) != len(female_players):
        raise ValueError("Debe haber el mismo número de jugadores hombres y mujeres")
    
    # Mezclar los jugadores de cada género
    random.shuffle(male_players)
    random.shuffle(female_players)
    
    # Crear equipos mixtos
    teams = []
    for male, female in zip(male_players, female_players):
        team = Team(male, female)
        teams.append(team)
    
    return teams

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

def show_home():
    # Mostrar el logo y el título
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(logo, width=200)
    
    st.markdown("""
    ## 🎾 Torneo de Dobles Mixtos - Club San Martín
    
    Este sistema te ayudará a organizar y gestionar el torneo de dobles mixtos en formato americano del Club San Martín.
    
    ### Características principales:
    - 20 parejas mixtas (20 hombres y 20 mujeres)
    - **Formato obligatorio: 1 hombre + 1 mujer por equipo**
    - Rankings separados por género (hombres 1-20, mujeres 21-40)
    - Generación automática de equipos mixtos
    - Sistema de puntuación con bonificaciones
    - Seguimiento de resultados en tiempo real
    - Premios especiales y creativos
    
    ### Cómo usar:
    1. Haz clic en "Generar Jugadores y Equipos" para comenzar
    2. Configura el torneo
    3. Sigue el programa de partidos
    4. Registra los resultados
    5. Consulta la clasificación
    6. Descubre los premios finales
    """)
    
    if st.button("Generar Jugadores y Equipos"):
        try:
            # Generar jugadores separados por género
            male_players, female_players = generate_players()
            st.session_state.players = male_players + female_players
            
            # Crear equipos mixtos
            st.session_state.teams = create_mixed_teams(male_players, female_players)
            
            # Mostrar los equipos generados
            st.markdown('<div class="success-message">¡Jugadores y equipos mixtos generados exitosamente!</div>', unsafe_allow_html=True)
            
            # Mostrar los equipos en una tabla
            teams_data = []
            for i, team in enumerate(st.session_state.teams):
                male_player = team.players[0]
                female_player = team.players[1]
                
                teams_data.append({
                    "Equipo": i + 1,
                    "Jugador": f"👨 {male_player.name}",
                    "Ranking Jugador": male_player.ranking,
                    "Jugadora": f"👩 {female_player.name}",
                    "Ranking Jugadora": female_player.ranking,
                    "Ranking Promedio": f"{team.ranking:.1f}"
                })
            
            df = pd.DataFrame(teams_data)
            st.dataframe(df, use_container_width=True)
            
            # Mostrar estadísticas
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Estadísticas de Rankings por Género")
                avg_male_ranking = sum(p.ranking for p in male_players) / len(male_players)
                avg_female_ranking = sum(p.ranking for p in female_players) / len(female_players)
                st.write(f"👨 Ranking promedio hombres (1-20): {avg_male_ranking:.1f}")
                st.write(f"👩 Ranking promedio mujeres (21-40): {avg_female_ranking:.1f}")
                
                st.write("\n**Mejores Hombres:**")
                for p in sorted(male_players, key=lambda x: x.ranking)[:3]:
                    st.write(f"👨 {p.name} (Ranking: {p.ranking})")
                
                st.write("\n**Mejores Mujeres:**")
                for p in sorted(female_players, key=lambda x: x.ranking)[:3]:
                    st.write(f"👩 {p.name} (Ranking: {p.ranking})")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Distribución de Equipos")
                team_rankings = [team.ranking for team in st.session_state.teams]
                avg_team_ranking = sum(team_rankings) / len(team_rankings)
                st.write(f"Ranking promedio de equipos: {avg_team_ranking:.1f}")
                
                st.write("\n**Mejores Equipos Mixtos:**")
                for i, team in enumerate(sorted(st.session_state.teams, key=lambda x: x.ranking)[:3]):
                    st.write(f"{i+1}. 👨 {team.players[0].name} & 👩 {team.players[1].name} (Ranking: {team.ranking:.1f})")
                
                st.write("\n**Equipos Mixtos Más Equilibrados:**")
                balanced_teams = sorted(st.session_state.teams, 
                                      key=lambda x: abs(x.players[0].ranking - x.players[1].ranking))[:3]
                for i, team in enumerate(balanced_teams):
                    diff = abs(team.players[0].ranking - team.players[1].ranking)
                    st.write(f"{i+1}. 👨 {team.players[0].name} & 👩 {team.players[1].name} (Diferencia: {diff})")
                st.markdown('</div>', unsafe_allow_html=True)
        
        except ValueError as e:
            st.error(str(e))
            st.markdown('<div class="info-message">Por favor, asegúrate de que haya el mismo número de jugadores hombres y mujeres.</div>', unsafe_allow_html=True)

def register_players():
    st.header("👥 Registro de Jugadores")
    
    if not st.session_state.players:
        st.info("Los jugadores se generan automáticamente al hacer clic en 'Generar Jugadores y Equipos' en la pantalla de Inicio.")
        return
    
    # Mostrar jugadores hombres
    st.subheader("Jugadores Hombres")
    male_players = [p for p in st.session_state.players if p.name in [
        "Juan", "Carlos", "Pedro", "Miguel", "David", "Jorge", "Pablo", "Antonio",
        "Fernando", "Javier", "Manuel", "José", "Francisco", "Ángel", "Alberto", "Sergio",
        "Diego", "Raúl", "Rubén", "Adrián"
    ]]
    
    male_data = []
    for player in sorted(male_players, key=lambda x: x.ranking):
        male_data.append({
            "Nombre": f"👨 {player.name}",
            "Ranking": player.ranking
        })
    
    st.dataframe(pd.DataFrame(male_data), use_container_width=True)
    
    # Mostrar jugadoras mujeres
    st.subheader("Jugadoras Mujeres")
    female_players = [p for p in st.session_state.players if p.name in [
        "María", "Ana", "Laura", "Sofía", "Elena", "Marta", "Lucía", "Isabel",
        "Carmen", "Rosa", "Teresa", "Patricia", "Silvia", "Cristina", "Nuria", "Marina",
        "Beatriz", "Victoria", "Claudia", "Natalia"
    ]]
    
    female_data = []
    for player in sorted(female_players, key=lambda x: x.ranking):
        female_data.append({
            "Nombre": f"👩 {player.name}",
            "Ranking": player.ranking
        })
    
    st.dataframe(pd.DataFrame(female_data), use_container_width=True)
    
    # Mostrar estadísticas
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Estadísticas Generales")
    col1, col2 = st.columns(2)
    with col1:
        avg_male_ranking = sum(p.ranking for p in male_players) / len(male_players)
        st.write(f"👨 Ranking promedio hombres: {avg_male_ranking:.1f}")
        st.write(f"Mejor ranking: {min(p.ranking for p in male_players)}")
        st.write(f"Peor ranking: {max(p.ranking for p in male_players)}")
    
    with col2:
        avg_female_ranking = sum(p.ranking for p in female_players) / len(female_players)
        st.write(f"👩 Ranking promedio mujeres: {avg_female_ranking:.1f}")
        st.write(f"Mejor ranking: {min(p.ranking for p in female_players)}")
        st.write(f"Peor ranking: {max(p.ranking for p in female_players)}")
    st.markdown('</div>', unsafe_allow_html=True)

def create_teams():
    st.header("🤝 Creación de Equipos")
    
    if not st.session_state.teams:
        st.info("Los equipos se generan automáticamente al hacer clic en 'Generar Jugadores y Equipos' en la pantalla de Inicio.")
        return
    
    # Mostrar todos los equipos
    teams_data = []
    for i, team in enumerate(st.session_state.teams):
        male_player = team.players[0]
        female_player = team.players[1]
        
        teams_data.append({
            "Equipo": i + 1,
            "Jugador": f"👨 {male_player.name}",
            "Ranking Jugador": male_player.ranking,
            "Jugadora": f"👩 {female_player.name}",
            "Ranking Jugadora": female_player.ranking,
            "Ranking Promedio": f"{team.ranking:.1f}"
        })
    
    st.dataframe(pd.DataFrame(teams_data), use_container_width=True)
    
    # Mostrar estadísticas de equipos
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Estadísticas de Equipos")
    
    # Mejores equipos
    st.write("**Mejores Equipos (por ranking promedio):**")
    for i, team in enumerate(sorted(st.session_state.teams, key=lambda x: x.ranking)[:3]):
        st.write(f"{i+1}. 👨 {team.players[0].name} & 👩 {team.players[1].name} (Ranking: {team.ranking:.1f})")
    
    # Equipos más equilibrados
    st.write("\n**Equipos Más Equilibrados:**")
    balanced_teams = sorted(st.session_state.teams, 
                          key=lambda x: abs(x.players[0].ranking - x.players[1].ranking))[:3]
    for i, team in enumerate(balanced_teams):
        diff = abs(team.players[0].ranking - team.players[1].ranking)
        st.write(f"{i+1}. 👨 {team.players[0].name} & 👩 {team.players[1].name} (Diferencia: {diff})")
    
    # Distribución de rankings
    team_rankings = [team.ranking for team in st.session_state.teams]
    st.write(f"\n**Ranking promedio de todos los equipos:** {sum(team_rankings) / len(team_rankings):.1f}")
    st.write(f"**Equipo más fuerte:** {min(team_rankings):.1f}")
    st.write(f"**Equipo más débil:** {max(team_rankings):.1f}")
    st.markdown('</div>', unsafe_allow_html=True)

def setup_tournament():
    st.header("⚙️ Configuración del Torneo")
    
    if not st.session_state.teams:
        st.warning("Primero debes crear los equipos")
        return
    
    with st.form("tournament_form"):
        name = st.text_input("Nombre del torneo")
        num_courts = st.number_input("Número de canchas disponibles", min_value=1, max_value=8, value=8)
        start_time = st.time_input("Hora de inicio")
        
        if st.form_submit_button("Configurar Torneo"):
            start_datetime = datetime.now().replace(
                hour=start_time.hour,
                minute=start_time.minute,
                second=0,
                microsecond=0
            )
            
            st.session_state.tournament = Tournament(name, num_courts)
            for team in st.session_state.teams:
                st.session_state.tournament.add_team(team)
            
            st.session_state.tournament.generate_schedule(start_datetime)
            st.success("¡Torneo configurado exitosamente!")

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
    
    if not st.session_state.tournament:
        st.warning("Primero debes configurar el torneo")
        return
    
    # Cargar la imagen de la cancha
    court_img = Image.open('static/images/tennis_court.png')
    
    for round_num, (time, matches) in enumerate(st.session_state.tournament.schedule.items()):
        with st.expander(f"Ronda {round_num + 1} - {time.strftime('%H:%M')}"):
            # Crear columnas para las canchas
            cols = st.columns(2)
            
            for i, match in enumerate(matches):
                # Determinar en qué columna mostrar la cancha
                col = cols[i % 2]
                
                with col:
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
                                <span>{match.team1.players[0].name}</span>
                            </div>
                            <div style="display: flex; align-items: center; justify-content: flex-end;">
                                <span style="font-size: 1.1em; margin-right: 5px;">👩</span>
                                <span>{match.team1.players[1].name}</span>
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
                                <span>{match.team2.players[0].name}</span>
                            </div>
                            <div style="display: flex; align-items: center;">
                                <span style="font-size: 1.1em; margin-right: 5px;">👩</span>
                                <span>{match.team2.players[1].name}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Mostrar información adicional
                    st.markdown(f"""
                    <div style="background-color: rgba(0,0,0,0.7); color: white; padding: 10px; border-radius: 5px; margin-top: 10px;">
                        <p style="margin: 0;"><strong>Diferencia de Ranking:</strong> {abs(match.team1.ranking - match.team2.ranking):.1f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Espacio entre canchas
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
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader(f"Cancha {match.court + 1}")
                
                # Mostrar los equipos
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    ### 👨 {match.team1.players[0].name} & 👩 {match.team1.players[1].name}
                    **Ranking promedio:** {match.team1.ranking:.1f}
                    """)
                with col2:
                    st.markdown(f"""
                    ### 👨 {match.team2.players[0].name} & 👩 {match.team2.players[1].name}
                    **Ranking promedio:** {match.team2.ranking:.1f}
                    """)
                
                # Input para el resultado
                st.markdown("---")
                st.subheader("Resultado del Partido")
                
                # Selección del ganador
                winner = st.radio(
                    "Equipo Ganador",
                    [
                        f"👨 {match.team1.players[0].name} & 👩 {match.team1.players[1].name}",
                        f"👨 {match.team2.players[0].name} & 👩 {match.team2.players[1].name}"
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
                        st.error("La diferencia debe ser de al menos 2 games")
                    elif max(games_team1, games_team2) < 6:
                        st.error("El ganador debe tener al menos 6 games")
                    else:
                        # Registrar el resultado
                        if st.button("Registrar Resultado", key=f"register_{round_num}_{match.court}"):
                            winning_team = match.team1 if winner.startswith(match.team1.players[0].name) else match.team2
                            match.play_match(winning_team)
                            
                            # Calcular puntos bonus por diferencia de games
                            games_diff = abs(games_team1 - games_team2)
                            if games_diff >= 4:
                                match.score += 0.5  # Bonus por victoria contundente
                            
                            st.success(f"""
                            Resultado registrado:
                            - Ganador: {winner}
                            - Resultado: {max(games_team1, games_team2)}-{min(games_team1, games_team2)}
                            - Puntos obtenidos: {match.score:.2f}
                            """)
                
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