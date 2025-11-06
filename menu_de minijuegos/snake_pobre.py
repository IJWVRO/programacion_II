import pygame
import sys
import random
import os
import json
import re
from pygame.math import Vector2
import smtplib
from email.message import EmailMessage

# ----------------------------
# 1. CONFIGURACIÓN INICIAL
# ----------------------------

pygame.init()
pygame.mixer.init()

# --- Dimensiones ---
cell_size = 25
number_of_cells = 25
OFFSET = 60
ANCHO = 2 * OFFSET + cell_size * number_of_cells
ALTO = OFFSET + cell_size * number_of_cells + 80

# --- Colores ---
GREEN_LIGHT = (173, 204, 96)
GREEN_DARK = (167, 197, 85)
DARK_GREEN = (43, 51, 24)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (150, 150, 150)

# --- Fuentes ---
title_font = pygame.font.Font(None, 80)
menu_font = pygame.font.Font(None, 40)
score_font = pygame.font.Font(None, 32)
input_font = pygame.font.Font(None, 36)

# --- Estados del Juego (CAMBIOS RECIENTES) ---
MENU = "MENU"
RUNNING = "RUNNING"
GAME_OVER = "GAME_OVER"
LEADERBOARD = "LEADERBOARD"
USER_INPUT = "USER_INPUT"

# --- Variables Globales de Juego (CAMBIOS RECIENTES) ---
game_state = MENU
current_player_name = "Invitado"
current_player_email = ""
last_score = 0
leaderboard_page = 0

# --- Ventana ---
screen = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Retro Snake Plus")
clock = pygame.time.Clock()

# --- Rutas de Recursos ---
BASE_PATH = os.path.dirname(__file__)
def get_asset_path(folder, filename):
    return os.path.join(BASE_PATH, folder, filename)

try:
    food_surface = pygame.image.load(get_asset_path("graficos", "food.png"))
    eat_sound = pygame.mixer.Sound(get_asset_path("sonidos", "eat.mp3"))
    wall_hit_sound = pygame.mixer.Sound(get_asset_path("sonidos", "wall.mp3"))
    
    # --- Música de Fondo (CAMBIOS RECIENTES: Línea añadida) ---
    # pygame.mixer.music.load(get_asset_path("sonidos", "background_music.mp3"))
    # pygame.mixer.music.play(-1) # El -1 hace que se reproduzca en bucle
except pygame.error as e:
    print(f"Error al cargar un recurso: {e}")
    food_surface = pygame.Surface((cell_size, cell_size))
    food_surface.fill(RED)
    eat_sound = None
    wall_hit_sound = None


# ----------------------------
# 2. SISTEMA DE DATOS
# ----------------------------

import smtplib
from email.message import EmailMessage

def send_email(player_name, to_email, new_score):
    sender_email = "fairbotnotifier@gmail.com"  # Cambiar por tu email
    sender_password = "pvrcyhncquzcibyv"  # Generar en Gmail

    msg = EmailMessage()
    msg['Subject'] = f"Nuevo récord en Retro Snake Plus: {new_score}"
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content(f"¡Felicidades {player_name}! Has alcanzado un nuevo récord de {new_score} puntos en Retro Snake Plus.")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)


