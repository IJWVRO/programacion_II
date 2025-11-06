import pygame
import random
import sys
import os
import time
import json
import smtplib
from email.message import EmailMessage

# ------------------ CONFIG (solo estas 2 variables para SMTP/Gmail) ------------------
# Reemplaza con tu email y la contraseña de aplicación (app password).
# Ejemplo:
# EMAIL_ADDRESS = "tucorreo@gmail.com"
# EMAIL_PASSWORD = "clave_de_aplicacion"
EMAIL_ADDRESS = "fairbotnotifier@gmail.com"    # <- pon aquí tu correo (string)
EMAIL_PASSWORD = "pvrcyhncquzcibyv"   # <- pon aquí tu clave de aplicación (string)

# ------------------ Inicialización / Config ------------------
pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except Exception as e:
    print("Advertencia: no se pudo inicializar el mixer:", e)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
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

# Fuentes
font_small = pygame.font.SysFont("consolas", 18)
font_med = pygame.font.SysFont("consolas", 26)
font_big = pygame.font.SysFont("consolas", 48)

# Música (si no las tienes, el código seguirá funcionando; solo imprime avisos)
menu = "menu.mp3"
juego = "game.mp3"

menu_volume = 0.3
game_volume = 0.6

SCORES_JSON = "scores.json"

