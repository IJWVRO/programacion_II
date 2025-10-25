import pygame
import random
import sys
import os
import time

# ------------------- Inicialización -------------------
pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except Exception as e:
    print("Advertencia: no se pudo inicializar el mixer:", e)

# ------------------- Configuración -------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders Minijuego 🎮")
clock = pygame.time.Clock()
FPS = 60

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 220, 0)
RED = (220, 60, 60)
YELLOW = (230, 230, 80)
BLUE = (100, 150, 255)
GRAY = (60, 60, 60)
HIGHLIGHT = (180, 180, 180)

# Fuentes
font_small = pygame.font.SysFont("consolas", 20)
font_med = pygame.font.SysFont("consolas", 28)
font_big = pygame.font.SysFont("consolas", 52)

# Música
MENU_MUSIC = "menu.mp3"
GAME_MUSIC = "game.mp3"
menu_volume = 0.3
game_volume = 0.6

# ------------------- Funciones de música -------------------
def play_music(file, volume=0.6, loop=True, fade_ms=800):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
    if os.path.exists(path):
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(fade_ms)
                pygame.time.delay(fade_ms)
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade_ms)
        except Exception as e:
            print("Error al reproducir música:", e)
    else:
        print(f"No se encontró {file}")

def stop_music(fade_ms=0):
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(fade_ms)
    except:
        pass

# ------------------- Fondo de estrellas -------------------
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(60)]
def draw_background():
    screen.fill(BLACK)
    for s in stars:
        pygame.draw.circle(screen, WHITE, (s[0], s[1]), 1)

def update_stars():
    for s in stars:
        s[1] += 1
        if s[1] > HEIGHT:
            s[0] = random.randint(0, WIDTH)
            s[1] = 0

def draw_text(text, font_obj, color, x, y, center=True):
    surf = font_obj.render(text, True, color)
    rect = surf.get_rect(center=(x,y)) if center else surf.get_rect(topleft=(x,y))
    screen.blit(surf, rect)
    return rect

