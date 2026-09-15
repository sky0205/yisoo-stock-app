import random
import pgzrun

WIDTH = 600
HEIGHT = 500

# 상태 변수
count = random.randint(1, 5)
buttons = []
feedback = "사과가 몇 개 있을까요?"
score = 0

# 버튼 초기화 (1부터 5까지)
for i in range(5):
    btn_rect = Rect((60 + i * 100, 380), (80, 60))
    buttons.append({'rect': btn_rect, 'val': i + 1})

def draw():
    screen.fill((245, 248, 250))  # 부드러운 배경색
    
    # 상단 안내 및 점수
    screen.draw.text(f"점수: {score}점", topright=(560, 20), fontsize=28, color=(70, 70, 70))
    screen.draw.text(feedback, center=(WIDTH // 2, 70), fontsize=34, color=(40, 40, 40))
    
    # 사과(원형) 그리기
    start_x = (WIDTH - (count * 70)) // 2 + 35
    for i in range(count):
        x = start_x + i * 70
        y = 220
        screen.draw.filled_circle((x, y), 25, (230, 60, 60))       # 사과 알
        screen.draw.filled_circle((x + 6, y - 28), 6, (40, 160, 60)) # 사과 잎
    
    # 하단 숫자 버튼 그리기
    for btn in buttons:
        screen.draw.filled_rect(btn['rect'], (255, 210, 80))
        screen.draw.rect(btn['rect'], (210, 160, 40))
        screen.draw.text(str(btn['val']), center=btn['rect'].center, fontsize=36, color=(30, 30, 30))

def on_mouse_down(pos):
    global count, feedback, score
    
    for btn in buttons:
        if btn['rect'].collidepoint(pos):
            if btn['val'] == count:
                score += 10
                feedback = "딩동댕! 정답이에요! 참 잘했어요!"
                clock.schedule_unique(next_round, 1.2)
            else:
                feedback = "다시 한번 천천히 세어볼까요?"

def next_round():
    global count, feedback
    count = random.randint(1, 5)
    feedback = "사과가 몇 개 있을까요?"

pgzrun.go()
