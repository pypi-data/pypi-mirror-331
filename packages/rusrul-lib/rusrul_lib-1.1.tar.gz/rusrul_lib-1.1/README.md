# Russian Roulette Lib
*Документация на русском ниже*
### Installing
`pip install rusrul_lib`
### Using
`import rusrul_lib`
OR (recommended):
`from rusrul_lib import *`
### Features
Revolver can have different ammo count and clip size. Here are different ways to create the same 1/6 revolver:
```py
rev1 = revolver()
rev2 = revolver(1, 6)
rev3 = revolver(clipSize=6)
```
Revolver has it's own clip. It is used to determine the next shooting attempt. There are different ways to check the clip. You can just get it as array or have a custom representation.
```py
rev = revolver()
print(rev.clip)   # [1, 0, 0, 0, 0, 0] - position of "1" (bullet) is random
print(rev)   # "#....."
rev.strAmmo = "A"   # change the way ammo is printed
rev.strEmpty = "-"   # change the way empty slot is printed
print(rev)   # "A-----"
rev.reprVisualise = False   # disable visual representation
print(rev)   # "revolver(1, 6) = [1, 0, 0, 0, 0, 0]"
```
Main functions:
- `revolver.shoot()` - makes a shot, returning the first item in clip and replacing it with 0.
- `revolver.spin(spinPower)` - spins the clip. Spin power becomes random if 0 or unless given as argumen. Supports negative values.
- `revolver.load(pattern)` - reloads revolver with given pattern. Loads full ammo by default. Can accept values different from 1 and 0, if your code can handle other ammo types. Takes pattern as string and converts it into array of ints used as new clip.
- `revolver.ammoCount()` - counts all values except 0 in clip.

Advanced usage:
- `revolver.allowStrPattern = True` - Makes load() funcion not convert pattern to ints. If enabled, turns off ammoCount() and onShoot. \_\_str\_\_() returns clip directly instead of using strAmmo and strEmpty. Can be buggy.
- `revolver.onShoot = "print('Hello world')"` - Custom piece of code that will be executed when revolver.shoot() returns non-zero value.

## На русском
### Установка
Ну я надеюсь ты знаешь как скачивать библиотеки, раз уж зашёл на PyPI.
`pip install rusrul_lib`
Там буквально в левом верхнем углу написано.
### Использование
Просто берёшь и импортируешь, что сложного?
`import rusrul_lib`
ИЛИ (советую):
`from rusrul_lib import *`
### Функционал
У револьвера есть барабан. В барабане есть патроны. Логично? Одинаковые револьверы 1/6 можно создать вот так:
```py
rev1 = revolver()
rev2 = revolver(1, 6)
rev3 = revolver(clipSize=6)
```
У каждого револьвера свой барабан. Револьвер стреляет первым патроном в барабане и никаким другим. Подсмотреть можно, хоть и это убирает весь интерес настоящей русской рулетки:
```py
rev = revolver()
print(rev.clip)   # [1, 0, 0, 0, 0, 0] - не всегда пуля будет первая. Но у тебя будет
print(rev)   # "#....."
rev.strAmmo = "A"   # Поменять как показываются патроны
rev.strEmpty = "-"   # Поменять как показывается пустая ячейка
print(rev)   # "A-----"
rev.reprVisualise = False   # Выключить визуал
print(rev)   # "revolver(1, 6) = [1, 0, 0, 0, 0, 0]"
```
Основные функции:
- `revolver.shoot()` - делает выстрел и возвращает первый патрон из барабана, заменяя его на 0.
- `revolver.spin(spinPower)` - крутит барабан. Сила прокрута случайная если равна 0, или если не задана.
- `revolver.load(pattern)` - перезаряжает револьвер по заданному паттерну. Заряжает полный барабан, если паттерн не задан. Принимает не только 0 и 1, если ваш код допускает другие виды патронов. Принимает паттерн в виде строки и конвертирует его в массив чисел.
- `revolver.ammoCount()` - считает все цифры кроме 0 в барабане.

Продвинутое использование:
- `revolver.allowStrPattern = True` - Выключает конвертирование в числа у функции load(). Также отключает ammoCount() и onShoot. \_\_str\_\_() возвращает барабан, игрорируя strAmmo и strEmpty. Может вызывать баги.
- `revolver.onShoot = "print('Hello world')"` - Кастомный кусок кода, который будет выполняться если revolver.shoot() возвращает не 0.