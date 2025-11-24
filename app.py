import sys
import cv2
import mediapipe as mp
import numpy as np
import random
import time
from config import config


# ================================================================
# ------------------- CONFIGURACIÓN MEDIAPIPE --------------------
# ================================================================
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=config.model_path),
    running_mode=VisionRunningMode.VIDEO,
    num_poses=1
)


# ================================================================
# --------------------- OBJETOS QUE CAEN -------------------------
# ================================================================
class FallingObject:
    def __init__(self, obj_type, x, speed, images):
        self.obj_type = obj_type
        self.x = x
        self.y = 0
        self.speed = speed
        self.image = images[obj_type]

        self.radius = int(max(self.image.shape[0], self.image.shape[1]) / 2) - 5

    def move(self):
        self.y += self.speed

    def draw(self, frame):
        img_h, img_w, _ = self.image.shape
        x1 = int(self.x - img_w / 2)
        y1 = int(self.y - img_h / 2)
        x2 = x1 + img_w
        y2 = y1 + img_h

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(frame.shape[1], x2)
        y2 = min(frame.shape[0], y2)

        img_x1 = 0
        img_y1 = 0
        if x1 == 0 and self.x - img_w / 2 < 0:
            img_x1 = int(-(self.x - img_w / 2))
        if y1 == 0 and self.y - img_h / 2 < 0:
            img_y1 = int(-(self.y - img_h / 2))

        img_to_draw = self.image[img_y1:img_y1+(y2-y1), img_x1:img_x1+(x2-x1)]

        if img_to_draw.shape[0] > 0 and img_to_draw.shape[1] > 0:
            roi = frame[y1:y2, x1:x2]

            if img_to_draw.shape[2] == 4:
                alpha_s = img_to_draw[:, :, 3] / 255.0
                alpha_l = 1.0 - alpha_s
                for c in range(0, 3):
                    roi[:, :, c] = alpha_s * img_to_draw[:, :, c] + alpha_l * roi[:, :, c]
            else:
                frame[y1:y2, x1:x2] = img_to_draw


def calculate_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)



# ================================================================
# ------------------ MENÚ EN CÁMARA (DIFICULTAD) -----------------
# ================================================================
BTN_EASY_REL   = (0.12, 0.15, 0.88, 0.30)
BTN_MEDIUM_REL = (0.12, 0.36, 0.88, 0.51)
BTN_HARD_REL   = (0.12, 0.57, 0.88, 0.72)
HOVER_TIME_REQUIRED = 1.5


def rect_from_rel(rel, w, h):
    x1 = int(rel[0] * w)
    y1 = int(rel[1] * h)
    x2 = int(rel[2] * w)
    y2 = int(rel[3] * h)
    return (x1, y1, x2, y2)


