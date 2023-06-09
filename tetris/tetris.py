# -*- coding: Utf-8 -*-
'''Python 350'''
import copy
import time
import sys
import os
import json

class Level:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.array = get_array(width, height)

class Figures:
    def __init__(self, name):
        self.figures = []
        self.currentFigureNumber = 0
        
        self._get_figures(name)
        self._set_segment_count()
        #self._print_corrent()
        self._set_options_figures()
        self._set_step_count()
        self._sort()
        self._remove_rotates_and_flips_from_first_figure()
        
    @property
    def current_figure(self):
        return self.figures[self.currentFigureNumber]
        
    def forward(self):
        self.currentFigureNumber += 1
        
    def is_full(self):
        return self.currentFigureNumber == len(self.figures)
        
    def rollback(self):
        self._check_move_figure()
        self._backward()
        self.current_figure.clear()
        if self.current_figure.step() == "reset":
            if self.currentFigureNumber == 0:
                return "end"
                
            return self.rollback()
            
    def _get_figures(self, name):
        path = sys.path[0]
        folderName = "figures{0}".format(name)
        
        for number, fileName in enumerate(sorted(os.listdir(os.path.join(path, folderName)))):
            file = open(os.path.join(path, "{1}/{0}".format(fileName, folderName)))
            read = file.read()
            
            figureNumber = number + 1
            figure = Figure(self._get_array_from_text(read, figureNumber), figureNumber)
            self.figures.append(figure)
            
            file.close()
        
    def _get_array_from_text(self, text, number):
        array = []
        for i in text.split("\n"):
            row = []
            for symbol in i:
                row.append(number if symbol == "x" else 0)
                
            array.append(row)
            
        return array
        
    def _sort(self): #
        #если сначала реверснуть, а потом отсортировать - получится немного другое время. можно проверить эти результаты. (а точно ли другое получится?)
        
        #вот тут мы используем размеры только оригинальной фигуры, что не совсем верно.
        
        #reverse=True и reverse() дают разные результаты, поэтому это тоже надо учесть.
        
        #self.figures.sort(key=lambda figure: figure.height, reverse=True) #desc(9, 76) asc(288, 1164) 12x12(x, 26) #сортировка по высоте.
        #self.figures.sort(key=lambda figure: figure.width, reverse=True) #desc(20, 50) asc(682, 2649) 12x12(x, 34) #сортировка по ширине.
        #self.figures.sort(key=lambda figure: figure.width * figure.height, reverse=True) #desc(14, 20) asc(808, 3466) 12x12(x, 11)
        self.figures.sort(key=lambda figure: figure.width + figure.height) #desc(2, 18) asc(1061) 12x12(x, 8) #сортировка по периметру.
        #self.figures.sort(key=lambda figure: figure.width ** figure.height, reverse=True) #desc(18, 27) 12x12(x, 16)
        #self.figures.sort(key=lambda figure: figure.height ** figure.width, reverse=True) #desc(15, 22) 12x12(x, 15)
        self.figures.reverse()
        
        #self.figures.sort(key=lambda figure: figure.steps) #desc(1, 15) 12x12(x, 47) #сортировка по шагам.
        lol = 0 #чтобы метод закрывался в notepad.
        
    def _set_step_count(self): #
        #возможно лучше стоит просчитать сумму шагов каждого положения фигуры для steps count. сделать короче оба варианта.
        
        for figure in self.figures:
            while figure.step() != "reset":
                figure.steps += 1
                
    def _set_segment_count(self):
        for figure in self.figures:
            for row in figure.array:
                for value in row:
                    if value != 0:
                        figure.segments += 1
                    
    def _print_corrent(self):
        result = 0
        
        for figure in self.figures:
            result += figure.segments
            
        print(level.width * level.height, result)
        
    def _backward(self): #можно было объединить с rollback. и тогда уже переименовать rollback в backward.
        self.currentFigureNumber -= 1
        
    def _get_list_options_figure(self, array):
        def append(arrayAppend):
            buffer = get_crop_left_top_array(copy.deepcopy(arrayAppend))
            buffer = get_remove_right_zero_from_array(buffer)
            result.append(buffer)
            
        def fraud(arrayArg):
            append(arrayArg)
            result = arrayArg
            for i in range(3):
                result = get_rotate_array(result)
                
                '''if i == 1:
                    continue'''
                
                append(result)
                
            return result
            
        result = []
        
        arrayCopy = copy.deepcopy(array)
        append(arrayCopy)
        arrayCopy = fraud(arrayCopy)
        
        arrayCopy = get_reverse_array(arrayCopy)
        
        #arrayCopy = fraud(arrayCopy) #
        
        return result
        
    def _set_options_figures(self): #
        for figure in self.figures:
            listOptionsFigure = self._get_list_options_figure(figure.arraySquare)
            
            figuresSet = remove_duplicates(listOptionsFigure)
            
            for figureOption in figuresSet:
                figure.options.append(FigureOption(figureOption))
            
            figure.sort_options()
            
            #figure.options = [figure.options[0]] #чтобы был старый step без поворотов.
            
    def _check_move_figure(self):
        if self.currentFigureNumber == 2:
            print_data()
            
    def _remove_rotates_and_flips_from_first_figure(self):
        self.figures[0].options = [self.figures[0].options[0]]
        
