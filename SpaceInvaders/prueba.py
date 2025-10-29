import pygame
import random
import sys
import os
import time
import json

# Inicializacion
pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except Exception as e:
    print("Advertencia: no se pudo inicializar el mixer:", e)

# Configuracion de la pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()
FPS = 60

# Configuracion de los colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 220, 0)
RED = (220, 60, 60)
YELLOW = (230, 230, 80)
BLUE = (100, 150, 255)
GRAY = (60, 60, 60)
HIGHLIGHT = (180, 180, 180)

# fuentes de texto en este caso use la fuente llamada consolas
font_small = pygame.font.SysFont("consolas", 18)
font_med = pygame.font.SysFont("consolas", 26)
font_big = pygame.font.SysFont("consolas", 48)

# las dos musicas utilizadas
menu = "menu.mp3"
juego = "game.mp3"

# Volúmenes predederminados
menu_volume = 0.3
game_volume = 0.6

# Archivos de puntaje use json para este sistema
SCORES_JSON = "scores.json"

def load_scores_json():
    """Carga puntajes desde SCORES_JSON. Devuelve lista de dicts {'name':..., 'score':...}."""
    if not os.path.exists(SCORES_JSON):
        return []
    try:
        with open(SCORES_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                # sanitizar
                out = []
                for it in data:
                    if isinstance(it, dict) and "name" in it and "score" in it:
                        try:
                            out.append({"name": str(it["name"]), "score": int(it["score"])})
                        except:
                            continue
                # ordenar descendente
                out.sort(key=lambda x: x["score"], reverse=True)
                return out
    except Exception as e:
        print("No se pudo leer scores.json:", e)
    return []

def save_score_json(name, pts):
    """Agrega un puntaje al archivo JSON."""
    scores = load_scores_json()
    scores.append({"name": name, "score": int(pts)})
    # ordenar y limitar si se desea (aquí guardamos todo)
    scores.sort(key=lambda x: x["score"], reverse=True)
    try:
        with open(SCORES_JSON, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error guardando scores.json:", e)

# ------------------- Reproducción de música (con y sin fade) -------------------
def play_music_with_fade(file, volume=0.6, loop=True, fade_ms=800):
    """Reproduce con fade: detiene la pista actual (fadeout), espera y empieza la nueva con fade."""
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
        # no romper el juego si falta archivo, solo informar
        print(f"No se encontró {file}")

def play_music_instant(file, volume=0.6, loop=True):
    """Reproduce inmediatamente (sin fade) — útil para ajuste de volumen donde queremos feedback instantáneo."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
    if os.path.exists(path):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception as e:
            print("Error al reproducir música (instant):", e)
    else:
        print(f"No se encontró {file}")

def stop_music(fade_ms=0):
    try:
        if pygame.mixer.music.get_busy() and fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
    except Exception:
        pass

# ------------------- Fondo de estrellas -------------------
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(70)]

def update_stars():
    for s in stars:
        s[1] += 1
        if s[1] > HEIGHT:
            s[0] = random.randint(0, WIDTH)
            s[1] = 0

def draw_background():
    screen.fill(BLACK)
    for s in stars:
        pygame.draw.circle(screen, WHITE, (s[0], s[1]), 1)

# ------------------- Utilidades de texto -------------------
def draw_text_center(text, font_obj, color, x, y):
    surf = font_obj.render(text, True, color)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)
    return rect

def draw_text_left(text, font_obj, color, x, y):
    surf = font_obj.render(text, True, color)
    rect = surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)
    return rect

# ------------------- Enemigos -------------------
def create_enemies(rows=4, cols=8):
    enemies = []
    for r in range(rows):
        for c in range(cols):
            x = 80 + c * 70
            y = 60 + r * 60
            enemies.append(pygame.Rect(x, y, 40, 40))
    return enemies

# ------------------- Pantalla de carga y fade -------------------
def loading_screen(seconds=1.0):
    t0 = time.time()
    while time.time() - t0 < seconds:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        update_stars()
        draw_background()
        draw_text_center("CARGANDO...", font_big, WHITE, WIDTH//2, HEIGHT//2 - 20)
        frac = (time.time() - t0) / seconds
        if frac > 1: frac = 1
        bw = 400; bh = 16
        bx = WIDTH//2 - bw//2; by = HEIGHT//2 + 20
        pygame.draw.rect(screen, GRAY, (bx, by, bw, bh), border_radius=6)
        pygame.draw.rect(screen, GREEN, (bx, by, int(bw * frac), bh), border_radius=6)
        pygame.display.flip()

def fade_out_screen(duration_ms=350):
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill(BLACK)
    steps = 20
    delay = max(1, duration_ms // steps)
    for i in range(steps+1):
        alpha = int((i/steps) * 255)
        fade.set_alpha(alpha)
        update_stars()
        draw_background()
        screen.blit(fade, (0, 0))
        pygame.display.flip()
        pygame.time.delay(delay)

# ------------------- Ajuste de volumen (TAB + flechas) -------------------
def adjust_volumes():
    global menu_volume, game_volume
    selected = 0  # 0=menu, 1=game
    # reproducir la pista correspondiente sin fade para feedback inmediato
    play_music_instant(menu, menu_volume)
    adjusting = True
    while adjusting:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_TAB:
                    selected = 1 - selected
                    # reproducir inmediatamente la pista seleccionada para escuchar
                    if selected == 0:
                        play_music_instant(menu, menu_volume)
                    else:
                        play_music_instant(juego, game_volume)
                elif ev.key == pygame.K_LEFT:
                    if selected == 0:
                        menu_volume = max(0.0, round(menu_volume - 0.05, 2))
                        pygame.mixer.music.set_volume(menu_volume)
                    else:
                        game_volume = max(0.0, round(game_volume - 0.05, 2))
                        pygame.mixer.music.set_volume(game_volume)
                elif ev.key == pygame.K_RIGHT:
                    if selected == 0:
                        menu_volume = min(1.0, round(menu_volume + 0.05, 2))
                        pygame.mixer.music.set_volume(menu_volume)
                    else:
                        game_volume = min(1.0, round(game_volume + 0.05, 2))
                        pygame.mixer.music.set_volume(game_volume)
                elif ev.key == pygame.K_ESCAPE:
                    # al volver al menú, aseguramos reproducir la música del menú
                    play_music_with_fade(menu, menu_volume, fade_ms=400)
                    adjusting = False

        update_stars()
        draw_background()
        draw_text_center("AJUSTAR VOLUMEN", font_big, YELLOW, WIDTH//2, HEIGHT//6)
        draw_text_center("TAB = cambiar MENÚ/JUEGO | ← / → = ajustar | ESC = volver", font_small, BLUE, WIDTH//2, HEIGHT//6 + 40)
        draw_text_center(f"{'MENÚ' if selected == 0 else 'JUEGO'}: {int((menu_volume if selected==0 else game_volume)*100)}%", font_med, WHITE, WIDTH//2, HEIGHT//2)
        pygame.display.flip()

# - Tabla de puntajes
def show_scores_screen():
    """Muestra la tabla de puntajes; vuelve con clic o tecla."""
    play_music_with_fade(menu, menu, fade_ms=400)
    scores = load_scores_json()
    showing = True
    while showing:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                showing = False

        update_stars()
        draw_background()
        draw_text_center("TABLA DE PUNTAJES :) ", font_big, YELLOW, WIDTH//2, 70)
        start_y = 120
        for i, it in enumerate(scores[:20]):
            line = f"{i+1:02d}. {it['name']} — {it['score']}"
            draw_text_center(line, font_med, WHITE, WIDTH//2, start_y + i*26)
        draw_text_center("Clic o tecla para volver", font_small, BLUE, WIDTH//2, HEIGHT - 40)
        pygame.display.flip()

# Game Over pantalla
def game_over_screen_with_input(score):
    """Muestra Game Over, permite escribir nombre, guarda en JSON al Enter, luego muestra botones."""
    # 
    stop_music()
    name = ""
    entering_name = True
    prompt = "ESCRIBÍ TU NOMBRE (ENTER para guardar):"
    # First, show input until Enter
    while entering_name:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    if name.strip() == "":
                        # ignora los nombres
                        pass
                    else:
                        # guardado del json
                        save_score_json(name.strip(), score)
                        entering_name = False
                elif ev.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 12 and ev.unicode.isprintable():
                        name += ev.unicode

        update_stars()
        draw_background()
        draw_text_center("GAME OVER", font_big, RED, WIDTH//2, HEIGHT//2 - 140)
        draw_text_center(f"Puntos: {score}", font_med, WHITE, WIDTH//2, HEIGHT//2 - 90)
        draw_text_center(prompt, font_small, YELLOW, WIDTH//2, HEIGHT//2 - 40)
        # input box
        box_rect = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 20, 440, 40)
        pygame.draw.rect(screen, WHITE, box_rect, border_radius=6)
        # los nombres y su psicion en la tabla
        txt_surf = font_med.render(name, True, BLACK)
        screen.blit(txt_surf, (box_rect.x + 8, box_rect.y + 4))
        draw_text_center("", font_small, GRAY, WIDTH//2, HEIGHT//2 + 40)
        pygame.display.flip()

    # tras guardar, mostrar botones: jugar de nuevo / volver al menu
    buttons = [
        {"label": "Jugar de nuevo", "rect": pygame.Rect(WIDTH//2 - 160, HEIGHT//2 + 60, 320, 54), "color": GREEN},
        {"label": "Volver al menú", "rect": pygame.Rect(WIDTH//2 - 160, HEIGHT//2 + 130, 320, 54), "color": BLUE},
    ]
    # asegurar que al volver se escuche la musica del juego"
    showing = True
    while showing:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                for b in buttons:
                    if b["rect"].collidepoint(ev.pos):
                        if b["label"] == "Jugar de nuevo":
                            # comenzar otra vez 
                            play_music_with_fade(juego, game_volume, fade_ms=400)
                            return "retry"
                        else:
                            play_music_with_fade(menu, menu_volume, fade_ms=400)
                            return "menu"

        update_stars()
        draw_background()
        draw_text_center("GAME OVER", font_big, RED, WIDTH//2, HEIGHT//2 - 120)
        draw_text_center(f"Puntos guardados: {score}", font_med, WHITE, WIDTH//2, HEIGHT//2 - 60)
        for b in buttons:
            color = b["color"]
            if b["rect"].collidepoint(mx, my):
                color = (min(color[0]+40,255), min(color[1]+40,255), min(color[2]+40,255))
            pygame.draw.rect(screen, color, b["rect"], border_radius=8)
            draw_text_center(b["label"], font_med, BLACK, b["rect"].centerx, b["rect"].centery)
        pygame.display.flip()

# juego principal
def main_game():
    """Función principal del juego (minijuego)."""
    # fade out del menu y carga, luego reproducir musica del juego
    fade_out_screen(200)
    loading_screen()
    play_music_with_fade(juego, game_volume, fade_ms=400)

    # player rect y variables
    player = pygame.Rect(WIDTH//2 - 25, HEIGHT - 60, 50, 20)
    bullets = []           # balas del jugador
    enemy_bullets = []     # disparos enemigos
    enemies = create_enemies()
    direction = 1
    score = 0
    enemy_speed = 2
    # Vidas
    player_lives = 3
    running = True

    while running:
        clock.tick(FPS)
        # eventos
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        # entrada 
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= 7
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += 7
        if keys[pygame.K_SPACE] and len(bullets) < 5:
            # crear bala
            bullets.append(pygame.Rect(player.centerx - 2, player.top, 4, 10))

        # movimiento de los enemigos
        move_down = False
        for en in enemies:
            en.x += enemy_speed * direction
            if en.right >= WIDTH - 10 or en.left <= 10:
                move_down = True
        if move_down:
            direction *= -1
            for en in enemies:
                en.y += 20

        # el disparo de los enemigos es alatorio
        if enemies and random.randint(1, 40) == 1:
            shooter = random.choice(enemies)
            enemy_bullets.append(pygame.Rect(shooter.centerx - 2, shooter.bottom, 4, 10))

        # balas jugador
        for b in bullets[:]:
            b.y -= 8
            if b.bottom < 0:
                try:
                    bullets.remove(b)
                except ValueError:
                    pass
                continue
            # comprobacion de las coliciones de los enemigos y la del jugador
            hit_enemy = None
            for e in enemies:
                if b.colliderect(e):
                    hit_enemy = e
                    break
            if hit_enemy:
                try:
                    enemies.remove(hit_enemy)
                except ValueError:
                    pass
                try:
                    bullets.remove(b)
                except ValueError:
                    pass
                score += 10
                # no seguir comprobando
                continue

        # actualizacion de las balas de los enemigos 
        for eb in enemy_bullets[:]:
            eb.y += 6
            if eb.top > HEIGHT:
                try:
                    enemy_bullets.remove(eb)
                except ValueError:
                    pass
                continue
            if eb.colliderect(player):
                try:
                    enemy_bullets.remove(eb)
                except ValueError:
                    pass
                player_lives -= 1
                # el jugador se posisiona en el centro por lo que resivio daño
                player.x = WIDTH//2 - player.width//2
                if player_lives <= 0:
                    running = False
                    break

        # si algun enemigo llega a estar en la misma altura que el jugador el jugador va a morir instantaneamente
        for e in enemies:
            if e.bottom >= player.top:
                player_lives = 0
                running = False
                break

        # Si no quedan enemigos, aparecen de nuevo , esto es infinito :( 
        if not enemies:
            enemies = create_enemies()

        # diseños de los personajes (bueno de hecho son cuadrados nomas)
        update_stars()
        draw_background()
        # jugador
        pygame.draw.rect(screen, GREEN, player)
        # las balas del jugador
        for b in bullets:
            pygame.draw.rect(screen, WHITE, b)
        # las balas de los enemigos
        for eb in enemy_bullets:
            pygame.draw.rect(screen, BLUE, eb)
        # los enemigos
        for e in enemies:
            pygame.draw.rect(screen, RED, e)

        # HUD: de las vidas y puntos
        draw_text_left(f"Puntos: {score}", font_small, WHITE, 10, 10)
        life_text = f"Vida: {player_lives}"
        draw_text_left(life_text, font_small, WHITE, WIDTH - 160, 10)
        # la barrita simple
        max_lives = 3
        bar_w = 100
        bar_h = 12
        bx = WIDTH - 160
        by = 30
        pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
        if player_lives > 0:
            fill_w = int((player_lives / max_lives) * bar_w)
            pygame.draw.rect(screen, GREEN, (bx, by, fill_w, bar_h))

        pygame.display.flip()

    # --- al terminar la partida el jugador debe ingresar su nombre
    stop_music(fade_ms=400)
    result = game_over_screen_with_input(score)
    if result == "retry":
        main_game()
    else:
        # volver al menu
        return

# ***************** Menu principal ****************
def main_menu():
    # al entrar al menú siempre reproducir la musica del menu
    play_music_with_fade(menu, menu_volume, fade_ms=400)
    loading_screen()

    # botones: color , tamaño y texto
    buttons = [
        ("JUGAR", HEIGHT//2 - 60, GREEN),
        ("PUNTUACIONES", HEIGHT//2, YELLOW),
        ("AJUSTAR VOLUMEN", HEIGHT//2 + 60, BLUE),
        ("SALIR", HEIGHT//2 + 120, RED),
    ]

    running = True
    while running:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        click = False
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                stop_music()
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                click = True

        update_stars()
        draw_background()
        draw_text_center("SPACE INVADERS", font_big, GREEN, WIDTH//2, HEIGHT//4)

        # los botones
        for text, y, base_color in buttons:
            rect = pygame.Rect(WIDTH//2 - 140, y - 22, 280, 48)
            color = base_color
            if rect.collidepoint(mx, my):
                # cuando el maus esta cerca se aclara un poco
                color = (min(base_color[0] + 40, 255), min(base_color[1] + 40, 255), min(base_color[2] + 40, 255))
            pygame.draw.rect(screen, color, rect, border_radius=8)
            draw_text_center(text, font_med, BLACK, rect.centerx, rect.centery)

        pygame.display.flip()

        if click:
            for text, y, base_color in buttons:
                rect = pygame.Rect(WIDTH//2 - 140, y - 22, 280, 48)
                if rect.collidepoint(mx, my):
                    if text == "JUGAR":
                        main_game()
                        # cuando regreseal menu forzamos música de menu
                        play_music_with_fade(menu, menu_volume, fade_ms=400)
                    elif text == "PUNTUACIONES":
                        show_scores_screen()
                        # asegurarmos de que siga sonando la musica del menu
                        play_music_with_fade(menu, menu_volume, fade_ms=400)
                    elif text == "AJUSTAR VOLUMEN":
                        # ajuste de la musica usando playback instantáneo para escuchar cambios sin fades
                        adjust_volumes()
                        # al volver al menu nos aseguramos de que siga sonando el menu (soy medio duro con la musica del menu)
                        play_music_with_fade(menu, menu_volume, fade_ms=400)
                    elif text == "SALIR":
                        stop_music()
                        pygame.quit()
                        sys.exit()

# ejecucion
if __name__ == "__main__":
    main_menu()