# ------------------- Puntajes -------------------
scores_file = "scores.txt"
def load_scores():
    if not os.path.exists(scores_file):
        return []
    out = []
    with open(scores_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                n, s = line.strip().split(",", 1)
                out.append((n, int(s)))
            except:
                pass
    return sorted(out, key=lambda x: x[1], reverse=True)

def save_score(name, pts):
    with open(scores_file, "a", encoding="utf-8") as f:
        f.write(f"{name},{pts}\n")

def show_scores():
    scores = load_scores()
    showing = True
    while showing:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                showing = False

        update_stars()
        draw_background()
        draw_text("🏆 TABLA DE PUNTAJES 🏆", font_med, YELLOW, WIDTH//2, 60)
        start_y = 110
        for i, (n,s) in enumerate(scores[:20]):
            draw_text(f"{i+1:02d}. {n} - {s}", font_small, WHITE, WIDTH//2, start_y + i*22)
        draw_text("Clic o tecla para volver", font_small, BLUE, WIDTH//2, HEIGHT - 30)
        pygame.display.flip()

# ------------------- Enemigos -------------------
def create_enemies(rows=4, cols=8):
    enemies = []
    for r in range(rows):
        for c in range(cols):
            x = 80 + c * 70
            y = 60 + r * 60
            enemies.append(pygame.Rect(x, y, 40, 40))
    return enemies

# ------------------- Fade y carga -------------------
def fade_out(duration_ms=350):
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill(BLACK)
    steps = 20
    delay = max(1, duration_ms // steps)
    for i in range(steps+1):
        alpha = int((i/steps) * 255)
        fade.set_alpha(alpha)
        draw_background()
        screen.blit(fade, (0,0))
        pygame.display.flip()
        pygame.time.delay(delay)

def loading_screen(seconds=1.4):
    t0 = time.time()
    while time.time() - t0 < seconds:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        update_stars()
        draw_background()
        draw_text("CARGANDO...", font_med, WHITE, WIDTH//2, HEIGHT//2 - 30)
        elapsed = time.time() - t0
        frac = min(1.0, elapsed / seconds)
        bar_w = 400; bar_h = 18
        bx = WIDTH//2 - bar_w//2; by = HEIGHT//2 + 10
        pygame.draw.rect(screen, GRAY, (bx, by, bar_w, bar_h), border_radius=6)
        pygame.draw.rect(screen, GREEN, (bx+2, by+2, int((bar_w-4)*frac), bar_h-4), border_radius=6)
        pygame.display.flip()

# ------------------- Ajuste de volumen -------------------
def adjust_volumes():
    global menu_volume, game_volume
    adjusting = True
    selected = 0  # 0=menu, 1=juego
    play_music(MENU_MUSIC, menu_volume, fade_ms=400)
    
    while adjusting:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_TAB:
                    selected = 1 - selected
                    if selected == 0: play_music(MENU_MUSIC, menu_volume, fade_ms=200)
                    else: play_music(GAME_MUSIC, game_volume, fade_ms=200)
                elif e.key == pygame.K_LEFT:
                    if selected == 0:
                        menu_volume = max(0.0, menu_volume - 0.05)
                        play_music(MENU_MUSIC, menu_volume, fade_ms=200)
                    else:
                        game_volume = max(0.0, game_volume - 0.05)
                        play_music(GAME_MUSIC, game_volume, fade_ms=200)
                elif e.key == pygame.K_RIGHT:
                    if selected == 0:
                        menu_volume = min(1.0, menu_volume + 0.05)
                        play_music(MENU_MUSIC, menu_volume, fade_ms=200)
                    else:
                        game_volume = min(1.0, game_volume + 0.05)
                        play_music(GAME_MUSIC, game_volume, fade_ms=200)
                elif e.key == pygame.K_ESCAPE:
                    adjusting = False

        update_stars()
        draw_background()
        draw_text("AJUSTAR VOLUMEN", font_big, YELLOW, WIDTH//2, HEIGHT//6)
        draw_text("TAB = cambiar, IZQ/DER = volumen, ESC = volver", font_small, BLUE, WIDTH//2, HEIGHT//6 + 40)
        draw_text(f"{'MENÚ' if selected==0 else 'JUEGO'}: {int((menu_volume if selected==0 else game_volume)*100)}%", font_med, WHITE, WIDTH//2, HEIGHT//2)
        pygame.display.flip()

# ------------------- Juego principal -------------------
def main_game():
    fade_out()
    loading_screen()
    stop_music(fade_ms=800)
    play_music(GAME_MUSIC, game_volume, fade_ms=800)

    player = pygame.Rect(WIDTH//2 - 25, HEIGHT - 60, 50, 20)
    bullets = []
    enemy_bullets = []
    enemies = create_enemies()
    direction = 1
    score = 0
    enemy_speed = 2
    running = True

    while running:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0: player.x -= 7
        if keys[pygame.K_RIGHT] and player.right < WIDTH: player.x += 7
        if keys[pygame.K_SPACE] and len(bullets)<5: bullets.append(pygame.Rect(player.centerx-2, player.top, 4, 10))

        move_down = False
        for en in enemies:
            en.x += enemy_speed * direction
            if en.right >= WIDTH - 10 or en.left <= 10: move_down = True
        if move_down:
            direction *= -1
            for en in enemies: en.y += 20

        if enemies and random.randint(1, 40)==1:
            shooter=random.choice(enemies)
            enemy_bullets.append(pygame.Rect(shooter.centerx-2, shooter.bottom, 4, 10))

        for b in bullets[:]:
            b.y -= 8
            if b.y < 0: bullets.remove(b)
            else:
                for e in enemies[:]:
                    if b.colliderect(e):
                        enemies.remove(e)
                        bullets.remove(b)
                        score += 10
                        break

        for eb in enemy_bullets[:]:
            eb.y += 6
            if eb.y>HEIGHT: enemy_bullets.remove(eb)
            elif eb.colliderect(player): running=False

        if not enemies: enemies = create_enemies()

        update_stars()
        draw_background()
        pygame.draw.rect(screen, GREEN, player)
        for b in bullets: pygame.draw.rect(screen, WHITE, b)
        for eb in enemy_bullets: pygame.draw.rect(screen, BLUE, eb)
        for en in enemies: pygame.draw.rect(screen, RED, en)
        draw_text(f"Puntos: {score}", font_small, WHITE, 10, 10, center=False)
        pygame.display.flip()

    stop_music(fade_ms=800)
    name = ""
    entering = True
    while entering:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key==pygame.K_RETURN and name.strip(): save_score(name, score); entering=False
                elif e.key==pygame.K_BACKSPACE: name=name[:-1]
                else: 
                    if len(name)<10 and e.unicode.isprintable(): name+=e.unicode

        update_stars()
        draw_background()
        draw_text("GAME OVER - Escribí tu nombre:", font_med, RED, WIDTH//2, HEIGHT//2-60)
        draw_text(name, font_med, GREEN, WIDTH//2, HEIGHT//2)
        pygame.display.flip()

    show_scores()
    play_music(MENU_MUSIC, menu_volume, fade_ms=800)  # volver al menú con música del menú

# ------------------- Menú principal -------------------
def main_menu():
    play_music(MENU_MUSIC, menu_volume, fade_ms=800)
    running = True
    while running:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        click=False
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            elif e.type==pygame.MOUSEBUTTONDOWN: click=True

        update_stars()
        draw_background()
        draw_text("SPACE INVADERS", font_big, GREEN, WIDTH//2, HEIGHT//4)

        buttons=[("JUGAR", HEIGHT//2-60, BLUE),
                 ("PUNTAJES", HEIGHT//2, GREEN),
                 ("AJUSTAR VOLUMEN", HEIGHT//2+60, YELLOW),
                 ("SALIR", HEIGHT//2+120, RED)]
        for text, y, base_color in buttons:
            rect=pygame.Rect(WIDTH//2-120, y-20, 240,40)
            color=HIGHLIGHT if rect.collidepoint(mx,my) else base_color
            pygame.draw.rect(screen,color,rect,border_radius=6)
            draw_text(text,font_med,BLACK,rect.centerx,rect.centery)

        pygame.display.flip()
        if click:
            for text,y,base_color in buttons:
                rect=pygame.Rect(WIDTH//2-120, y-20, 240,40)
                if rect.collidepoint(mx,my):
                    if text=="JUGAR": main_game()
                    elif text=="PUNTAJES": show_scores()
                    elif text=="AJUSTAR VOLUMEN": adjust_volumes()
                    elif text=="SALIR": pygame.quit(); sys.exit()

# ------------------- Iniciar -------------------
if __name__=="__main__":
    main_menu()
