## 🎮 launcher.py
# Menú principal con tres juegos, créditos, música y botón de sonido.

import pygame, sys, os, subprocess

# --- Inicialización ---
pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

# --- Configuración general ---
WIDTH, HEIGHT = 900, 640
FPS = 60
BG_COLOR = (15, 15, 25)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 220, 80)
GREEN = (80, 200, 120)
BLUE = (80, 140, 220)

# Ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Arcade Launcher")
clock = pygame.time.Clock()

# Fuentes
title_font = pygame.font.Font(None, 90)
menu_font = pygame.font.Font(None, 50)
credits_font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 30)

# Música del menú
MUSIC_FILE = "menu_retro.mp3"
music_on = False
if os.path.exists(MUSIC_FILE):
    pygame.mixer.music.load(MUSIC_FILE)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)
    music_on = True

# --- Clase botón ---
class Button:
    def __init__(self, text, rect, base_color, hover_color, text_color=WHITE):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = menu_font

    def draw(self, surface):
        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        text_surf = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# --- Créditos ---
def show_credits():
    credits_text = [
        "🎮 CREDITS 🎮",
        "",
        "-Space Invaders-:",
        "Hecho por: Ignacio Janco",
        "Música del menú: TRYZ",
        "Música del juego: Desconocida",
        "Playtesters: Lionel y Alan",
        "",
        " -Flappy Bird Pobre-:",
        "Hecho por: Alan Chaparro",
        "Música: No utilizada",
        "Origen de efectos: Desconocido",
        "Playtesters: Ignacio y Lionel",
        "",
        "-Snake-:",
        "Hecho por: Lionel Belén",
        "Música: No utilizada",
        "Origen de efectos: Desconocido",
        "Playtesters: Ignacio y Alan",
        "",
        "🧰 Programas usados:",
        "Python, Thonny, Visual Studio Code, Pygame",
        "",
        "💬 Agradecimientos:",
        "A todos los profes de la especialidad y a nuestras familias ❤️",
        "",
        "-------------------  Gracias : ) ---------------------"
    ]

    # Cargar el meme
    meme_img = None
    if os.path.exists("meme.jpg"):
        meme_img = pygame.image.load("meme.jpg").convert_alpha()
        meme_img = pygame.transform.scale(meme_img, (350, 350))

    scrolling_y = HEIGHT
    meme_shown = False
    alpha = 0

    while True:
        screen.fill(BG_COLOR)

        # Dibujar los créditos que suben
        for i, line in enumerate(credits_text):
            text = credits_font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, scrolling_y + i * 50))
            screen.blit(text, text_rect)

        scrolling_y -= 1

        # Cuando terminan los créditos, mostrar el meme
        if scrolling_y < -len(credits_text) * 50:
            if meme_img:
                if alpha < 255:
                    alpha += 3  # efecto de aparición
                meme_img.set_alpha(alpha)
                meme_rect = meme_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(meme_img, meme_rect)

                msg = small_font.render("Presiona cualquier tecla para volver", True, GRAY)
                screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT - 40)))
            else:
                msg = small_font.render("(No se encontró meme.jpg)", True, GRAY)
                screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return

        pygame.display.flip()
        clock.tick(60)

# --- Funciones auxiliares ---
def run_game(file_name):
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    subprocess.Popen(["python", file_name])
    pygame.time.wait(500)
    pygame.mixer.music.play(-1)

def draw_music_button():
    icon = "🔊" if music_on else "🔇"
    text = small_font.render(icon, True, WHITE)
    pygame.draw.circle(screen, GRAY, (40, HEIGHT - 40), 25)
    screen.blit(text, text.get_rect(center=(40, HEIGHT - 40)))

def toggle_music():
    global music_on
    if music_on:
        pygame.mixer.music.pause()
        music_on = False
    else:
        pygame.mixer.music.unpause()
        music_on = True

# --- Botones del menú principal ---
buttons = [
    Button("🎯 Jugar Space Invaders", (WIDTH//2 - 200, 220, 400, 60), BLUE, (100, 170, 250)),
    Button("🕊️ Jugar Flappy Pobre", (WIDTH//2 - 200, 300, 400, 60), YELLOW, (255, 240, 120)),
    Button("🐍 Jugar Snake Pobre", (WIDTH//2 - 200, 380, 400, 60), GREEN, (100, 250, 150)),
]
credits_button = Button("Créditos", (WIDTH - 180, 30, 150, 40), GRAY, (180, 180, 180))

# --- Bucle principal ---
def main_menu():
    global music_on
    while True:
        # Fondo animado
        for y in range(HEIGHT):
            color = (int(20 + y/15) % 255, int(20 + y/25) % 255, 40)
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))

        # Título
        title = title_font.render("RETRO ARCADE", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))

        # Botones
        for button in buttons:
            button.draw(screen)
        credits_button.draw(screen)
        draw_music_button()

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if buttons[0].is_clicked(pos):
                    run_game("space_invaders.py")
                elif buttons[1].is_clicked(pos):
                    run_game("flappy_pobre.py")
                elif buttons[2].is_clicked(pos):
                    run_game("snake_pobre.py")
                elif credits_button.is_clicked(pos):
                    show_credits()
                elif (pos[0]-40)**2 + (pos[1]-(HEIGHT-40))**2 <= 25**2:
                    toggle_music()

        pygame.display.flip()
        clock.tick(FPS)

# --- Iniciar menú ---
if __name__ == "__main__":
    main_menu()