def draw_menu_overlay(frame, buttons, hovered_btn_name=None, hover_progress=0.0):
    overlay = frame.copy()
    h, w, _ = frame.shape
    
    alpha = 0.6

    menu_x1 = int(0.08 * w)
    menu_y1 = int(0.10 * h)
    menu_x2 = int(0.92 * w)
    menu_y2 = int(0.78 * h)
    cv2.rectangle(overlay, (menu_x1, menu_y1), (menu_x2, menu_y2), (20, 20, 20), -1)
    
    cv2.putText(overlay, "Selecciona dificultad con la mano",
                (int(0.12*w), int(0.13*h)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)

    for name, rect in buttons.items():
        x1, y1, x2, y2 = rect

        cv2.rectangle(overlay, (x1, y1), (x2, y2), (255,255,255), 2)

        txt = name
        (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        tx = x1 + (x2 - x1)//2 - tw//2
        ty = y1 + (y2 - y1)//2 + th//2
        cv2.putText(overlay, txt, (tx, ty),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                    (255,255,255), 2)

        if hovered_btn_name == name:
            bar_w = int((x2 - x1) * min(1.0, hover_progress))
            cv2.rectangle(overlay, (x1, y2 - 10), (x1 + bar_w, y2 - 2), (255,255,255), -1)

    return cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0)



def run_menu_with_hand_selection(landmarker, cap, frame_ms, current_ts):
    hovered_button = None
    hover_start = None

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = landmarker.detect_for_video(mp_image, int(current_ts))
        current_ts += frame_ms

        right_hand = left_hand = None

        if result.pose_landmarks:
            person_landmarks = result.pose_landmarks[0]
            try:
                right_w = person_landmarks[20]
                left_w = person_landmarks[19]
                right_hand = (int(right_w.x * w), int(right_w.y * h))
                left_hand = (int(left_w.x * w), int(left_w.y * h))
            except:
                pass

        buttons = {
            'FACIL': rect_from_rel(BTN_EASY_REL, w, h),
            'MEDIO': rect_from_rel(BTN_MEDIUM_REL, w, h),
            'DIFICIL': rect_from_rel(BTN_HARD_REL, w, h)
        }

        hand_point = right_hand or left_hand
        current_hover = None

        if hand_point:
            hx, hy = hand_point
            cv2.circle(frame, (hx, hy), 10, (0,255,255), -1)

            for name, rect in buttons.items():
                x1, y1, x2, y2 = rect
                if x1 <= hx <= x2 and y1 <= hy <= y2:
                    current_hover = name
                    break

        hover_progress = 0.0

        if current_hover:
            if hovered_button == current_hover:
                if hover_start is None: hover_start = time.time()
                elapsed = time.time() - hover_start
                hover_progress = elapsed / HOVER_TIME_REQUIRED
                if elapsed >= HOVER_TIME_REQUIRED:
                    mul = {'FACIL':0.6,'MEDIO':1.0,'DIFICIL':1.5}[current_hover]
                    return mul, current_ts
            else:
                hovered_button = current_hover
                hover_start = time.time()
        else:
            hovered_button = None
            hover_start = None

        frame_menu = draw_menu_overlay(frame, buttons, hovered_button, hover_progress)
        cv2.putText(frame_menu, "Coloca tu mano durante 1s para seleccionar",
                    (int(0.1*w), int(0.85*h)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 2)

        cv2.imshow("Falling Objects Pose Game", frame_menu)

        if cv2.waitKey(1) & 0xFF == 27:
            sys.exit()



# ================================================================
# ------------------ MENÚ DE DURACIÓN ----------------------------
# ================================================================
def draw_duration_menu_overlay(frame, buttons, hovered_btn_name=None, hover_progress=0.0):
    overlay = frame.copy()
    h, w, _ = frame.shape
    alpha = 0.6

    # fondo
    cv2.rectangle(overlay, (int(0.08*w), int(0.10*h)),
                  (int(0.92*w), int(0.78*h)), (20,20,20), -1)

    cv2.putText(overlay, "Selecciona duracion del juego",
                (int(0.12*w), int(0.13*h)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)

    for name, rect in buttons.items():
        x1,y1,x2,y2 = rect
        cv2.rectangle(overlay,(x1,y1),(x2,y2),(255,255,255),2)

        (tw,th),_ = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX,1,2)
        tx = x1+(x2-x1)//2 - tw//2
        ty = y1+(y2-y1)//2 + th//2
        cv2.putText(overlay,name,(tx,ty),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)

        if hovered_btn_name==name:
            bar_w = int((x2-x1)*min(1.0,hover_progress))
            cv2.rectangle(overlay,(x1,y2-10),(x1+bar_w,y2-2),(255,255,255),-1)

    return cv2.addWeighted(overlay,alpha,frame,1-alpha,0)



def run_menu_for_duration(landmarker, cap, frame_ms, current_ts):
    hovered = None
    hover_start = None

    while True:
        ret, frame = cap.read()
        if not ret: continue

        frame=cv2.flip(frame,1)
        h,w,_=frame.shape

        mp_img=mp.Image(image_format=mp.ImageFormat.SRGB,data=frame)
        result=landmarker.detect_for_video(mp_img,int(current_ts))
        current_ts+=frame_ms

        right_hand=left_hand=None
        if result.pose_landmarks:
            L=result.pose_landmarks[0]
            try:
                right_hand=(int(L[20].x*w),int(L[20].y*h))
                left_hand =(int(L[19].x*w),int(L[19].y*h))
            except: pass

        btns={
            '30 SEG':rect_from_rel(BTN_EASY_REL,w,h),
            '60 SEG':rect_from_rel(BTN_MEDIUM_REL,w,h),
            '90 SEG':rect_from_rel(BTN_HARD_REL,w,h)
        }

        hand=right_hand or left_hand
        current=None

        if hand:
            hx,hy=hand
            cv2.circle(frame,(hx,hy),10,(0,255,255),-1)
            for name,r in btns.items():
                if r[0]<=hx<=r[2] and r[1]<=hy<=r[3]:
                    current=name
                    break

        progress=0
        if current:
            if hovered==current:
                if hover_start is None: hover_start=time.time()
                elapsed=time.time()-hover_start
                progress=elapsed/HOVER_TIME_REQUIRED
                if elapsed>=HOVER_TIME_REQUIRED:
                    return {'30 SEG':30,'60 SEG':60,'90 SEG':90}[current], current_ts
            else:
                hovered=current
                hover_start=time.time()
        else:
            hovered=None
            hover_start=None

        out=draw_duration_menu_overlay(frame,btns,hovered,progress)
        cv2.putText(out,"Mantén la mano 1s para seleccionar",
                    (int(0.1*w),int(0.85*h)),cv2.FONT_HERSHEY_SIMPLEX,0.7,(200,200,200),2)
        cv2.imshow("Falling Objects Pose Game",out)

        if cv2.waitKey(1)&0xFF==27:
            sys.exit()



# ================================================================
# ------------------ NUEVO MENÚ DE MODO ---------------------------
# ================================================================
def draw_mode_menu_overlay(frame, buttons, hovered_btn_name=None, hover_progress=0.0):
    overlay = frame.copy()
    h, w, _ = frame.shape
    alpha = 0.6

    cv2.rectangle(overlay, (int(0.08*w), int(0.10*h)),
                  (int(0.92*w), int(0.78*h)), (20,20,20), -1)

    cv2.putText(overlay, "Selecciona modo de juego",
                (int(0.12*w), int(0.13*h)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)

    for name, rect in buttons.items():
        x1, y1, x2, y2 = rect
        cv2.rectangle(overlay,(x1,y1),(x2,y2),(255,255,255),2)

        (tw, th), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        tx = x1 + (x2-x1)//2 - tw//2
        ty = y1 + (y2-y1)//2 + th//2
        cv2.putText(overlay, name, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

        if hovered_btn_name == name:
            bar_w = int((x2-x1)*min(1.0, hover_progress))
            cv2.rectangle(overlay,(x1,y2-10),(x1+bar_w,y2-2),(255,255,255),-1)

    return cv2.addWeighted(overlay, alpha, frame, 1-alpha, 0)



def run_menu_for_mode(landmarker, cap, frame_ms, current_ts):
    hovered = None
    hover_start = None

    while True:
        ret, frame = cap.read()
        if not ret: continue

        frame = cv2.flip(frame,1)
        h,w,_ = frame.shape

        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = landmarker.detect_for_video(mp_img, int(current_ts))
        current_ts += frame_ms

        right_hand = left_hand = None
        if result.pose_landmarks:
            L = result.pose_landmarks[0]
            try:
                right_hand=(int(L[20].x*w),int(L[20].y*h))
                left_hand =(int(L[19].x*w),int(L[19].y*h))
            except: pass

        buttons = {
            "SOLO MANOS": rect_from_rel(BTN_EASY_REL, w, h),
            "CUERPO ENTERO": rect_from_rel(BTN_MEDIUM_REL, w, h)
        }

        hand = right_hand or left_hand
        current = None

        if hand:
            hx,hy = hand
            cv2.circle(frame,(hx,hy),10,(0,255,255),-1)
            for name, r in buttons.items():
                if r[0]<=hx<=r[2] and r[1]<=hy<=r[3]:
                    current = name
                    break

        progress = 0
        if current:
            if hovered == current:
                if hover_start is None: hover_start = time.time()
                elapsed = time.time() - hover_start
                progress = elapsed / HOVER_TIME_REQUIRED
                if elapsed >= HOVER_TIME_REQUIRED:
                    return current, current_ts
            else:
                hovered = current
                hover_start = time.time()
        else:
            hovered = None
            hover_start = None

        out = draw_mode_menu_overlay(frame, buttons, hovered, progress)
        cv2.putText(out, "Mantén tu mano 1s para seleccionar",
                    (int(0.1*w), int(0.85*h)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 2)
        cv2.imshow("Falling Objects Pose Game", out)

        if cv2.waitKey(1)&0xFF == 27:
            sys.exit()



# ================================================================
# -------------------------- JUEGO -------------------------------
# ================================================================
with PoseLandmarker.create_from_options(options) as landmarker:

    cap = cv2.VideoCapture(0)
    ret_init, frame_init = cap.read()
    if not ret_init:
        print("Error cámara.")
        sys.exit()

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0: fps = 30
    frame_ms = int(1000/fps)
    timestamp = 0

    # ---------------- MENÚ DIFICULTAD ----------------
    speed_multiplier, timestamp = run_menu_with_hand_selection(landmarker, cap, frame_ms, timestamp)

    # ---------------- MENÚ DURACIÓN -------------------
    game_duration, timestamp = run_menu_for_duration(landmarker, cap, frame_ms, timestamp)

    # ---------------- MENÚ MODO NUEVO -----------------
    game_mode, timestamp = run_menu_for_mode(landmarker, cap, frame_ms, timestamp)
    use_full_body = (game_mode == "CUERPO ENTERO")


    # ---------------- INICIALIZACIÓN ------------------
    counter = 0
    start_time = time.time()
    objects = []

    try:
        images = {
            'manzana': cv2.imread('manzanas.png', cv2.IMREAD_UNCHANGED),
            'pera': cv2.imread('pera.png', cv2.IMREAD_UNCHANGED),
            'balon': cv2.imread('balon.png', cv2.IMREAD_UNCHANGED)
        }

        if any(img is None for img in images.values()):
            raise FileNotFoundError("Error cargando imágenes.")

        target_size = (100,100)
        for key in images:
            images[key] = cv2.resize(images[key], target_size)
    except:
        sys.exit()



    # ======================= LOOP DE JUEGO =======================
    while cap.isOpened():

        ret, frame = cap.read()
        if not ret: break

        frame = cv2.flip(frame,1)
        h,w,_ = frame.shape

        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = landmarker.detect_for_video(mp_img, timestamp)
        timestamp += frame_ms

        right_hand = left_hand = right_foot = left_foot = None

        if result.pose_landmarks:
            for person in result.pose_landmarks:
                for idx, lm in enumerate(person):
                    x,y = int(lm.x*w), int(lm.y*h)

                    # dibujo original intacto
                    if idx in [15,17,19,21]:
                        cv2.circle(frame,(x,y),6,(0,255,0),-1)
                    elif idx in [16,18,20,22]:
                        cv2.circle(frame,(x,y),6,(0,0,255),-1)
                    elif idx in [27,28,31,32]:
                        cv2.circle(frame,(x,y),6,(255,0,0),-1)

                try:
                    right_hand = (int(person[20].x*w), int(person[20].y*h))
                    left_hand  = (int(person[19].x*w), int(person[19].y*h))
                    right_foot = (int(person[32].x*w), int(person[32].y*h))
                    left_foot  = (int(person[31].x*w), int(person[31].y*h))
                except:
                    pass


        # --- Generar objetos ---
        if random.random() < 0.03:

            if not use_full_body:
                # solo manos → solo frutas
                obj_type = random.choice(['manzana','pera'])
            else:
                # cuerpo entero → frutas + balones
                r=random.random()
                if r < 0.33: obj_type='manzana'
                elif r < 0.66: obj_type='pera'
                else: obj_type='balon'

            x = random.randint(40, w-40)
            speed = random.uniform(2,6)*speed_multiplier
            objects.append(FallingObject(obj_type, x, speed, images))


        # --- Actualizar objetos ---
        new_objs=[]
        for obj in objects:
            obj.move()
            obj.draw(frame)

            if obj.y > h:
                continue

            caught=False

            if right_hand and obj.obj_type=='manzana':
                if calculate_distance((obj.x,obj.y), right_hand) < obj.radius:
                    caught=True
                    counter+=1

            elif left_hand and obj.obj_type=='pera':
                if calculate_distance((obj.x,obj.y), left_hand) < obj.radius:
                    caught=True
                    counter+=1

            elif use_full_body and obj.obj_type=='balon':
                if left_foot and calculate_distance((obj.x,obj.y), left_foot) < obj.radius:
                    caught=True
                    counter+=1
                elif right_foot and calculate_distance((obj.x,obj.y), right_foot) < obj.radius:
                    caught=True
                    counter+=1

            if not caught:
                new_objs.append(obj)

        objects=new_objs

        # HUD
        elapsed = time.time() - start_time
        remaining = max(0, game_duration - elapsed)

        cv2.putText(frame,f"Time: {remaining:.1f}  Points: {counter}",
                    (10,40),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)

        # fin de juego
        if remaining <= 0:
            frame[:] = 0
            cv2.putText(frame,f"Final Score: {counter}",(int(w/3),int(h/2)),
                        cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,255,0),3)

            cv2.putText(frame,"Press ENTER to restart or ESC to exit",
                        (int(w/6),int(h/2+60)),
                        cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,255),2)

            cv2.imshow("Falling Objects Pose Game", frame)

            while True:
                key=cv2.waitKey(1)&0xFF
                if key==13:
                    speed_multiplier,timestamp = run_menu_with_hand_selection(landmarker,cap,frame_ms,timestamp)
                    game_duration,timestamp = run_menu_for_duration(landmarker,cap,frame_ms,timestamp)
                    game_mode,timestamp = run_menu_for_mode(landmarker,cap,frame_ms,timestamp)
                    use_full_body = (game_mode=="CUERPO ENTERO")
                    counter=0
                    objects=[]
                    start_time=time.time()
                    break

                elif key==27:
                    cap.release()
                    cv2.destroyAllWindows()
                    sys.exit()

        else:
            cv2.imshow("Falling Objects Pose Game", frame)
            if cv2.waitKey(1)&0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

