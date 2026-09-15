import random
import math
import numpy as np
import pygame
import pgzrun

WIDTH = 640
HEIGHT = 560

# 윈도우 한글 폰트 설정
pygame.font.init()
font_large = pygame.font.SysFont("malgungothic", 28, bold=True)
font_small = pygame.font.SysFont("malgungothic", 20, bold=True)
font_num = pygame.font.SysFont("malgungothic", 30, bold=True)

# 사운드 믹서 초기화 및 자체 효과음 생성 (별도 오디오 파일 불필요)
pygame.mixer.init(frequency=22050, size=-16, channels=2)

def make_tone(freq, duration=0.15, volume=0.3):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    buf = np.zeros((n_samples, 2), dtype=np.int16)
    max_amp = 32767 * volume
    for i in range(n_samples):
        # 감쇠 효과(페이드아웃) 적용
        decay = (1.0 - (i / n_samples))
        val = int(max_amp * decay * math.sin(2.0 * math.pi * freq * i / sample_rate))
        buf[i][0] = val
        buf[i][1] = val
    return pygame.sndarray.make_sound(buf)

# 정답(도-미-솔) / 오답(낮은 도) 효과음
snd_correct_1 = make_tone(523.25, 0.12)  # C5
snd_correct_2 = make_tone(659.25, 0.12)  # E5
snd_correct_3 = make_tone(783.99, 0.25)  # G5
snd_wrong = make_tone(220.00, 0.25, 0.2) # A3

def play_dingdong():
    snd_correct_1.play()
    clock.schedule_unique(lambda: snd_correct_2.play(), 0.10)
    clock.schedule_unique(lambda: snd_correct_3.play(), 0.20)

def play_wrong():
    snd_wrong.play()

# 상태 변수 (1~10 무작위)
count = random.randint(1, 10)
buttons = []
feedback = "사과가 모두 몇 개 있을까요?"
score = 0
can_click = True

# 1~10 숫자 버튼 생성 (2줄 x 5개)
# 윗줄: 1~5 / 아랫줄: 6~10
for i in range(10):
    row = i // 5
    col = i % 5
    bx = 65 + col * 105
    by = 405 + row * 65
    btn_rect = Rect((bx, by), (85, 52))
    buttons.append({'rect': btn_rect, 'val': i + 1})

def draw():
    screen.fill((246, 248, 252))
    
    # 상단 점수
    score_surf = font_small.render(f"점수: {score}점", True, (80, 80, 80))
    screen.surface.blit(score_surf, (WIDTH - score_surf.get_width() - 25, 20))
    
    # 상단 질문 및 안내 문구
    msg_surf = font_large.render(feedback, True, (40, 40, 40))
    screen.surface.blit(msg_surf, ((WIDTH - msg_surf.get_width()) // 2, 60))
    
    # 사과 그리기 (최대 5개씩 2줄로 정렬)
    for i in range(count):
        row = i // 5
        col = i % 5
        
        # 줄당 사과 개수에 따라 가운데 정렬
        items_in_row = min(count - row * 5, 5)
        start_x = (WIDTH - (items_in_row * 68)) // 2 + 34
        
        ax = start_x + col * 68
        ay = 160 + row * 85
        
        screen.draw.filled_circle((ax, ay), 24, (235, 65, 65))        # 사과 알
        screen.draw.filled_circle((ax + 5, ay - 26), 6, (45, 165, 65)) # 잎사귀
    
    # 숫자 버튼 그리기 (1~10)
    for btn in buttons:
        screen.draw.filled_rect(btn['rect'], (255, 215, 85))
        screen.draw.rect(btn['rect'], (215, 160, 40))
        
        num_surf = font_num.render(str(btn['val']), True, (30, 30, 30))
        nx = btn['rect'].x + (btn['rect'].width - num_surf.get_width()) // 2
        ny = btn['rect'].y + (btn['rect'].height - num_surf.get_height()) // 2
        screen.surface.blit(num_surf, (nx, ny))

def on_mouse_down(pos):
    global count, feedback, score, can_click
    
    if not can_click:
        return

    for btn in buttons:
        if btn['rect'].collidepoint(pos):
            if btn['val'] == count:
                score += 10
                feedback = "딩동댕! 정답이에요! 아주 잘했어요!"
                play_dingdong()
                can_click = False
                clock.schedule_unique(next_round, 1.3)
            else:
                feedback = "다시 한번 차근차근 세어볼까요?"
                play_wrong()

def next_round():
    global count, feedback, can_click
    count = random.randint(1, 10)
    feedback = "사과가 모두 몇 개 있을까요?"
    can_click = True

pgzrun.go()