# ------------------ Funciones para JSON de puntajes ------------------
def load_scores_json():
    if not os.path.exists(SCORES_JSON):
        return []
    try:
        with open(SCORES_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                out = []
                for it in data:
                    if isinstance(it, dict) and "name" in it and "score" in it:
                        try:
                            out.append({
                                "name": str(it.get("name", "")),
                                "score": int(it.get("score", 0)),
                                "email": str(it.get("email", "")) if it.get("email", "") is not None else ""
                            })
                        except Exception:
                            continue
                out.sort(key=lambda x: x["score"], reverse=True)
                return out
    except Exception as e:
        print("No se pudo leer scores.json:", e)
    return []

def save_score_json(name, pts, email=""):
    scores = load_scores_json()
    scores.append({"name": name, "score": int(pts), "email": email})
    scores.sort(key=lambda x: x["score"], reverse=True)
    try:
        with open(SCORES_JSON, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error guardando scores.json:", e)

# ------------------ Envío de correo (Gmail: smtp.gmail.com:587, STARTTLS) ------------------
def enviar_correo_gmail(destinatario, nombre, puntaje):
    """
    Envía correo usando únicamente EMAIL_ADDRESS y EMAIL_PASSWORD (Gmail STARTTLS).
    - No hace nada si EMAIL_ADDRESS o EMAIL_PASSWORD están vacíos.
    - Devuelve True si todo salió bien, False en caso contrario.
    """
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("EMAIL_ADDRESS o EMAIL_PASSWORD no configurados: no se enviará correo.")
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = f"Nuevo puntaje en Space Invaders: {puntaje}"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = destinatario
        body = (f"Hola {nombre},\n\n"
                f"¡Felicidades! Tu puntaje de {puntaje} en Space Invaders fue registrado.\n\n"
                "Gracias por jugar.\n")
        msg.set_content(body)

        server = "smtp.gmail.com"
        port = 587
        with smtplib.SMTP(server, port, timeout=10) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            s.send_message(msg)
        print(f"Correo enviado a {destinatario}")
        return True
    except Exception as e:
        print("Error al enviar correo (SMTP):", e)
        return False

# ------------------ Reproducción de música ------------------
def play_music_with_fade(file, volume=0.6, loop=True, fade_ms=800):
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

def play_music_instant(file, volume=0.6, loop=True):
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

# ------------------ Fondo de estrellas ------------------
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

# ------------------ Utilidades de texto ------------------
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

# ------------------ Enemigos ------------------
def create_enemies(rows=4, cols=8):
    enemies = []
    for r in range(rows):
        for c in range(cols):
            x = 80 + c * 70
            y = 60 + r * 60
            enemies.append(pygame.Rect(x, y, 40, 40))
    return enemies

# ------------------ Loading y fade ------------------
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

# ------------------ Ajuste de volumen ------------------
def adjust_volumes():
    global menu_volume, game_volume
    selected = 0  # 0=menu, 1=game
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
                    play_music_with_fade(menu, menu_volume, fade_ms=400)
                    adjusting = False

        update_stars()
        draw_background()
        draw_text_center("AJUSTAR VOLUMEN", font_big, YELLOW, WIDTH//2, HEIGHT//6)
        draw_text_center("TAB = cambiar MENÚ/JUEGO | ← / → = ajustar | ESC = volver", font_small, BLUE, WIDTH//2, HEIGHT//6 + 40)
        draw_text_center(f"{'MENÚ' if selected == 0 else 'JUEGO'}: {int((menu_volume if selected==0 else game_volume)*100)}%", font_med, WHITE, WIDTH//2, HEIGHT//2)
        pygame.display.flip()

# ------------------ Triángulos para paginación ------------------
def draw_triangle_button(centerx, centery, size, direction="right", base_color=WHITE):
    """Dibuja triángulo (right/left) y devuelve rect para colisiones."""
    half = size // 2
    if direction == "right":
        points = [(centerx-half, centery-half), (centerx-half, centery+half), (centerx+half, centery)]
    else:
        points = [(centerx+half, centery-half), (centerx+half, centery+half), (centerx-half, centery)]
    pygame.draw.polygon(screen, base_color, points)
    minx = min(p[0] for p in points); maxx = max(p[0] for p in points)
    miny = min(p[1] for p in points); maxy = max(p[1] for p in points)
    return pygame.Rect(minx, miny, maxx - minx, maxy - miny)

def show_scores_screen():
    """Muestra puntajes con paginación y triángulos prev/next."""
    play_music_with_fade(menu, menu_volume, fade_ms=400)
    scores = load_scores_json()
    per_page = 10
    page = 0
    total_pages = max(1, (len(scores) + per_page - 1) // per_page)
    showing = True
    while showing:
        clock.tick(FPS)
        click = False
        mx, my = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                click = True
                mx, my = ev.pos
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    showing = False
                elif ev.key == pygame.K_LEFT:
                    page = max(0, page - 1)
                elif ev.key == pygame.K_RIGHT:
                    page = min(total_pages - 1, page + 1)

        update_stars()
        draw_background()
        draw_text_center("TABLA DE PUNTAJES", font_big, YELLOW, WIDTH//2, 70)

        start_idx = page * per_page
        for i, it in enumerate(scores[start_idx:start_idx + per_page]):
            index = start_idx + i
            line = f"{index+1:02d}. {it['name']} — {it['score']}"
            draw_text_center(line, font_med, WHITE, WIDTH//2, 120 + i*36)
            if it.get("email"):
                draw_text_center(f"{it.get('email')}", font_small, GRAY, WIDTH//2, 120 + i*36 + 20)

        # triángulos prev/next (gris si no hay más páginas)
        left_tri = draw_triangle_button(80, HEIGHT//2, 36, direction="left", base_color=WHITE if page>0 else GRAY)
        right_tri = draw_triangle_button(WIDTH-80, HEIGHT//2, 36, direction="right", base_color=WHITE if page < total_pages-1 else GRAY)

        draw_text_center(f"Página {page+1}/{total_pages}", font_small, BLUE, WIDTH//2, HEIGHT-40)
        draw_text_center("ESC = volver | ← → teclas | click triángulos", font_small, BLUE, WIDTH//2, HEIGHT-20)

        pygame.display.flip()

        if click:
            if left_tri.collidepoint(mx, my) and page > 0:
                page -= 1
            elif right_tri.collidepoint(mx, my) and page < total_pages - 1:
                page += 1
            else:
                # click fuera de triángulos cierra la tabla
                showing = False

# ------------------ Game Over: pedir nombre + correo, guardar, enviar correo ------------------
def game_over_screen_with_input(score):
    """
    0) pedir nombre (Enter)
    1) pedir correo (Enter para omitir)
    2) guardar, intentar enviar correo UNA VEZ (si email dado y credenciales configuradas)
    3) mostrar botones Jugar de nuevo / Volver al menú
    """
    stop_music()
    name = ""
    email = ""
    stage = 0
    prompt_name = "ESCRIBÍ TU NOMBRE (ENTER para guardar):"
    prompt_email = "ESCRIBÍ TU CORREO (ENTER para omitir):"
    email_sent_result = None  # True/False/None

    # Stage 0: nombre
    while stage == 0:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    if name.strip() == "":
                        pass
                    else:
                        stage = 1
                elif ev.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 20 and ev.unicode.isprintable():
                        name += ev.unicode

        update_stars()
        draw_background()
        draw_text_center("GAME OVER", font_big, RED, WIDTH//2, HEIGHT//2 - 140)
        draw_text_center(f"Puntos: {score}", font_med, WHITE, WIDTH//2, HEIGHT//2 - 90)
        draw_text_center(prompt_name, font_small, YELLOW, WIDTH//2, HEIGHT//2 - 40)
        box_rect = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 20, 440, 40)
        pygame.draw.rect(screen, WHITE, box_rect, border_radius=6)
        txt_surf = font_med.render(name, True, BLACK)
        screen.blit(txt_surf, (box_rect.x + 8, box_rect.y + 4))
        pygame.display.flip()

    # Stage 1: email
    while stage == 1:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    # Guardar (email puede quedar vacío)
                    save_score_json(name.strip(), score, email.strip())
                    # Intentar enviar correo UNA sola vez si el usuario ingresó un email
                    if email.strip():
                        email_sent_result = enviar_correo_gmail(email.strip(), name.strip(), score)
                    else:
                        email_sent_result = None
                    stage = 2
                elif ev.key == pygame.K_BACKSPACE:
                    email = email[:-1]
                else:
                    if len(email) < 100 and ev.unicode.isprintable():
                        email += ev.unicode

        update_stars()
        draw_background()
        draw_text_center("GAME OVER", font_big, RED, WIDTH//2, HEIGHT//2 - 140)
        draw_text_center(f"Puntos: {score}", font_med, WHITE, WIDTH//2, HEIGHT//2 - 90)
        draw_text_center(prompt_email, font_small, YELLOW, WIDTH//2, HEIGHT//2 - 40)
        box_rect = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 20, 600, 40)
        pygame.draw.rect(screen, WHITE, box_rect, border_radius=6)
        txt_surf = font_med.render(email, True, BLACK)
        screen.blit(txt_surf, (box_rect.x + 8, box_rect.y + 4))
        pygame.display.flip()

    # Stage 2: botones finales
    buttons = [
        {"label": "Jugar de nuevo", "rect": pygame.Rect(WIDTH//2 - 160, HEIGHT//2 + 60, 320, 54), "color": GREEN},
        {"label": "Volver al menú", "rect": pygame.Rect(WIDTH//2 - 160, HEIGHT//2 + 130, 320, 54), "color": BLUE},
    ]

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

        # Mostrar estado del email (si se ingresó)
        status_text = ""
        if email.strip():
            if email_sent_result is True:
                status_text = "Notificación por email: Enviada ✅"
            elif email_sent_result is False:
                status_text = "Notificación por email: Falló el envío ❌"
        else:
            status_text = "No se ingresó correo (omitido)."
        draw_text_center(status_text, font_small, GRAY, WIDTH//2, HEIGHT//2 + 20)

        pygame.display.flip()

# ------------------ Juego principal ------------------
def main_game():
    fade_out_screen(200)
    loading_screen()
    play_music_with_fade(juego, game_volume, fade_ms=400)

    player = pygame.Rect(WIDTH//2 - 25, HEIGHT - 60, 50, 20)
    bullets = []
    enemy_bullets = []
    enemies = create_enemies()
    direction = 1
    score = 0
    enemy_speed = 2
    player_lives = 3
    running = True

    while running:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= 7
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += 7
        if keys[pygame.K_SPACE] and len(bullets) < 5:
            bullets.append(pygame.Rect(player.centerx - 2, player.top, 4, 10))

        move_down = False
        for en in enemies:
            en.x += enemy_speed * direction
            if en.right >= WIDTH - 10 or en.left <= 10:
                move_down = True
        if move_down:
            direction *= -1
            for en in enemies:
                en.y += 20

        if enemies and random.randint(1, 40) == 1:
            shooter = random.choice(enemies)
            enemy_bullets.append(pygame.Rect(shooter.centerx - 2, shooter.bottom, 4, 10))

        for b in bullets[:]:
            b.y -= 8
            if b.bottom < 0:
                try:
                    bullets.remove(b)
                except ValueError:
                    pass
                continue
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
                continue

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
                player.x = WIDTH//2 - player.width//2
                if player_lives <= 0:
                    running = False
                    break

        for e in enemies:
            if e.bottom >= player.top:
                player_lives = 0
                running = False
                break

        if not enemies:
            enemies = create_enemies()

        update_stars()
        draw_background()
        pygame.draw.rect(screen, GREEN, player)
        for b in bullets:
            pygame.draw.rect(screen, WHITE, b)
        for eb in enemy_bullets:
            pygame.draw.rect(screen, BLUE, eb)
        for e in enemies:
            pygame.draw.rect(screen, RED, e)

        draw_text_left(f"Puntos: {score}", font_small, WHITE, 10, 10)
        life_text = f"Vida: {player_lives}"
        draw_text_left(life_text, font_small, WHITE, WIDTH - 160, 10)
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

    stop_music(fade_ms=400)
    result = game_over_screen_with_input(score)
    if result == "retry":
        main_game()
    else:
        return

# ------------------ Menu principal ------------------
def main_menu():
    play_music_with_fade(menu, menu_volume, fade_ms=400)
    loading_screen()

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

        for text, y, base_color in buttons:
            rect = pygame.Rect(WIDTH//2 - 140, y - 22, 280, 48)
            color = base_color
            if rect.collidepoint(mx, my):
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
                        play_music_with_fade(menu, menu_volume, fade_ms=400)
                    elif text == "PUNTUACIONES":
                        show_scores_screen()
                        play_music_with_fade(menu, menu_volume, fade_ms=400)
                    elif text == "AJUSTAR VOLUMEN":
                        adjust_volumes()
                        play_music_with_fade(menu, menu_volume, fade_ms=400)
                    elif text == "SALIR":
                        stop_music()
                        pygame.quit()
                        sys.exit()

# ------------------ Inicio ------------------
if __name__ == "__main__":
    main_menu()