class Figure:
    def __init__(self, array, number):
        self.array = array
        self.arraySquare = get_square_array(array)
        self.number = number
        self.steps = 0
        self.segments = 0
        
        self.width, self.height = get_size_array(self.array)
        
        self._reset_position()
        
        self.options = []
        self.optionNumber = 0
        
    @property
    def figure(self):
        return self.options[self.optionNumber].array
        
    @property
    def figureWidth(self):
        return self.options[self.optionNumber].width
        
    @property
    def figureHeight(self):
        return self.options[self.optionNumber].height
        
    def draw(self):
        for y, row in enumerate(self.figure):
            for x, value in enumerate(row):
                if value == 0:
                    continue
                
                level.array[y + self.y][x + self.x] = value
                
    def is_collision(self):
        for y, row in enumerate(self.figure):
            for x, value in enumerate(row):
                if value == 0:
                    continue
                
                if level.array[y + self.y][x + self.x] != 0:
                    return True
                    
    def step_original(self):
        self._move()
        
        if self._is_collision_left():
            self._move_row()
            
            if self._is_collision_bottom():
                self._reset_position()
                return "reset"
                
    def step(self):
        self._move()
        
        if self._is_collision_left():
            self._move_row()
            
            if self._is_collision_bottom():
                self._reset_position()
                
                if len(self.options) == 1:
                    return "reset"
                
                self.optionNumber += 1
                
                if self.optionNumber >= len(self.options):
                    self.optionNumber = 0
                    return "reset"
                
    def clear(self):
        for y, row in enumerate(self.figure):
            for x, value in enumerate(row):
                if value != 0:
                    level.array[y + self.y][x + self.x] = 0
                    
    def sort_options(self):
        #сортируем, чтобы всегда была одинаковая последовательность (set() возвращает случайную).
        self.options.sort(key=lambda option: option.array) 
        
        #сортируем, чтобы первая фигура в списке options становилась такая же как и оригинальная.
        self.options.sort(key=lambda option: option.array == self.array, reverse=True)
        
    def _is_collision_left(self):
        return (self.x + self.figureWidth) > level.width
        
    def _is_collision_bottom(self):
        return (self.y + self.figureHeight) > level.height
        
    def _reset_position(self):
        self.x = 0
        self.y = 0
        
    def _move(self):
        self.x += 1
        
    def _move_row(self):
        self.x = 0
        self.y += 1
        
class FigureOption:
    def __init__(self, array):
        self.array = array
        
        self.width, self.height = get_size_array(self.array)
        
def tick():
    global drawCount
    
    while figures.current_figure.is_collision():
        if figures.current_figure.step() != "reset":
            continue
            
        if figures.currentFigureNumber == 0:
            return "end"
        
        return figures.rollback()
    
    drawCount += 1
    figures.current_figure.draw() #<-- вот это можно поместить в класс Figures в метод forward().
    figures.forward()
    
def work():
    figuresCopy = figures.figures[:]

    figures.figures = []

    figures.figures.append(figuresCopy[9])
    figures.figures.append(figuresCopy[4])
    figures.figures.append(figuresCopy[6])
    figures.figures.append(figuresCopy[7])
    figures.figures.append(figuresCopy[0])
    figures.figures.append(figuresCopy[2])
    figures.figures.append(figuresCopy[8])
    figures.figures.append(figuresCopy[10])
    figures.figures.append(figuresCopy[1])
    figures.figures.append(figuresCopy[3])
    figures.figures.append(figuresCopy[5])

def print_level():
    levelCopy = copy.deepcopy(level.array)
    
    for y, row in enumerate(levelCopy):
        for x, value in enumerate(row):
            levelCopy[y][x] = " " if value == 0 else get_char(value)
            
    result = ['=' * level.width]
    
    for col in levelCopy:
        result.append("".join(col) + "|")
        
    result.append('=' * level.width)
    
    print("\n".join(result))

def print_time():
    t = time.time() - timeStart
    print('time: {0}:{1}:{2}'.format(str(int((t / 3600) % 24)).zfill(2), str(int((t / 60) % 60)).zfill(2), str(int(t % 60)).zfill(2)))
    
