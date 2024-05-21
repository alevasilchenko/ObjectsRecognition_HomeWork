import cv2
import numpy as np

cap = cv2.VideoCapture(0)  # получаем видео с веб-камеры ноутбука

height = int(cap.get(4))  # запрашиваем высоту изображения
width = int(cap.get(3))  # запрашиваем ширину изображения

cascade = cv2.CascadeClassifier('eyes.xml')  # используем рекомендуемый в ТЗ каскад Хаара

# Создаём 3-слойную матрицу, идентичную размерности видеопотока.
# В каждый из её слоёв будет записан очередной кадр видео в сером формате.
# Так сделано для совместимости массивов цветного и серого изображения при их наложении друг на друга.
gray3_img = np.zeros((height, width, 3), dtype='uint8')

while True:
    success, color_img = cap.read()  # считываем очередной кадр видеопотока
    gray_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)  # преобразуем его в оттенки серого
    eyes = cascade.detectMultiScale(gray_img, scaleFactor=1.15, minNeighbors=20)  # распознавание глаз

    x_min, y_min = width, height  # задаём начальные минимальные значения (x, y) заведомо большими
    x_max, y_max = 0, 0  # задаём начальные максимальные значения (x, y) заведомо меньшими
    for (x1, y1, w, h) in eyes:  # осуществляем перебор найденных координат с целью выделения единой области глаз
        x2 = x1 + w
        y2 = y1 + h
        if x1 < x_min:
            x_min = x1
        if y1 < y_min:
            y_min = y1
        if x2 > x_max:
            x_max = x2
        if y2 > y_max:
            y_max = y2

    delta_x = x_max - x_min  # размер найденной области глаз по ширине
    delta_y = y_max - y_min  # размер найденной области глаз по высоте

    # далее расширяем найденную область (согласно ТЗ) в каждом направлении (в нашем случае на 10%)
    x_min = x_min - round(0.1 * delta_x)
    y_min = y_min - round(0.1 * delta_y)
    x_max = x_max + round(0.1 * delta_x)
    y_max = y_max + round(0.1 * delta_y)

    for i in range(3):
        gray3_img[:, :, i] = gray_img  # записываем изображение в оттенках серого в 3-слойную матрицу

    # далее предварительно размытый фрагмент серого изображения, соответствующий найденной на кадре области глаз,
    # передаётся в соответствующие элементы матрицы цветного изображения;
    # поскольку при моргании возникала ошибка функции размытия "пустого" изображения (глаза не распознавались),
    # то на данном этапе проверялось возникновение исключительной ситуации:
    try:
        color_img[y_min:y_max, x_min:x_max] = cv2.GaussianBlur(gray3_img[y_min:y_max, x_min:x_max], (111, 11), 0)
    except Exception:
        pass

    cv2.imshow('Blured eyes', color_img)  # вывод цветного кадра с "заретушированным взглядом" в оттенках серого

    key = cv2.waitKey(1)
    if key == ord('q'):  # цикл завершится при нажатии клавиши q
        break