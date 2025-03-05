![Компания Эталон](https://omsketalon.ru/sites/default/files/logo_s_0.png)

<br>
<h1>Калибратор КС-1200С</h1>

Данный пакет предназначен для рабооты калибратора сухоблочного КС-1200С компании Эталон.
<br><br><br>
1. <h1>Установка</h1>
2. <h1>Обновление</h1>

1. Установка
   1.1. Пошаговая установка на чистую систему.
   1.1.1. Записываем обновленный образ системы из папки [Armbian чистые образы](https://disk.yandex.ru/d/-d6GdyGaJy6reQ) на флешку. Для записи удобно использовать [Rufus](https://rufus.ie/ru/). Можно записать образ сразу с клаиватурой, тогда последующие шаги не нужны.<br>
   пароль SU: try123!
1. Обновляем систему:<br>
    sudo apt update<br>
    sudo apt upgrade
2. Устанавливаем необходимые пакеты:<br>
    sudo apt install python3-pyqt5 python-is-python3 qtdeclarative5-dev libqt5svg5-dev qtbase5-private-dev qml-module-qtquick-controls2 qml-module-qtquick-controls qml-module-qt-labs-folderlistmodel<br>
    sudo apt install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev
3. Загружаем исходники виртуальной клавиатуры QT, собираем её с нужными языками и устанавливаем:<br>
    git clone -b 5.11 https://github.com/qt/qtvirtualkeyboard.git<br>
    cd qtvirtualkeyboard<br>
    qmake "CONFIG += lang-en lang-ru"<br>
    sudo make<br>
    sudo make install
4. Устанавливаем данный пакет калибратора:<br>
    pip install calibrator-ks1200
<br><br><br>
<h2> Ссылки </h2>

- [Компания эталон](http://www.omsketalon.ru/)
- [GitHUB](https://github.com/psih0/KS1200)
<br><br><br>
## Лицензия

Лицензия MIT