def print_draw_count():
    print('draw count:', drawCount)
    
def print_data():
    print_draw_count()
    print_time()
    print_level()
    
def get_size_array(array):
    height = len(array)
    width = 0
    for i in array:
        width = max(width, len(i))
        
    return width, height
    
def get_array(width, height):
    return [[0 for w in range(width)] for h in range(height)]
    
def get_rotate_array(array):
    width, height = get_size_array(array)
    
    result = get_array(width, height)
    
    for y, row in enumerate(array):
        for x, value in enumerate(row):
            result[width - 1 - x][y] = value
            
    return result
    
def get_remove_right_zero_from_array(array):
    def is_row_empty(row):
        for i in row:
            if i != 0:
                return False
                
        return True
    
    result = []
    
    for row in array:
        buffer = row[:]
        
        if is_row_empty(buffer):
            continue
        
        while buffer[-1] == 0:
            buffer.pop()
        
        result.append(buffer)
        
    return result
    
def get_crop_left_top_array(array):
    def is_left_empty():
        for row in result:
            if row[0] != 0:
                return False
                
        return True
    
    result = copy.deepcopy(array)
    
    while len(list(filter(lambda i: i != 0, result[0]))) == 0:
        result.pop(0)
        
    while is_left_empty():
        for row in result:
            row.pop(0)
        
    return result
    
def get_square_array(array):
    width, height = get_size_array(array)
    
    result = copy.deepcopy(array)
    
    for row in result:
        while len(row) < max(width, height): #max(width, height). это не ошибка, бывают случаи, когда это нужно.
            row.append(0)
            
    while len(result) < width:
        result.append([0 for x in range(width)])
        
    return result
    
def get_reverse_array(array):
    result = copy.deepcopy(array)
    
    for row in result:
        row.reverse()
        
    return result
    
def remove_duplicates(array):
    buffer = []
    
    for subArray in array:
        buffer.append(json.dumps(subArray))
        
    buffer = set(buffer)
    
    result = []
    
    for subArray in buffer:
        result.append(json.loads(subArray))

    return result
    
def get_char(number):
    return chr(number + 64)
    
def common():
    while tick() != "end":
        if figures.is_full():
            print_data()
            #print_draw_count()
            #print_time()
            
            #figures.rollback()
            break
            
    print_draw_count()
    
print('Start.')

timeStart = time.time()

level = Level(8, 6)
#level = Level(12, 12)
figures = Figures("1")

drawCount = 0

'''for figure in figures.figures:
    print(get_char(figure.number))'''
    
'''for figure in figures.figures:
    for row in figure.array:
        print(row)
        
    print()'''
    
'''for figure in figures.figures:
    for option in figure.options:
        for row in option.array:
            print(row)
            
        print()'''
        
'''for option in figures.figures[0].options:
    for row in option.array:
        print(row)
        
    print()'''
    
'''for figure in figures.figures:
    print(figure.steps, get_char(figure.number))'''

common()

r'''
<Notes>
    C:\Users\Wilson\AppData\Local\Programs\Python\Python35\python.exe -i "$(FULL_CURRENT_PATH)"
    
    мне кажется можно оптимизировать алгоритм, но я не знаю как. например, если я вижу, что после постановки первой фигуры - я не смогу заткнуть дырку - значит можно сразу двигать первую фигуру, таким образом сокращая кучу итераций.
    
    по хорошему я мог бы вынести некоторые методы из классов, которые являются общими.
    
    т.к. доска квадратная - можно делить количество решений на 4. потому что каждое решение это поворот его же на 90. поэтому я могу просто отключить вращение и флипы первой фигуры.
</Notes>

<Tasks>
    скорее всего, когда я сделаю повороты, у меня будет минимум два варианта: первый и второй, повёрнутый на 180 градусов. его можно убрать. ну тут скорее всего можно будет через уже готовую функцию remove_duplicates. но хотелось бы заранее не просчитывать дубликаты и остановить выполнение проги. кажется я понял. если у нас доска не квадратная, а прямоугольная, то стоит для первой фигуры сделать только два варианта: оригинальный и повёрнутый на 90 градусов. ещё я заметил, что на прямоугольной доске если у первой фигуры всего 2 варианта может быть, то ей достаточно дойти лишь до половины карты - остальное будет симметрично как при повороте на 180 градусов. (без utf-8 веерху файла этот коммент не даёт запуститься прогу.)
    
    попробовать ещё вывести параметры фигур и расставить фигуры вручную, исходя из следующих критериев:
    1. сначала те, которые самые большие по периметру.
    2. те, которым нужно меньше шагов на прохождение поля.
    
    сделать ещё чтобы логи в файл писало. всегда будет один файл с логами.
    
    level переименовать на table.
</Tasks>
'''