class DataManager:
    """Clase para manejar la carga y guardado de puntuaciones."""
    def __init__(self, filename="leaderboard_data.json"):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        """Carga la lista de jugadores desde el archivo JSON."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []

    def save_data(self):
        """Guarda la lista de jugadores en el archivo JSON."""
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)

    def update_score(self, name, email, score):
        """
        Actualiza el puntaje de un jugador existente o agrega uno nuevo,
        y envía email si hay un récord.
        """
        if not name or name == "Invitado": 
            return False, 0

        name = name.strip()
        
        for player in self.data:
            if player['name'].lower() == name.lower():
                old_score = player['score']
                if score > old_score:
                    player['score'] = score
                    self.data.sort(key=lambda x: x['score'], reverse=True)
                    self.save_data()

                    # ---- ENVÍO DE EMAIL ----
                    if email.strip():  # Solo si hay email
                        try:
                            send_email(name, email, score)
                        except Exception as e:
                            print(f"No se pudo enviar el email: {e}")
                    # -----------------------

                    return True, old_score
                return False, old_score
        
        # Si el usuario no existe, lo agrega
        new_player = {'name': name, 'email': email, 'score': score}
        self.data.append(new_player)
        self.data.sort(key=lambda x: x['score'], reverse=True)
        self.save_data()
        
        # ---- ENVÍO DE EMAIL ----
        if email.strip():  # Solo si hay email
            try:
                send_email(name, email, score)
            except Exception as e:
                print(f"No se pudo enviar el email: {e}")
        # -----------------------

        return False, 0

    def get_top_scores(self):
        """Retorna la lista ordenada de jugadores."""
        self.data.sort(key=lambda x: x['score'], reverse=True)
        return self.data


# ----------------------------
# 3. CLASES DEL JUEGO
# ----------------------------

class Food:
    """Maneja la posición y dibujo de la comida. (CAMBIOS RECIENTES: Múltiples posiciones)"""
    def __init__(self, snake_body, walls, num_foods=4):
        self.positions = [] # Lista para guardar las 4 posiciones de comida
        self.num_foods = num_foods
        self.generate_initial_pos(snake_body, walls)

    def draw(self):
        """Dibuja todas las comidas en sus respectivas posiciones."""
        for position in self.positions:
            food_rect = pygame.Rect(
                OFFSET + position.x * cell_size,
                OFFSET + position.y * cell_size,
                cell_size,
                cell_size
            )
            screen.blit(food_surface, food_rect)

    def generate_random_cell(self):
        x = random.randint(0, number_of_cells - 1)
        y = random.randint(0, number_of_cells - 1)
        return Vector2(x, y)

    def generate_initial_pos(self, snake_body, walls):
        """Genera las posiciones iniciales de las comidas."""
        self.positions = []
        
        # Convertir todos los obstáculos a tuplas para el set
        excluded_positions = set([(int(v.x), int(v.y)) for v in snake_body] + [(int(v.x), int(v.y)) for v in walls])
        
        for _ in range(self.num_foods):
            position = self.generate_random_cell()
            pos_tuple = (int(position.x), int(position.y))
            
            # Repetir si la posición ya está ocupada por la serpiente, un muro o por otra comida
            while pos_tuple in excluded_positions:
                position = self.generate_random_cell()
                pos_tuple = (int(position.x), int(position.y))
            
            self.positions.append(position)
            excluded_positions.add(pos_tuple) # Añade la nueva comida a los excluidos

    def regenerate_single_pos(self, snake_body, walls):
        """Genera una única nueva posición de comida (después de que una es comida)."""
        excluded_positions = set([(int(v.x), int(v.y)) for v in snake_body] + 
                                 [(int(v.x), int(v.y)) for v in walls] +
                                 [(int(v.x), int(v.y)) for v in self.positions]) # Excluye todas las comidas actuales
        
        position = self.generate_random_cell()
        pos_tuple = (int(position.x), int(position.y))
        
        while pos_tuple in excluded_positions:
            position = self.generate_random_cell()
            pos_tuple = (int(position.x), int(position.y))
            
        self.positions.append(position)



class Snake:
    """Maneja el cuerpo, movimiento, dirección y la restricción de movimiento. (CAMBIOS RECIENTES: can_change_direction)"""
    def __init__(self):
        self.body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        self.direction = Vector2(1, 0)
        self.add_segment = False
        self.eat_sound = eat_sound
        self.wall_hit_sound = wall_hit_sound
        self.can_change_direction = True # BANDERA CLAVE para la corrección de colisión instantánea

    def draw(self):
        """Dibuja cada segmento del cuerpo de la serpiente."""
        for index, segment in enumerate(self.body):
            segment_rect = (
                OFFSET + segment.x * cell_size,
                OFFSET + segment.y * cell_size,
                cell_size,
                cell_size
            )
            color = (50, 70, 50) if index == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, segment_rect, 0, 7)

    def update(self):
        """Mueve la serpiente y restablece la bandera de cambio de dirección."""
        self.body.insert(0, self.body[0] + self.direction)
        
        if not self.add_segment:
            self.body = self.body[:-1]
        else:
            self.add_segment = False
            
        self.can_change_direction = True # Se permite un nuevo cambio de dirección después de cada movimiento

    def change_direction(self, new_direction):
        """Cambia la dirección solo si la serpiente no va a girar 180 grados y si se permite el cambio."""
        if self.can_change_direction:
            # Comprueba si la nueva dirección es opuesta a la actual (para evitar el auto-choque)
            if new_direction != -self.direction:
                self.direction = new_direction
                self.can_change_direction = False # Evita otro cambio de dirección hasta el próximo update
                
    def reset(self):
        """Restablece la serpiente a su posición inicial."""
        self.body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        self.direction = Vector2(1, 0)
        self.can_change_direction = True


class Game:
    """Clase principal que coordina todos los elementos del juego."""
    def __init__(self):
        self.snake = Snake()
        
        # --- Muros y Velocidad ---
        self.max_walls = 8
        self.walls = self.generate_walls()
        self.food = Food(self.snake.body, self.walls)
        self.score = 0
        self.initial_speed_ms = 200
        self.current_speed_ms = self.initial_speed_ms

    def generate_walls(self):
        """Genera un conjunto de muros aleatorios."""
        # --- CAMBIOS RECIENTES (Corrección de TypeError) ---
        snake_body_tuples = [(int(v.x), int(v.y)) for v in self.snake.body]
        excluded_positions_tuples = set(snake_body_tuples)
        
        # Excluir un área alrededor del inicio para asegurar un inicio limpio
        for x, y in snake_body_tuples:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    excluded_positions_tuples.add((x + dx, y + dy))
        
        possible_positions = [Vector2(x, y) for x in range(number_of_cells) for y in range(number_of_cells)]
        
        available_positions = []
        for pos in possible_positions:
            pos_tuple = (int(pos.x), int(pos.y))
            if pos_tuple not in excluded_positions_tuples:
                available_positions.append(pos)

        if len(available_positions) >= self.max_walls:
            walls = random.sample(available_positions, self.max_walls)
        else:
            walls = available_positions
            
        return walls

    def draw(self):
        """Dibuja la comida, los muros y la serpiente."""
        self.draw_walls()
        self.food.draw()
        self.snake.draw()

    def draw_walls(self):
        """Dibuja los bloques de muro en el tablero."""
        for wall in self.walls:
            wall_rect = (
                OFFSET + wall.x * cell_size,
                OFFSET + wall.y * cell_size,
                cell_size,
                cell_size
            )
            pygame.draw.rect(screen, (70, 80, 70), wall_rect)
            
    def update(self):
        """Ejecuta un paso de juego (movimiento, colisiones)."""
        self.snake.update()
        self.check_collision_with_food()
        self.check_collision_with_edges()
        self.check_collision_with_tail()
        self.check_collision_with_walls()
        self.update_speed()

    def check_collision_with_food(self):
        """Verifica si la cabeza de la serpiente está en alguna de las 4 posiciones de comida. (CAMBIOS RECIENTES)"""
        head = self.snake.body[0]
        
        for index, position in enumerate(self.food.positions):
            if head == position:
                # 1. Elimina la comida que se comió
                self.food.positions.pop(index)
                
                # 2. Hace crecer la serpiente
                self.snake.add_segment = True
                
                # 3. Aumenta el score
                self.score += 1
                
                # 4. Reproduce sonido
                if self.snake.eat_sound:
                    self.snake.eat_sound.play()
                    
                # 5. Regenera la comida en una nueva posición
                self.food.regenerate_single_pos(self.snake.body, self.walls)
                
                # 6. Regenera muros cada 100 puntos
                if self.score > 0 and self.score % 100 == 0:
                    self.walls = self.generate_walls()
                    # Regenera TODAS las 4 comidas en nuevas posiciones seguras
                    self.food.generate_initial_pos(self.snake.body, self.walls)
                return # Termina la función después de encontrar la primera colisión

    def check_collision_with_edges(self):
        """Verifica colisión con los límites del tablero."""
        head = self.snake.body[0]
        if head.x >= number_of_cells or head.x < 0 or head.y >= number_of_cells or head.y < 0:
            self.game_over()

    def check_collision_with_tail(self):
        """Verifica colisión con el propio cuerpo."""
        headless_body = self.snake.body[1:]
        if self.snake.body[0] in headless_body:
            self.game_over()
            
    def check_collision_with_walls(self):
        """Verifica colisión con los muros generados."""
        if self.snake.body[0] in self.walls:
            self.game_over()
            
    def update_speed(self):
        """Aumenta la velocidad de la serpiente si el puntaje es alto."""
        speed_increase = (self.score // 250) * 20
        new_speed = self.initial_speed_ms - speed_increase
        
        if new_speed < 50:
            new_speed = 50
        
        if new_speed != self.current_speed_ms:
            self.current_speed_ms = new_speed
            pygame.time.set_timer(SNAKE_UPDATE, self.current_speed_ms)

    def game_over(self):
        """Maneja el fin del juego."""
        global game_state, last_score, current_player_name, current_player_email
        
        last_score = self.score
        data_manager.update_score(current_player_name, current_player_email, last_score)
        
        if self.snake.wall_hit_sound:
            self.snake.wall_hit_sound.play()

        self.snake.reset()
        self.walls = self.generate_walls()
        self.food.generate_initial_pos(self.snake.body, self.walls) # Regenera las 4 comidas
        self.score = 0
        game_state = GAME_OVER
        
        self.current_speed_ms = self.initial_speed_ms
        pygame.time.set_timer(SNAKE_UPDATE, self.current_speed_ms)


# ----------------------------
# 4. FUNCIONES DE DIBUJO DE INTERFAZ
# ----------------------------

class Button:
    """Clase simple para botones interactivos."""
    def __init__(self, text, rect, color, text_color=BLACK, font=menu_font):
        self.text = text
        self.rect = rect
        self.color = color
        self.text_color = text_color
        self.font = font

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, 0, 10)
        pygame.draw.rect(surface, DARK_GREEN, self.rect, 3, 10)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_menu():
    """Dibuja la pantalla del menú principal con los botones."""
    global boton_rects
    
    title_surface = title_font.render("RETRO SNAKE", True, DARK_GREEN)
    screen.blit(title_surface, title_surface.get_rect(center=(ANCHO // 2, ALTO // 4)))
    
    button_y_start = ALTO // 2 - 100
    button_height = 60
    button_width = 300
    spacing = 80
    
    buttons_data = [
        ("JUGAR", button_y_start),
        ("CLASIFICACIONES", button_y_start + spacing),
        ("USUARIO", button_y_start + 2 * spacing),
        ("SALIR DEL JUEGO", button_y_start + 3 * spacing)
    ]
    
    boton_rects = {}
    for text, y in buttons_data:
        rect = pygame.Rect(ANCHO // 2 - button_width // 2, y, button_width, button_height)
        button = Button(text, rect, GREEN_LIGHT, DARK_GREEN)
        button.draw(screen)
        boton_rects[text] = rect
        
    user_text = score_font.render(f"Jugador: {current_player_name}", True, DARK_GREEN)
    screen.blit(user_text, (OFFSET, ALTO - 50))
    
    return boton_rects

def draw_leaderboard():
    """Dibuja la tabla de clasificaciones con paginación."""
    global leaderboard_page, leaderboard_close_button, prev_page_button, next_page_button
    
    overlay = pygame.Surface((ANCHO, ALTO))
    overlay.set_alpha(200)
    overlay.fill(DARK_GREEN)
    screen.blit(overlay, (0, 0))

    title_text = title_font.render("CLASIFICACIONES", True, WHITE)
    screen.blit(title_text, title_text.get_rect(center=(ANCHO // 2, OFFSET)))

    close_rect = pygame.Rect(ANCHO - OFFSET, OFFSET // 2, 40, 40)
    pygame.draw.rect(screen, RED, close_rect, 0, 5)
    close_text = menu_font.render("X", True, WHITE)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))
    leaderboard_close_button = close_rect

    # --- Contenido de la Tabla ---
    scores_per_page = 10
    scores = data_manager.get_top_scores()
    num_pages = (len(scores) + scores_per_page - 1) // scores_per_page
    
    leaderboard_page = max(0, min(leaderboard_page, num_pages - 1))
    
    start_index = leaderboard_page * scores_per_page
    end_index = start_index + scores_per_page
    current_page_scores = scores[start_index:end_index]

    header = score_font.render("POS  | NOMBRE       | PUNTAJE", True, GREEN_LIGHT)
    screen.blit(header, (ANCHO // 2 - 150, OFFSET + 80))
    pygame.draw.line(screen, GREEN_LIGHT, (ANCHO // 2 - 150, OFFSET + 110), (ANCHO // 2 + 150, OFFSET + 110), 2)

    for i, player in enumerate(current_page_scores):
        pos = start_index + i + 1
        text_line = f"{pos:<3}  | {player['name'][:10]:<10} | {player['score']}"
        score_text = score_font.render(text_line, True, WHITE)
        screen.blit(score_text, (ANCHO // 2 - 150, OFFSET + 130 + i * 30))

    # --- Paginación ---
    page_text = score_font.render(f"Página {leaderboard_page + 1} de {num_pages if num_pages > 0 else 1}", True, WHITE)
    screen.blit(page_text, page_text.get_rect(center=(ANCHO // 2, ALTO - 60)))
    
    prev_page_button = Button("<-", pygame.Rect(ANCHO // 2 - 100, ALTO - 80, 40, 40), GRAY)
    next_page_button = Button("->", pygame.Rect(ANCHO // 2 + 60, ALTO - 80, 40, 40), GRAY)
    
    if leaderboard_page > 0: prev_page_button.draw(screen)
    if leaderboard_page < num_pages - 1 and num_pages > 1: next_page_button.draw(screen)

def draw_user_input():
    """Dibuja la pantalla para que el usuario ingrese Nombre y Email."""
    global user_input_close_button, name_input_rect, email_input_rect, submit_button_rect, active_input, name_text, email_text, input_error_text

    overlay = pygame.Surface((ANCHO, ALTO))
    overlay.set_alpha(200)
    overlay.fill(DARK_GREEN)
    screen.blit(overlay, (0, 0))

    title_text = title_font.render("CONFIGURAR USUARIO", True, WHITE)
    screen.blit(title_text, title_text.get_rect(center=(ANCHO // 2, OFFSET)))

    close_rect = pygame.Rect(ANCHO - OFFSET, OFFSET // 2, 40, 40)
    pygame.draw.rect(screen, RED, close_rect, 0, 5)
    close_text = menu_font.render("X", True, WHITE)
    screen.blit(close_text, close_text.get_rect(center=close_rect.center))
    user_input_close_button = close_rect
    
    # --- Input Name ---
    label_name = input_font.render("Nombre (único):", True, WHITE)
    screen.blit(label_name, (ANCHO // 2 - 150, ALTO // 3))
    
    name_input_rect = pygame.Rect(ANCHO // 2 - 150, ALTO // 3 + 30, 300, 40)
    color_name = GREEN_LIGHT if active_input == 'name' else WHITE
    pygame.draw.rect(screen, color_name, name_input_rect, 0, 5)
    
    name_surf = input_font.render(name_text, True, BLACK)
    screen.blit(name_surf, (name_input_rect.x + 5, name_input_rect.y + 5))

    # --- Input Email ---
    label_email = input_font.render("Email (para alertas):", True, WHITE)
    screen.blit(label_email, (ANCHO // 2 - 150, ALTO // 3 + 100))
    
    email_input_rect = pygame.Rect(ANCHO // 2 - 150, ALTO // 3 + 130, 300, 40)
    color_email = GREEN_LIGHT if active_input == 'email' else WHITE
    pygame.draw.rect(screen, color_email, email_input_rect, 0, 5)
    
    email_surf = input_font.render(email_text, True, BLACK)
    screen.blit(email_surf, (email_input_rect.x + 5, email_input_rect.y + 5))
    
    # --- Mensaje de Error ---
    if input_error_text:
        error_surf = score_font.render(input_error_text, True, RED)
        screen.blit(error_surf, error_surf.get_rect(center=(ANCHO // 2, ALTO // 3 + 190)))

    # --- Botón Guardar ---
    submit_button_rect = pygame.Rect(ANCHO // 2 - 75, ALTO - 150, 150, 50)
    submit_button = Button("GUARDAR", submit_button_rect, GREEN_LIGHT, DARK_GREEN)
    submit_button.draw(screen)

def draw_game_over():
    """Dibuja la pantalla de Game Over y los botones de navegación."""
    global game_over_rects
    
    overlay = pygame.Surface((ANCHO, ALTO))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    game_over_text = title_font.render("GAME OVER", True, RED)
    score_text = menu_font.render(f"Puntaje: {last_score}", True, WHITE)
    
    screen.blit(game_over_text, game_over_text.get_rect(center=(ANCHO // 2, ALTO // 3)))
    screen.blit(score_text, score_text.get_rect(center=(ANCHO // 2, ALTO // 3 + 80)))
    
    button_y_start = ALTO // 2 + 100
    button_width = 250
    spacing = 70
    
    boton_play_again = Button("Volver a Jugar", pygame.Rect(ANCHO // 2 - button_width // 2, button_y_start, button_width, 50), GREEN_LIGHT, DARK_GREEN)
    boton_menu = Button("Ir a Inicio", pygame.Rect(ANCHO // 2 - button_width // 2, button_y_start + spacing, button_width, 50), GRAY, DARK_GREEN)
    
    boton_play_again.draw(screen)
    boton_menu.draw(screen)

    game_over_rects = {
        "PLAY_AGAIN": boton_play_again.rect,
        "MENU": boton_menu.rect
    }

# ----------------------------
# 5. LÓGICA DE INPUT DE TEXTO
# ----------------------------

name_text = ""
email_text = ""
active_input = 'name'
name_input_rect = None
email_input_rect = None
submit_button_rect = None
input_error_text = ""

def handle_text_input(event):
    """Maneja las pulsaciones de teclado en el estado USER_INPUT."""
    global name_text, email_text, active_input, input_error_text
    
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
            if active_input == 'name':
                active_input = 'email'
            elif active_input == 'email':
                save_user_data()
        elif event.key == pygame.K_TAB:
            active_input = 'email' if active_input == 'name' else 'name'
        elif event.key == pygame.K_BACKSPACE:
            if active_input == 'name':
                name_text = name_text[:-1]
            elif active_input == 'email':
                email_text = email_text[:-1]
            input_error_text = ""
        else:
            char = event.unicode
            if len(char) == 1 and char.isprintable():
                if active_input == 'name' and len(name_text) < 15:
                    name_text += char
                elif active_input == 'email' and len(email_text) < 30:
                    email_text += char
            
def validate_email(email):
    """Verifica si el email tiene un formato básico válido."""
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(regex, email, re.IGNORECASE)

def save_user_data():
    """Valida los datos y los establece como el usuario actual."""
    global game_state, current_player_name, current_player_email, input_error_text, name_text, email_text
    
    if not name_text.strip():
        input_error_text = "El nombre no puede estar vacío."
        return
    
    if email_text.strip() and not validate_email(email_text):
        input_error_text = "El email no tiene un formato válido."
        return

    current_player_name = name_text.strip()
    current_player_email = email_text.strip()
    game_state = MENU
    input_error_text = ""
    name_text = current_player_name
    email_text = current_player_email

# ----------------------------
# 6. BUCLE PRINCIPAL DEL JUEGO
# ----------------------------

# Inicialización
data_manager = DataManager()
game = Game()
name_text = current_player_name
email_text = current_player_email


SNAKE_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SNAKE_UPDATE, game.current_speed_ms)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # --- Manejo de la Lógica del Juego (RUNNING) ---
        if game_state == RUNNING:
            if event.type == SNAKE_UPDATE:
                game.update() # Mueve la serpiente y habilita el cambio de dirección (can_change_direction = True)

            if event.type == pygame.KEYDOWN:
                # Se llama al nuevo método change_direction que contiene la lógica de restricción
                if event.key == pygame.K_UP:
                    game.snake.change_direction(Vector2(0, -1))
                if event.key == pygame.K_DOWN:
                    game.snake.change_direction(Vector2(0, 1))
                if event.key == pygame.K_LEFT:
                    game.snake.change_direction(Vector2(-1, 0))
                if event.key == pygame.K_RIGHT:
                    game.snake.change_direction(Vector2(1, 0))

        # --- Manejo de la Interfaz ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if game_state == MENU:
                if boton_rects["JUGAR"].collidepoint(mouse_pos):
                    game_state = RUNNING
                elif boton_rects["CLASIFICACIONES"].collidepoint(mouse_pos):
                    game_state = LEADERBOARD
                    leaderboard_page = 0
                elif boton_rects["USUARIO"].collidepoint(mouse_pos):
                    game_state = USER_INPUT
                elif boton_rects["SALIR DEL JUEGO"].collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

            elif game_state == GAME_OVER:
                if game_over_rects["PLAY_AGAIN"].collidepoint(mouse_pos):
                    game_state = RUNNING
                elif game_over_rects["MENU"].collidepoint(mouse_pos):
                    game_state = MENU

            elif game_state == LEADERBOARD:
                if leaderboard_close_button.collidepoint(mouse_pos):
                    game_state = MENU
                
                if 'prev_page_button' in locals() and prev_page_button.rect.collidepoint(mouse_pos) and leaderboard_page > 0:
                    leaderboard_page -= 1
                scores = data_manager.get_top_scores()
                scores_per_page = 10
                num_pages = (len(scores) + scores_per_page - 1) // scores_per_page
                if 'next_page_button' in locals() and next_page_button.rect.collidepoint(mouse_pos) and leaderboard_page < num_pages - 1:
                    leaderboard_page += 1

            elif game_state == USER_INPUT:
                if user_input_close_button.collidepoint(mouse_pos):
                    game_state = MENU
                    input_error_text = ""
                elif name_input_rect and name_input_rect.collidepoint(mouse_pos):
                    active_input = 'name'
                elif email_input_rect and email_input_rect.collidepoint(mouse_pos):
                    active_input = 'email'
                else:
                    active_input = None
                if submit_button_rect and submit_button_rect.collidepoint(mouse_pos):
                    save_user_data()

        # --- Manejo de Teclado en Input de Texto ---
        if game_state == USER_INPUT:
            handle_text_input(event)

    # -------------------
    # DIBUJO
    # -------------------

    if game_state == MENU:
        screen.fill(GREEN_DARK)
        draw_menu()

    elif game_state == RUNNING or game_state == GAME_OVER:
        # 1. Dibuja el tablero
        screen.fill(GREEN_DARK)
        for fila in range(number_of_cells):
            for columna in range(number_of_cells):
                color = GREEN_LIGHT if (fila + columna) % 2 == 0 else GREEN_DARK
                rect = pygame.Rect(
                    OFFSET + columna * cell_size,
                    OFFSET + fila * cell_size,
                    cell_size,
                    cell_size
                )
                pygame.draw.rect(screen, color, rect)

        pygame.draw.rect(screen, DARK_GREEN,
                         (OFFSET - 5, OFFSET - 5, cell_size * number_of_cells + 10, cell_size * number_of_cells + 10), 5)

        # 2. Dibuja elementos del juego
        game.draw()

        # 3. Dibuja Score y Nombre
        score_surface = score_font.render(f"Puntaje: {game.score}", True, DARK_GREEN)
        name_surface = score_font.render(f"Jugador: {current_player_name}", True, DARK_GREEN)

        screen.blit(name_surface, (OFFSET, ALTO - 50))
        screen.blit(score_surface, (OFFSET + name_surface.get_width() + 30, ALTO - 50))
        
        # 4. Dibuja la pantalla de Game Over si aplica
        if game_state == GAME_OVER:
            draw_game_over()

    elif game_state == LEADERBOARD:
        draw_leaderboard()

    elif game_state == USER_INPUT:
        draw_user_input()

    pygame.display.update()
    clock.tick(60)