import time
import sqlite3
import sys
import random
from PyQt5.QtCore import QObject, QTimer, QTime, Qt, QDate
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QTextCharFormat, QIcon
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from threading import Timer
from PIL import ImageGrab
import datetime
from datetime import datetime, timedelta
import webbrowser
import setting_rc

home_ui = uic.loadUiType("home.ui")[0]
calendar_ui = uic.loadUiType("calendar.ui")[0]

window_width = 700
window_height = 500
toolbar_width = 70
toolbar_height = 510
rect_width = window_width - toolbar_width
rect_height = window_height
max_window = 500

DataBase = "./data/"  # DB 경로
DBfile = "conaTimetable.db"

cafe_url = 'https://cafe.naver.com/conatimetable'

advice_list = ["수업 시간은 공부 시간에 포함하지 않는 것이 좋습니다.",
               "강의를 듣는 시간과 학습 시간은 다르게 생각하는 것이 좋습니다."
               "공부를 정각에 맞춰서 시작하는 습관은 고치는 것이 좋습니다.",
               "무리한 공부 계획을 세우는 건 비효율적인 행동입니다.\n실천할 수 있는 계획을 세웁시다.",
               "공부할 때에는 스마트폰과 같은 전자기기를 멀리하는 것이 좋습니다.",
               "휴식은 시간을 정해놓고 쉬는 것이 좋습니다.",
               "목표를 글로 적는 습관을 들이면 학업 수행 능력이 향상됩니다.",
               "오래 앉아있는 것 만이 능사는 아닙니다.\n하고 있는 것에 집중합시다."
               ]


class Form(QWidget):
    def __init__(self):
        QWidget.__init__(self, flags=Qt.Widget)
        self.stack = QStackedWidget(self)
        self.stack.setGeometry(70, 0, window_width, window_height)
        self.init_widget()

    def init_widget(self):
        self.resize(window_width, max_window)
        self.setMinimumSize(QtCore.QSize(window_width, window_height))
        self.setMaximumSize(QtCore.QSize(window_width, max_window))
        self.setWindowTitle("CONA")
        self.setWindowIcon(QIcon('conalogo.png'))

        self.group = QtWidgets.QButtonGroup(self)

        self.line = QtWidgets.QFrame(self)
        self.line.setGeometry(QtCore.QRect(60, -10, 16, 931))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        self.calendar_tab_bt = QtWidgets.QToolButton(self)
        self.calendar_tab_bt.setGeometry(QtCore.QRect(20, 80, 31, 31))
        self.calendar_tab_bt.setStyleSheet("border-image: url(:/icon/calendar.png);")
        self.calendar_tab_bt.setText("")
        self.calendar_tab_bt.setObjectName("calrendar_tab_bt")

        self.timetable_tab_bt = QtWidgets.QToolButton(self)
        self.timetable_tab_bt.setGeometry(QtCore.QRect(20, 140, 31, 31))
        self.timetable_tab_bt.setStyleSheet("border-image: url(:/icon/timetable.png);")
        self.timetable_tab_bt.setText("")
        self.timetable_tab_bt.setObjectName("timetable_tab_bt")

        self.recode_tab_bt = QtWidgets.QToolButton(self)
        self.recode_tab_bt.setGeometry(QtCore.QRect(20, 200, 31, 31))
        self.recode_tab_bt.setStyleSheet("border-image: url(:/icon/clock.png);")
        self.recode_tab_bt.setText("")
        self.recode_tab_bt.setObjectName("recode_tab_bt")

        self.cafe_tab_bt = QtWidgets.QToolButton(self)
        self.cafe_tab_bt.setGeometry(QtCore.QRect(20, 260, 31, 31))
        self.cafe_tab_bt.setStyleSheet("border-image: url(:/icon/cafe.png);")
        self.cafe_tab_bt.setText("")
        self.cafe_tab_bt.setObjectName("cafe_tab_bt")

        self.home_tab_bt = QtWidgets.QToolButton(self)
        self.home_tab_bt.setGeometry(QtCore.QRect(20, 20, 31, 31))
        self.home_tab_bt.setStyleSheet("border-image: url(:/icon/home.png);")
        self.home_tab_bt.setText("")
        self.home_tab_bt.setObjectName("home_tab_bt")

        self.setting_tab_bt = QtWidgets.QToolButton(self)
        self.setting_tab_bt.setGeometry(QtCore.QRect(20, 320, 31, 31))
        self.setting_tab_bt.setStyleSheet("border-image: url(:/icon/set.png);")
        self.setting_tab_bt.setText("")
        self.setting_tab_bt.setObjectName("setting_tab_bt")

        self.group.addButton(self.home_tab_bt, 0)
        self.group.addButton(self.timetable_tab_bt, 1)
        self.group.addButton(self.calendar_tab_bt, 2)
        self.group.addButton(self.recode_tab_bt, 3)
        self.group.addButton(self.cafe_tab_bt, 4)
        self.group.addButton(self.setting_tab_bt, 5)

        self.stack.addWidget(home())
        self.stack.addWidget(timetable_page())
        self.stack.addWidget(Calendar())
        self.stack.addWidget(recode())
        self.stack.addWidget(cafe())
        self.stack.addWidget(setting())

        # 시그널 슬롯 연결
        self.group.buttonClicked[int].connect(self.stack.setCurrentIndex)


class setting(QWidget):
    def __init__(self):
        super().__init__()
        self.set = QtWidgets.QWidget()  # 설정
        self.set.setGeometry(0, 0, rect_width - 20, 650)

        # ============================================설정 페이지==================================================

        # self.alarm_set_start   수업 시작 알림 사용여부
        # self.alarm_set_10      수업 10분 전 알림 사용 여부
        # self.study_advice      조언 사용 여부
        self.alarm_set_10, self.alarm_set_start, self.study_advice = self.get_setting()

        self.guide = QtWidgets.QLabel("※모든 설정 변경은 프로그램을 재시작 해야 반영됩니다※", self)
        self.guide.setStyleSheet("color: #E57373")
        self.guide.move(int(rect_width / 2) - 160, 300)

        self.before_alarm = QtWidgets.QCheckBox("시작 10분 전 알림", self)  # 시작 전 알림 설정
        self.before_alarm.setGeometry(int(rect_width / 3) - 60, int(rect_height / 10), 120, 50)
        if self.alarm_set_10:
            self.before_alarm.toggle()
        self.before_alarm.stateChanged.connect(self.set_before)

        self.start_alarm = QtWidgets.QCheckBox("시작 때 알림", self)  # 시작 알림 설정
        self.start_alarm.setGeometry(QtCore.QRect(int(rect_width * 2 / 3) - 50, int(rect_height / 10), 100, 50))
        if self.alarm_set_start:
            self.start_alarm.toggle()
        self.start_alarm.stateChanged.connect(self.set_start)

        self.advice = QtWidgets.QCheckBox("학습 조언", self)  # 학습 조언 설정
        self.advice.setGeometry(QtCore.QRect(int(rect_width / 3) - 60, int(rect_height / 5), 100, 50))
        if self.study_advice:
            self.advice.toggle()
        self.advice.stateChanged.connect(self.set_advice)

        self.advice_label = QtWidgets.QLabel("학습 시간을 잴 때 다양한 조언을 해줍니다.", self)
        self.advice_label.setFont(QtGui.QFont("돋움", 8))
        self.advice_label.setStyleSheet("color: #AAAAAA")
        self.advice_label.setGeometry(QtCore.QRect(int(rect_width / 3) - 60, int(rect_height / 5) + 30, 300, 30))

        self.reset_bt = QtWidgets.QPushButton("누적 기록 시간 초기화\n되돌릴 수 없습니다", self)  # 초기화 버튼
        self.reset_bt.setFont(QtGui.QFont("돋움", 12))
        self.reset_bt.setStyleSheet("color: #FFFFFF;"
                                    "background-color: #FF0303;"
                                    "border-radius: 10px;"
                                    )
        self.reset_bt.setGeometry(QtCore.QRect(int(rect_width / 2 - 100), int(rect_height * 4 / 10), 200, 50))
        self.reset_bt.clicked.connect(self.reset_time)
        '''
        # ==================================================기록 페이지==============================================
        '''

    def reset_time(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("경고")
        msg.setText("정말 초기화 하시겠습니까?")
        msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        result = msg.exec_()
        if result == QMessageBox.Ok:
            conn = sqlite3.connect(DBfile)
            db_curs = conn.cursor()
            db_curs.execute("UPDATE total SET total_time=0;")
            conn.commit()
            conn.close()

    def set_before(self):  # 시작 10분 전 알림 설정하면 연결, DB에 설정 정보 업데이트를 반영
        self.alarm_set_10 = self.before_alarm.isChecked()
        conn = sqlite3.connect(DBfile)
        db_curs = conn.cursor()

        db_curs.execute("UPDATE setting SET before_alarm=" + str(int(self.alarm_set_10)) + ";")
        conn.commit()
        conn.close()

    def set_start(self):  # 시작 알림 설정하면 연결, DB에 설정 정보 업데이트를 반영
        self.alarm_set_start = self.start_alarm.isChecked()
        conn = sqlite3.connect(DBfile)
        db_curs = conn.cursor()

        db_curs.execute("UPDATE setting SET start_alarm=" + str(int(self.alarm_set_start)) + ";")
        conn.commit()
        conn.close()

    def set_advice(self):  # 조언 설정하면 연결, DB에 설정 정보 업데이트를 반영
        self.study_advice = self.advice.isChecked()
        conn = sqlite3.connect(DBfile)
        db_curs = conn.cursor()

        db_curs.execute("UPDATE setting SET advice=" + str(int(self.study_advice)) + ";")
        conn.commit()
        conn.close()

    def get_setting(self):  # 설정값을 받아옴
        conn = sqlite3.connect(DBfile)
        db_curs = conn.cursor()

        db_curs.execute("SELECT * FROM setting;")  # 전체 내용 검색
        conn.commit()
        setting_value = db_curs.fetchall()

        if setting_value:
            self.alarm_set_start, self.alarm_set_10, self.study_advice = setting_value[0]
        else:  # 알람 사용 설정값이 없는 경우
            self.alarm_set_10 = False
            self.alarm_set_start = True
            self.study_advice = False
            db_curs.execute("insert into setting (before_alarm, start_alarm, advice) values(0, 1, 0);")
            conn.commit()

        conn.close()
        return setting_value[0]

    # =================================================기록 페이지=================================================


class cafe(QWidget):
    def __init__(self):
        super().__init__()

        self.open_button = QtWidgets.QPushButton(self)  # 시작 버튼
        self.open_button.setGeometry(int(rect_width/2 - 60), int(rect_height/2 - 15), 120, 30)
        self.open_button.setText("네이버 카페 연결")
        self.open_button.clicked.connect(self.open)

    def open(self):
        webbrowser.open(cafe_url)


DEFAULT_STYLE = """
QProgressBar {
    border: 2px solid grey;
    border-radius: 5px;
    text-align: center
}

QProgressBar::chunk {
    background-color: lightblue;
    width: 20px;
}
""" # qprogressBar stylesheet


class recode(QWidget):
    def __init__(self):
        super().__init__()
        self.sc = QtWidgets.QWidget()  # 기록
        self.sc.setGeometry(0, 0, rect_width - 20, 650)

        self.scrollArea = QtWidgets.QScrollArea(self)  # 기록
        self.scrollArea.setGeometry(-1, -1, rect_width + 2, rect_height + 2)
        self.scrollArea.setWidget(self.sc)

        self.weekly_time = dict()  # 이번 주 누적 공부 시간 형식 [ 0:00000, 1:0000, ... ] 0=월 6=일
        self.weekly = dict()
        self.weekly_goal = dict()
        self.total_time = get_total()  # 사용 누적 공부 시간
        self.now = time.localtime(time.time())  # 현재 날짜 정보 받아오기
        self.today = int(time.strftime('%y%m%d', self.now))  # 오늘 날짜를 yymmdd 꼴로 정수 저장
        _, self.today_study_time = get_time(self.today)  # 오늘 누적 공부 시간 = DB에서 받아옴
        self.advice = get_setting_advice()
        self.uptime = 0
        self.day_goal = get_day_target(time.strftime('%y%m%d', self.now))
        self.step = sum_percent(self.today_study_time, self.day_goal)

        self.timer_start = QtWidgets.QPushButton(self.sc)  # 시작 버튼
        self.timer_start.setGeometry(QtCore.QRect(int(rect_width / 2) - 120, 230, 75, 23))
        self.timer_start.setObjectName("timer_start")
        self.timer_start.setText("시작")
        self.timer_start.clicked.connect(self.start_timer)

        self.timer_stop = QtWidgets.QPushButton(self.sc)  # 정지 버튼
        self.timer_stop.setGeometry(QtCore.QRect(int(rect_width / 2) + 20, 230, 75, 23))
        self.timer_stop.setObjectName("timer_stop")
        self.timer_stop.setText("중지")
        self.timer_stop.clicked.connect(self.stop)

        rectW = int(rect_width / 2)
        self.time_lcd = QtWidgets.QLCDNumber(self.sc)  # 오늘 공부 시간 기록 LCD
        self.time_lcd.display(set_time(show_time(self.today_study_time)))
        self.time_lcd.setDigitCount(8)
        self.time_lcd.setGeometry(rectW - 215, 120, 400, 100)
        self.time_lcd.setObjectName("time_label")

        self.sum_study_label = QtWidgets.QLabel(self.sc)  # 오늘 공부 시간 라벨
        self.sum_study_label.move(rectW - 60, 100)
        self.sum_study_label.setText("오늘 누적 공부 시간")
        self.sum_study_label.setObjectName("sum_study_label")

        self.time_set = QTimer(self)  # 각종 시간 위젯 갱신용 타이머
        self.time_set.setInterval(10000)  # 10초에 한 번 갱신
        self.time_set.timeout.connect(self.set_time_label)
        self.time_set.start()

        self.now_label = QtWidgets.QLabel(self.sc)  # 현재 시각 표시 라벨
        self.now_label.move(int(rect_width * 2 / 3), 30)
        self.now_label.setFont(QtGui.QFont("바탕", 13))
        self.now_label.setText("현재 시각\n" + str(time.strftime("%I:%M %p", self.now)))

        self.today_label_MD = QtWidgets.QLabel(self.sc)  # 오늘 월, 요일 표시 라벨
        self.today_label_MD.move(int(rect_width / 3) - 100, 30)
        self.today_label_MD.setFont(QtGui.QFont("바탕", 12))
        self.today_label_MD.setText(str(self.today)[2:4] + "월, " + today_is_day())
        self.today_label_MD.setObjectName("today_label_MD")

        self.today_label_day = QtWidgets.QLabel(self.sc)  # 오늘 일 표시 라벨
        self.today_label_day.move(int(rect_width / 3) - 75, 50)
        self.today_label_day.setFont(QtGui.QFont("바탕", 19))
        self.today_label_day.setText(str(self.today)[4:] + "일")
        self.today_label_day.setObjectName("today_label_day")

        self.day_complete = QtWidgets.QLabel("일일 달성률", self.sc)  # 일일 달성률 제목
        self.day_complete.setFont(QtGui.QFont("돋움", 12))
        self.day_complete.move(55, 280)

        self.day_progress = QtWidgets.QProgressBar(self.sc)  # 일일 달성률 바
        self.day_progress.setGeometry(50, 310, window_width - 140, 25)
        self.day_progress.setValue(self.step)
        self.day_progress.setStyleSheet(DEFAULT_STYLE)

        self.set_week_time()
        # print(self.weekly_time, self.weekly, self.weekly_goal)
        self.weekly_complete = QtWidgets.QLabel("주간 달성률", self.sc)  # 주간 달성률 제목
        self.weekly_complete.setFont(QtGui.QFont("돋움", 12))
        self.weekly_complete.move(55, 370)

        self.mon0 = QtWidgets.QLabel("월", self.sc)  # 주간 달성률 행 제목 라벨
        self.mon0.setFont(QtGui.QFont("돋움", 11))
        self.mon0.move(50, 400)
        self.mon1 = QtWidgets.QLabel(self.sc)  # 주간 달성률 퍼센트
        self.mon1.setText(str(sum_percent(self.weekly_time[0], self.weekly_goal[0])) + "%")
        self.mon1.setFont(QtGui.QFont("돋움", 11))
        self.mon1.move(50, 425)
        self.mon2 = QtWidgets.QLabel(self.sc)  # 주간 달성률 시간
        self.mon2.setText(view_hms(*show_time(self.weekly_time[0])))
        self.mon2.setFont(QtGui.QFont("돋움", 11))
        self.mon2.move(50, 450)

        self.tue0 = QtWidgets.QLabel("화", self.sc)  # 주간 달성률 행 제목 라벨
        self.tue0.setFont(QtGui.QFont("돋움", 11))
        self.tue0.move(130, 400)
        self.tue1 = QtWidgets.QLabel(self.sc)  # 주간 달성률 퍼센트
        self.tue1.setText(str(sum_percent(self.weekly_time[1], self.weekly_goal[1])) + "%")
        self.tue1.setFont(QtGui.QFont("돋움", 11))
        self.tue1.move(130, 425)
        self.tue2 = QtWidgets.QLabel(self.sc)  # 주간 달성률 시간
        self.tue2.setText(view_hms(*show_time(self.weekly_time[1])))
        self.tue2.setFont(QtGui.QFont("돋움", 11))
        self.tue2.move(130, 450)

        self.wen0 = QtWidgets.QLabel("수", self.sc)  # 주간 달성률 행 제목 라벨
        self.wen0.setFont(QtGui.QFont("돋움", 11))
        self.wen0.move(215, 400)
        self.wen1 = QtWidgets.QLabel(self.sc)  # 주간 달성률 퍼센트
        self.wen1.setText(str(sum_percent(self.weekly_time[2], self.weekly_goal[2])) + "%")
        self.wen1.setFont(QtGui.QFont("돋움", 11))
        self.wen1.move(215, 425)
        self.wen2 = QtWidgets.QLabel(self.sc)  # 주간 달성률 시간
        self.wen2.setText(view_hms(*show_time(self.weekly_time[2])))
        self.wen2.setFont(QtGui.QFont("돋움", 11))
        self.wen2.move(215, 450)

        self.thu0 = QtWidgets.QLabel("목", self.sc)  # 주간 달성률 행 제목 라벨
        self.thu0.setFont(QtGui.QFont("돋움", 11))
        self.thu0.move(305, 400)
        self.thu1 = QtWidgets.QLabel(self.sc)  # 주간 달성률 퍼센트
        self.thu1.setText(str(sum_percent(self.weekly_time[3], self.weekly_goal[3])) + "%")
        self.thu1.setFont(QtGui.QFont("돋움", 11))
        self.thu1.move(305, 425)
        self.thu2 = QtWidgets.QLabel(self.sc)  # 주간 달성률 시간
        self.thu2.setText(view_hms(*show_time(self.weekly_time[3])))
        self.thu2.setFont(QtGui.QFont("돋움", 11))
        self.thu2.move(305, 450)

        self.fri0 = QtWidgets.QLabel("금", self.sc)  # 주간 달성률 행 제목 라벨
        self.fri0.setFont(QtGui.QFont("돋움", 11))
        self.fri0.move(390, 400)
        self.fri1 = QtWidgets.QLabel(self.sc)  # 주간 달성률 퍼센트
        self.fri1.setText(str(sum_percent(self.weekly_time[4], self.weekly_goal[4])) + "%")
        self.fri1.setFont(QtGui.QFont("돋움", 11))
        self.fri1.move(390, 425)
        self.fri2 = QtWidgets.QLabel(self.sc)  # 주간 달성률 시간
        self.fri2.setText(view_hms(*show_time(self.weekly_time[4])))
        self.fri2.setFont(QtGui.QFont("돋움", 11))
        self.fri2.move(390, 450)

        self.sat0 = QtWidgets.QLabel("토", self.sc)  # 주간 달성률 행 제목 라벨
        self.sat0.setFont(QtGui.QFont("돋움", 11))
        self.sat0.move(470, 400)
        self.sat1 = QtWidgets.QLabel(self.sc)  # 주간 달성률 퍼센트
        self.sat1.setText(str(sum_percent(self.weekly_time[5], self.weekly_goal[5])) + "%")
        self.sat1.setFont(QtGui.QFont("돋움", 11))
        self.sat1.move(470, 425)
        self.sat2 = QtWidgets.QLabel(self.sc)  # 주간 달성률 시간
        self.sat2.setText(view_hms(*show_time(self.weekly_time[5])))
        self.sat2.setFont(QtGui.QFont("돋움", 11))
        self.sat2.move(470, 450)

        self.sun0 = QtWidgets.QLabel("일", self.sc)  # 주간 달성률 행 제목 라벨
        self.sun0.setFont(QtGui.QFont("돋움", 11))
        self.sun0.move(550, 400)
        self.sun1 = QtWidgets.QLabel(self.sc)  # 주간 달성률 퍼센트
        self.sun1.setText(str(sum_percent(self.weekly_time[6], self.weekly_goal[6])) + "%")
        self.sun1.setFont(QtGui.QFont("돋움", 11))
        self.sun1.move(550, 425)
        self.sun2 = QtWidgets.QLabel(self.sc)  # 주간 달성률 시간
        self.sun2.setText(view_hms(*show_time(self.weekly_time[6])))
        self.sun2.setFont(QtGui.QFont("돋움", 11))
        self.sun2.move(550, 450)

        self.total_s_label = QtWidgets.QLabel(self.sc)  # 누적 기록 시간
        self.total_s_label.setText("누적 기록 시간")
        self.total_s_label.setFont(QtGui.QFont("돋움", 14))
        self.total_s_label.move(rectW - 80, 550)

        self.total_label = QtWidgets.QLabel(self.sc)  # 누적 기록 시간 표시
        h, m, s = show_time(self.total_time)
        self.total_label.setText(str(h) + "시간 " + str(m) + "분 " + str(s) + "초")
        self.total_label.setGeometry(rectW - 150, 570, 400, 50)
        self.total_label.setFont(QtGui.QFont("돋움", 30))

        self.timer = QTimer(self.sc)  # 타이머 생성
        self.timer.setInterval(1000)  # 타이머의 인터벌 설정 (ms)
        self.timer.timeout.connect(self.timeout)  # 인터벌 시간이 끝나면 수행할 핸들러

        self.timer_stop.setEnabled(False)  # 정지 중엔 정지 버튼 비활성화

    # 주간 누적 시간을 저장하기 위한 메소드
    def set_week_time(self):
        for i in range(0, self.now.tm_wday + 1):  # 현재 요일부터 월요일(0)까지 누적 시간을 날짜(yymmdd)를 key로 weekly_time에 저장
            self.weekly[i], self.weekly_time[i] = get_time(self.today - (self.now.tm_wday - i))
            self.weekly_goal[i] = get_day_target(self.weekly[i])

        if self.now.tm_wday != 6:
            for i in range(self.now.tm_wday + 1, 7):
                self.weekly[i] = 0
                self.weekly_time[i] = 0
                self.weekly_goal[i] = 0

    # 화면에 띄운 라벨을 주기적으로 업데이트하는 메소드 (일일 달성률, 오늘 시간 정보)
    def set_time_label(self):
        sender = self.sender()
        self.now = time.localtime(time.time())
        self.today = int(time.strftime('%y%m%d', self.now))
        self.today_label_MD.setText(str(self.today)[2:4] + "월, " + today_is_day())
        self.today_label_day.setText(str(self.today)[4:] + "일")
        # 오늘 시간 정보 갱신

        self.day_goal = 0  # get_day_target(time.strftime('%y%m%d', self.now))
        self.step = sum_percent(self.today_study_time, self.day_goal)
        self.day_progress.setValue(self.step)
        # 일일 달성률 갱신

        if id(sender) == id(self.time_set):
            self.today_label_day.setText(str(self.today)[4:] + "일")
            self.today_label_MD.setText(str(self.today)[2:4] + "월, " + today_is_day())
            self.now_label.setText("현재 시각\n" + str(time.strftime("%I:%M %p", self.now)))
            self.today_label_day.repaint()
            self.today_label_MD.repaint()
            self.now_label.repaint()

    # 타이머 시작 핸들러
    def start_timer(self):
        self.timer.start()  # 타이머 시작
        self.timer_stop.setEnabled(True)  # 시작 중엔 정지 버튼 활성화
        self.timer_start.setEnabled(False)  # 시작 중엔 시작 버튼 비활성화
        self.uptime = 0

        if self.advice:
            msg = QtWidgets.QMessageBox()  # 조언 팝업
            msg.setWindowTitle("조언")
            msg.setText(advice_list[random.randrange(0, len(advice_list))])
            msg.setStandardButtons(QMessageBox.Cancel)
            msg.exec_()

    # 타이머 정지 핸들러 + 누적 기록 시간
    def stop(self):
        self.timer.stop()  # 타이머 정지
        self.timer_stop.setEnabled(False)  # 정지 중엔 정지 버튼 비활성화
        self.timer_start.setEnabled(True)  # 정지 중엔 시작 버튼 활성화

        conn = sqlite3.connect(DBfile)  # 정지 후 시간 정보 DB에 업데이트
        db_curs = conn.cursor()

        db_curs.execute(  # 오늘 날짜의 값을 받아와보고
            "SELECT * FROM time WHERE save_day=" + str(time.strftime('%y%m%d', time.localtime(time.time())))
        )
        conn.commit()
        study_time = db_curs.fetchall()

        if not study_time:  # 값이 없으면 = insert가 필요하면
            db_curs.execute("insert into time (save_day, save_time) values("
                            + str(time.strftime('%y%m%d', time.localtime(time.time()))) + ", "
                            + str(self.today_study_time) + ");")
        else:  # 값이 있으면 = update를 해야하면
            db_curs.execute("update time set save_time=" + str(self.today_study_time)
                            + " where save_day='"
                            + str(time.strftime('%y%m%d', time.localtime(time.time()))) + "';")

        conn.commit()

        totalT = get_total()

        if not totalT:  # 값이 없으면 = insert가 필요하면
            db_curs.execute("insert into total (total_time) values(" + str(self.today_study_time) + ");")
        else:  # 값이 있으면 = update를 해야하면
            total_value = self.uptime + totalT
            # print(total_value)
            db_curs.execute("update total set total_time=" + str(total_value) + ";")
        conn.commit()
        conn.close()

        self.total_time = get_total()
        h, m, s = show_time(self.total_time)  # 누적 기록 시간 갱신
        self.total_label.setText(str(h) + "시간 " + str(m) + "분 " + str(s) + "초")
        self.total_label.repaint()

        self.week_update()

    # 타이머 핸들러
    def timeout(self):
        sender = self.sender()
        self.today_study_time += 1
        self.uptime += 1
        currentTime = set_time(show_time(self.today_study_time))

        if id(sender) == id(self.timer):
            self.time_lcd.display(currentTime)

    # 주간 달성률 중, 오늘 달성률 업데이트
    def week_update(self):
        self.now = time.localtime(time.time())
        day = time.strftime("%a", self.now)
        print(day)
        self.set_week_time()

        if day == "Mon":
            self.mon1.setText(str(sum_percent(self.weekly_time[0], self.weekly_goal[0])) + "%")  # 퍼센트 갱신
            self.mon2.setText(view_hms(*show_time(self.weekly_time[0])))  # 시간 갱신
            self.mon1.repaint()
            self.mon2.repaint()

        elif day == "Tue":
            self.tue1.setText(str(sum_percent(self.weekly_time[1], self.weekly_goal[1])) + "%")
            self.tue2.setText(view_hms(*show_time(self.weekly_time[1])))
            self.tue1.repaint()
            self.tue2.repaint()

        elif day == "Wen":
            self.wen1.setText(str(sum_percent(self.weekly_time[2], self.weekly_goal[2])) + "%")
            self.wen2.setText(view_hms(*show_time(self.weekly_time[2])))
            self.wen1.repaint()
            self.wen2.repaint()

        elif day == "Thu":
            self.thu1.setText(str(sum_percent(self.weekly_time[3], self.weekly_goal[3])) + "%")
            self.thu2.setText(view_hms(*show_time(self.weekly_time[3])))
            self.thu1.repaint()
            self.thu2.repaint()

        elif day == "Fri":
            self.fri1.setText(str(sum_percent(self.weekly_time[4], self.weekly_goal[4])) + "%")
            self.fri2.setText(view_hms(*show_time(self.weekly_time[4])))
            self.fri1.repaint()
            self.fri2.repaint()

        elif day == "Sat":
            self.sat1.setText(str(sum_percent(self.weekly_time[5], self.weekly_goal[5])) + "%")
            self.sat2.setText(view_hms(*show_time(self.weekly_time[5])))
            self.sat1.repaint()
            self.sat2.repaint()

        elif day == "Sun":
            self.sun1.setText(str(sum_percent(self.weekly_time[6], self.weekly_goal[6])) + "%")
            self.sun2.setText(view_hms(*show_time(self.weekly_time[6])))
            self.sun1.repaint()
            self.sun2.repaint()

    # ============================================================================================================
    # =================================================홈 페이지=================================================


class home(QMainWindow, home_ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.date = QDate.currentDate()
        self.time = QTime.currentTime()

        self.now = time.localtime(time.time())  # 현재 날짜 정보 받아오기
        self.today = int(time.strftime('%y%m%d', self.now))  # 오늘 날짜를 yymmdd 꼴로 정수 저장
        _, self.today_study_time = get_time(self.today)  # 오늘 누적 공부 시간 = DB에서 받아옴

        self.time_set = QTimer(self)  # 각종 시간 위젯 갱신용 타이머
        self.time_set.setInterval(10000)  # 10초에 한 번 갱신
        self.time_set.timeout.connect(self.bar_update)
        self.time_set.start()

        self.day_goal = get_day_target(time.strftime('%y%m%d', self.now))
        self.step = sum_percent(self.today_study_time, self.day_goal)
        self.today_study_gauge.setValue(self.step)
        self.today_study_gauge.setStyleSheet(DEFAULT_STYLE)

        self.timer = QTimer(self)  # 타이머 생성
        self.timer.setInterval(60000)  # 타이머의 인터벌 설정 (ms)
        self.timer.timeout.connect(self.now_time)  # 인터벌 시간이 끝나면 수행할 핸들러

        self.initUI()

    def initUI(self):
        daynum = self.date.dayOfWeek()  # 요일 따로 받아오기
        if daynum == 1:
            day = '월'
        elif daynum == 2:
            day = '화'
        elif daynum == 3:
            day = '수'
        elif daynum == 4:
            day = '목'
        elif daynum == 5:
            day = '금'
        elif daynum == 6:
            day = '토'
        elif daynum == 7:
            day = '일'

        self.viewdate.setText('''
{}월{}일
{}요일'''.format(self.date.month(), self.date.day(), day))  # 오늘 날짜 표시
        self.now_time()  # 현재 시간 표시

        sel_year = self.date.year()
        year = str(sel_year - 2000)
        sel_date = self.date.day()
        sel_month = self.date.month()
        if sel_month < 10:
            sel_month = "0" + str(sel_month)
        else:
            sel_month = str(sel_month)

        if sel_date < 10:
            sel_date = "0" + str(sel_date)
        else:
            sel_date = str(sel_date)
        today = year + sel_month + sel_date

        #todo_list = ["과제하기", "공부하기"]  # DB 계획목록 받아올 것 오늘날짜
        todo_list = get_todolist(today)   # DB 메소드
        for i in range(len(todo_list)):  # 오늘의 일정 추가
            self.todo_list.addItem(todo_list[i])

        schedule = get_schedule(today)  # DB 시간표 받아올 것 오늘날짜

        first = QTableWidgetItem(schedule[0])  # 시간표에 들어갈 수업
        second = QTableWidgetItem(schedule[1])
        third = QTableWidgetItem(schedule[2])
        fourth = QTableWidgetItem(schedule[3])
        fifth = QTableWidgetItem(schedule[4])
        sixth = QTableWidgetItem(schedule[5])
        seventh = QTableWidgetItem(schedule[6])
        eighth = QTableWidgetItem(schedule[7])
        classes = [first, second, third, fourth, fifth, sixth, seventh, eighth]

        for i in range(8):
            self.timetable.setItem(1, i, classes[i])  # 시간표 테이블에 입력

    def now_time(self):  # 현재시간 표시
        t = time.localtime()
        self.viewtime.setText('''{}:{}:{}'''.format(t.tm_hour, t.tm_min, t.tm_sec))
        self.viewtime.repaint()

    def bar_update(self):  # 진행도 업데이트
        self.day_goal = 0  # get_day_target(time.strftime('%y%m%d', self.now))
        self.step = sum_percent(self.today_study_time, self.day_goal)
        self.today_study_gauge.setValue(self.step)

    # ============================================================================================================
    # =================================================달력 페이지=================================================


class Calendar(QMainWindow, calendar_ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.date = QDate.currentDate()
        self.initUI()

    def initUI(self):
        planned_day = ['201204']  # DB 모든 일정들의 날짜값 받아올 것
        # planned_day = get_planned_day() #DB메소드
        thousand_year = ['20']
        complt_planned_day = [thousand_year[0] + i for i in planned_day]
        fm = QTextCharFormat()
        fm.setBackground(Qt.yellow)  # 배경 노란색 색상 변경 가능

        for dday in complt_planned_day:
            dday2 = QDate.fromString(dday, "yyyyMMdd")
            self.cal.setDateTextFormat(dday2, fm)

        self.cal.clicked[QDate].connect(self.clked_date)  # 달력에서 날짜 선택시 일정 표시

    def clked_date(self, date):
        sel_year = date.year()
        year = str(sel_year - 2000)
        sel_date = date.day()
        sel_month = date.month()
        if sel_month < 10:
            sel_month = "0" + str(sel_month)
        else:
            sel_month = str(sel_month)

        if sel_date < 10:
            sel_date = "0" + str(sel_date)
        else:
            sel_date = str(sel_date)
        sel_day = year + sel_month + sel_date

        # todolist = ["공부하기", "과제하기"] #DB 계획 받아올 것 0월0일의 계획
        todolist = get_todolist(sel_day)  # DB 메소드
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("일정")
        msg.setText("{}년 {}월 {}일의 일정\n{}".format(sel_year, sel_month, sel_date, "\n".join(todolist)))  # DB에서 일정 받아오기 필요
        msg.exec_()


form_class = uic.loadUiType("timetableUI.ui")[0]


def change_date(start, end, *re):   # 날짜 리스트를 받기 위한 함수
    # now = time.localtime(time.time())
    try:
        if int(end) < int(start):  # 종료일이 오늘보다 앞의 날인 경우
            return "day error"  # day error 발생
    except ValueError:  # end에 숫자로 변환할 수 없는 문자가 들어온 경우
        return "day error"

    if len(re) <= 1:  # 반복 종류만 주고 상세 설정을 주지 않은 경우
        return "type error"  # type error 발생

    # today = int(time.strftime("%y%m%d", now))  # 오늘 날짜 yymmdd 형식
    start_date = time_to_date(start)  # 오늘 날짜를 datetime 객체로
    end_date = time_to_date(end)  # 끝 날짜를 datetime 객체로
    one_day = timedelta(days=1)  # 하루 더하기 위한 객체
    day = list()  # 반환할 날짜 리스트

    try:
        if re[0] == 'day':  # 요일 반복이면
            if type(re[1]) == list:  # 반복 요일 받아옴
                day_list = re[1]
            elif type(re[1]) == int:
                day_list = list(re[1:])

            date = start_date  # 첫 확인 날짜를 오늘로 설정
            while end_date >= date:  # 종료일보다 확인 날짜가 적으면 반복
                for i in day_list:
                    if date.weekday() == i:
                        day.append(date_to_time(date))
                date += one_day

        elif re[0] == 'nday':  # 기간 반복이면
            sum_day = timedelta(days=int(re[1]))  # 반복 텀
            date = start_date

            while end_date >= date:
                day.append(date_to_time(date))
                date += sum_day

        else:  # 반복 종류가 정상적인 값이 아닐 경우
            return "type error"  # type error 발생
    except TypeError:
        return "input error"

    return day


# "yymmdd"꼴의 문자열을 datetime 객체로 변환해서 반환
def time_to_date(day):
    date = day
    if not type(day) == str:
        date = str(day)

    y = int(date[:2])
    m = int(date[2:4])
    d = int(date[4:])

    y += 2000

    result = datetime(y, m, d)
    return result


# datetime 객체를 "yymmdd"꼴의 문자열로 변환해 반환
def date_to_time(day):
    year = day.year - 2000  # 년
    month = day.month  # 월
    date = day.day  # 일

    y = str(year)

    if month < 10:
        m = "0" + str(month)
    else:
        m = str(month)

    if date < 10:
        d = "0" + str(date)
    else:
        d = str(date)

    return y + m + d


# db 생성
conn = sqlite3.connect("conaTimetable.db")
cur = conn.cursor()
cur.execute("create table IF NOT EXISTS timetable (class_plan INTEGER, name TEXT, date TEXT, start_tm INTEGER, end_tm INTEGER, memo TEXT, block TEXT);")
conn.commit()
conn.close()


class change_popup(QDialog):
    def __init__(self, parent, name, date, sts, eds, memo, rgbs, cp):
        super(change_popup, self).__init__(parent)
        form_class6 = './changepopup.ui'
        uic.loadUi(form_class6, self)
        self.show()
        self.name = name
        self.date = date
        self.sts = sts
        self.eds = eds
        self.memo = memo
        self.rgbs = rgbs
        self.cp = cp
        # 불러오기
        self.setWindowTitle("{} 계획 변경".format(name))
        self.setFixedSize(400, 300)
        self.setWindowIcon(QIcon('conalogo.png'))
        self.nameedit.setText("{}".format(name))
        day = time_to_date(date)
        q_date = QDate(day)
        self.dateEdit.setDate(q_date)
        self.memoedit.setText("{}".format(memo))
        self.st_tm.setValue(int(sts))
        self.ed_tm.setValue(int(eds))
        # ui 설정
        self.dateEdit.setCalendarPopup(True)
        self.st_tm.setRange(6, 23)  # spinbox 선택범위
        self.ed_tm.setRange(7, 24)
        self.plancheck.stateChanged.connect(self.changecheckplan)  # 계획체크박스 상태가 변하면 수업 토글
        self.classcheck.stateChanged.connect(self.changecheckclass)  # 수업체크박스 상태가 변하면 계획 토글

        if cp == 0:
            self.plancheck.setChecked(True)
        else:
            self.classcheck.setChecked(True)

        if rgbs == "192,000,000":
            self.rgb1.setChecked(True)
        elif rgbs == "244,177,131":
            self.rgb2.setChecked(True)
        elif rgbs == "255,230,153":
            self.rgb3.setChecked(True)
        elif rgbs == "169,209,142":
            self.rgb4.setChecked(True)
        elif rgbs == "157,195,230":
            self.rgb5.setChecked(True)
        elif rgbs == "000,032,096":
            self.rgb6.setChecked(True)
        else:
            self.rgb7.setChecked(True)

        # 수정
        self.save_bt.clicked.connect(self.changesave)
        self.cancel_bt.clicked.connect(self.changecancel)
        self.pdel_bt.clicked.connect(self.pdelplan)
        self.rgb1.clicked.connect(self.rgbradioClicked)  # rgb1 라디오 버튼 클릭하면
        self.rgb2.clicked.connect(self.rgbradioClicked)  # rgb2 라디오 버튼 클릭하면
        self.rgb3.clicked.connect(self.rgbradioClicked)  # rgb3 라디오 버튼 클릭하면
        self.rgb4.clicked.connect(self.rgbradioClicked)  # rgb4 라디오 버튼 클릭하면
        self.rgb5.clicked.connect(self.rgbradioClicked)  # rgb5 라디오 버튼 클릭하면
        self.rgb6.clicked.connect(self.rgbradioClicked)  # rgb6 라디오 버튼 클릭하면
        self.rgb7.clicked.connect(self.rgbradioClicked)  # rgb7 라디오 버튼 클릭하면

    def changecheckplan(self):  # 계획이 눌려지고 수업 토글
        if self.plancheck.isChecked() == True:
            self.classcheck.setChecked(False)
        else:
            self.classcheck.setChecked(True)

    def changecheckclass(self):  # 수업이 눌려지고 계획 토글
        if self.classcheck.isChecked() == True:
            self.plancheck.setChecked(False)
        else:
            self.plancheck.setChecked(True)

    def rgbradioClicked(self):  # 라디오 버튼이 클릭되면 rgb값 리턴
        if self.rgb1.isChecked():
            rgbr = "192,000,000"
        elif self.rgb2.isChecked():
            rgbr = "244,177,131"
        elif self.rgb3.isChecked():
            rgbr = "255,230,153"
        elif self.rgb4.isChecked():
            rgbr = "169,209,142"
        elif self.rgb5.isChecked():
            rgbr = "157,195,230"
        elif self.rgb6.isChecked():
            rgbr = "000,032,096"
        else:
            rgbr = "112,048,160"
        return rgbr

    def changesave(self):
        namee = self.nameedit.text()
        memoe = self.memoedit.text()
        datee = self.dateEdit.date()
        dateee = str(datee.toPyDate())
        dateslice = dateee[2:]
        datesplit = dateslice.split('-')
        datejoin = "".join(datesplit)
        sts = self.st_tm.value()  # int
        eds = self.ed_tm.value()  # int
        class_planck = int(self.classcheck.isChecked())  # 수업 <class 'bool'> -> int로 true = 1 false = 0, 1이면 수업 0이면 계획
        rgbr = self.rgbradioClicked()  # 라디오 버튼으로 블록색 받아오기
        if namee != "" and rgbr != "" and sts < eds:
            try:
                conn = sqlite3.connect("conaTimetable.db")
                db_cur = conn.cursor()  # 커서 생성
                db_cur.execute(
                    "UPDATE timetable SET class_plan = {}, date = '{}', name = '{}', start_tm = {}, end_tm = {}, memo = '{}', block = '{}' WHERE class_plan=? AND name=? AND date=? AND end_tm=? AND memo=? AND block=?".format(class_planck, datejoin, namee, sts, eds, memoe, rgbr), (self.cp, self.name, self.date, self.eds, self.memo, self.rgbs)
                )  # 기존 저장 팝업으로 저장한 컬럼에 변경한 데이터값 db 추가
                conn.commit()
                conn.close()
                msg = QMessageBox.information(
                    self, "시간표 저장 완료", "계획이름: {}, 메모: {}, 시작시각: {}시, 종료시각: {}시".format(namee, memoe, sts, eds),
                    QMessageBox.Ok
                )
                if msg == QMessageBox.Ok:
                    result = self.close()
                else:
                    return

                if result:
                    self.close()
            except:
                QMessageBox.warning(
                    self, "시간표 저장 실패", "입력 오류 \n올바른 형식의 입력이 아닙니다.",
                    QMessageBox.Ok
                )
                return
        else:
            QMessageBox.warning(
                self, "시간표 저장 실패", "입력 오류 \n계획 이름과 블록색상을 지정을 반드시 해주세요.\n계획 종료 시각이 시작 시각보다 빠를 수 없습니다.",
                QMessageBox.Ok
            )
            return

    def changecancel(self):  # 변경 팝업 취소 누렀을 때
        msg = QMessageBox.warning(

            self, "시간표 변경 취소", "지금까지 입력하신 정보는 사라집니다. 취소하시겠습니까?",

            QMessageBox.Yes | QMessageBox.No,

            QMessageBox.No

        )
        if msg == QMessageBox.Yes:
            result = self.close()
        else:
            return

        if result:
            self.close()

    def pdelplan(self):  # 변경 팝업 일정 삭제 누렀을 때
        msg = QMessageBox.warning(

            self, "시간표 일정 삭제", "일정을 삭제하시겠습니까?",

            QMessageBox.Yes | QMessageBox.No,

            QMessageBox.No

        )
        if msg == QMessageBox.Yes:
            conn = sqlite3.connect("conaTimetable.db")  # db 연결
            cur = conn.cursor()  # 커서 생성
            cur.execute(
                "DELETE FROM timetable WHERE class_plan=? AND name=? AND date=? AND start_tm=? AND end_tm=? AND memo=? AND block=?",
                (self.cp, self.name, self.date, self.sts, self.eds, self.memo, self.rgbs))
            conn.commit()
            conn.close()
            result = self.close()
        else:
            return

        if result:
            self.close()


class clicked_popup(QDialog):
    def __init__(self, parent, name, date, sts, eds, memo, rgbs, cp):
        super(clicked_popup, self).__init__(parent)
        form_class5 = './clickedpopup.ui'
        uic.loadUi(form_class5, self)
        self.show()
        self.name = name
        self.date = date
        self.sts = sts
        self.eds = eds
        self.memo = memo
        self.rgbs = rgbs
        self.cp = cp
        self.setWindowTitle("{} 계획 정보".format(name))
        self.setFixedSize(400, 260)
        self.setWindowIcon(QIcon('conalogo.png'))
        self.pname.setText("{}".format(name))
        self.pdate.setText("{}".format(date))
        self.time.setText("{}시 ~ {}시".format(sts, eds))
        self.memoedit.setText("{}".format(memo))
        self.change_bt.clicked.connect(self.clickchange)
        self.pdel_bt.clicked.connect(self.pdelplan)

        if cp == 0:
            self.plancheck.setChecked(True)
        else:
            self.classcheck.setChecked(True)

        if rgbs == "192,000,000":
            self.rgb1.setChecked(True)
        elif rgbs == "244,177,131":
            self.rgb2.setChecked(True)
        elif rgbs == "255,230,153":
            self.rgb3.setChecked(True)
        elif rgbs == "169,209,142":
            self.rgb4.setChecked(True)
        elif rgbs == "157,195,230":
            self.rgb5.setChecked(True)
        elif rgbs == "000,032,096":
            self.rgb6.setChecked(True)
        else:
            self.rgb7.setChecked(True)

    def clickchange(self):  # 변경 팝업으로
        change_popup(self, self.name, self.date, self.sts, self.eds, self.memo, self.rgbs, self.cp)
        self.close()

    def pdelplan(self): # 일정 삭제
        msg = QMessageBox.warning(

            self, "시간표 일정 삭제", "일정을 삭제하시겠습니까?",

            QMessageBox.Yes | QMessageBox.No,

            QMessageBox.No

        )
        if msg == QMessageBox.Yes:
            conn = sqlite3.connect("conaTimetable.db")  # db 연결
            cur = conn.cursor()  # 커서 생성
            cur.execute(
                "DELETE FROM timetable WHERE class_plan=? AND name=? AND date=? AND start_tm=? AND end_tm=? AND memo=? AND block=?",
                (self.cp, self.name, self.date, self.sts, self.eds, self.memo, self.rgbs))
            conn.commit()
            conn.close()
            result = self.close()
        else:
            return

        if result:
            self.close()

class cont_popup(QDialog):  # 반복 팝업
    def __init__(self, parent):
        super(cont_popup, self).__init__(parent)
        form_class4 = './contpopup.ui'
        uic.loadUi(form_class4, self)
        self.show()
        # ui 설정
        self.setWindowTitle("반복 설정")
        self.setFixedSize(480, 210)
        self.sdate1.setDate(QDate.currentDate())  # 지정날짜1에 현재 날짜로 표시하기
        self.sdate1.setMinimumDate(QDate.currentDate())  # 최소 날짜 오늘로
        self.sdate2.setDate(QDate.currentDate())  # 지정날짜2에 현재 날짜로 표시하기
        self.sdate2.setMinimumDate(QDate.currentDate())  # 최소 날짜 오늘로
        self.stdate.setDate(QDate.currentDate())  # 시작날짜에 현재 날짜로 표시하기
        self.stdate.setMinimumDate(QDate.currentDate())  # 최소 날짜 오늘로
        self.eddate.setDate(QDate.currentDate())  # 종료날짜에 현재 날짜로 표시하기
        self.eddate.setMinimumDate(QDate.currentDate())  # 최소 날짜 오늘로
        self.ndays.addItems(["반복안함", "1", "2", "3", "4", "5", "6", "7"])  # combobox에 내용 추가
        # ui 설정 끝
        # datetime 지정일 상태 변하면
        self.sdate1.dateChanged.connect(self.changedsdate)
        self.sdate2.dateChanged.connect(self.changedsdate)
        # changedsdate 함수 연결
        # 시작이 종료일 상태 변하면
        self.stdate.dateChanged.connect(self.changeddate)
        self.eddate.dateChanged.connect(self.changeddate)
        # changeddate 함수 연결
        # 요일 반복 상태 변하면
        self.monck.stateChanged.connect(self.changedck)
        self.tueck.stateChanged.connect(self.changedck)
        self.wedck.stateChanged.connect(self.changedck)
        self.thuck.stateChanged.connect(self.changedck)
        self.frick.stateChanged.connect(self.changedck)
        self.satck.stateChanged.connect(self.changedck)
        self.sunck.stateChanged.connect(self.changedck)
        # changedck 함수 연결
        # 며칠 반복 상태 변하면
        self.ndays.currentTextChanged.connect(self.changedcom)
        # changedcom 함수 연결
        self.sdate1join = None  # None으로 초기화
        self.sdate2join = None  # None으로 초기화
        self.stdatejoin = None  # None으로 초기화
        self.eddatejoin = None  # None으로 초기화
        # 저장 누른경우
        self.saved.clicked.connect(self.savecont)
        self.caned.clicked.connect(self.cancelcont)

    def changedsdate(self):  # 지정일 반복 : date를 yymmdd로 변환하여 day 리스트로 반환
        now = datetime.today().strftime("%Y-%m-%d")  # class str
        now2 = time.localtime(time.time())
        today = int(time.strftime("%y%m%d", now2))
        dateselect1 = self.sdate1.date()  # sdate1 변경된값 dateselect1에 할당
        datedateselect1 = str(dateselect1.toPyDate())  # datetime.date를 str로    지정일1
        dateselect2 = self.sdate2.date()
        datedateselect2 = str(dateselect2.toPyDate())  # 지정일2
        day = list()
        if now != datedateselect1:
            sdate1slice = datedateselect1[2:]
            sdate1split = sdate1slice.split("-")
            self.sdate1join = "".join(sdate1split)
        else:
            self.sdate1join = None
        if now != datedateselect2:
            sdate2slice = datedateselect2[2:]
            sdate2split = sdate2slice.split("-")
            self.sdate2join = "".join(sdate2split)
        else:
            self.sdate2join = None

        if self.sdate1join == None and self.sdate2join == None:
            day = None  # 다시 오늘 날짜로 초기화한 경우
        elif self.sdate1join == None and self.sdate2join != None:
            day.extend([today ,self.sdate2join])  # 시작일이 오늘, 종료일이 변경된경우
        elif self.sdate1join != None and self.sdate2join == None:
            day.append(self.sdate1join)  # 시작일이 변경되고 종료일이 변경안된경우
        elif self.sdate1join != None and self.sdate2join != None and self.sdate1join == self.sdate2join:
            day.append(self.sdate1join)  # 오늘이 아닌 다른 날짜 시작일과 종료일이 같은 경우
        else:
            day.extend([self.sdate1join, self.sdate2join])
        return day

    def changeddate(self):  # 날짜 지정 범위 반복 모든 반복을 위해 꼭 필요함
        stardate = self.stdate.date()  # <class 'PyQt5.QtCore.QDate'>
        stardt = stardate.toPyDate()  # <class 'datetime.date'>
        enddate = self.eddate.date()  # <class 'PyQt5.QtCore.QDate'>
        enddt = enddate.toPyDate()  # datetime.date 객체로
        endstr = str(enddt)
        endslice = endstr[2:]
        endsplit = endslice.split("-")
        endjoin = "".join(endsplit)
        ststr = str(stardt)
        stsli = ststr[2:]
        stsp = stsli.split("-")
        stj = "".join(stsp)
        day = list()
        if stardt <= enddt:  # 시작일이 종료일보다 같거나 작으면
            sdt = stardt  # datetime.date 객체
            while sdt <= enddt:  # datetime 객체간 시작일과 종료일 비교
                sds = str(sdt)
                sdsslice = sds[2:]
                sdssplit = sdsslice.split("-")
                sdsjoin = "".join(sdssplit)
                day.append(sdsjoin)
                sdt += timedelta(days=1)
            return day, stj, endjoin

    def changedck(self):  # 요일반복이 선택되면 day 리스트에 요일 추가
        day = list()
        if self.monck.isChecked() == True:
            day.append(0)
        if self.tueck.isChecked() == True:
            day.append(1)
        if self.wedck.isChecked() == True:
            day.append(2)
        if self.thuck.isChecked() == True:
            day.append(3)
        if self.frick.isChecked() == True:
            day.append(4)
        if self.satck.isChecked() == True:
            day.append(5)
        if self.sunck.isChecked() == True:
            day.append(6)
        if not day:
            day = None
        return day

    def changedcom(self):
        # 만약 사용자가 며칠반복을 취소하고 다른 반복을 선택했을때를 위해 spin 에서 comboBox로 변경 반복안함,1~7까지
        nday = self.ndays.currentText()
        if nday == "반복안함":
            nday = None
        elif nday == "1":
            nday = int(self.ndays.currentText())
        elif nday == "2":
            nday = int(self.ndays.currentText())
        elif nday == "3":
            nday = int(self.ndays.currentText())
        elif nday == "4":
            nday = int(self.ndays.currentText())
        elif nday == "5":
            nday = int(self.ndays.currentText())
        elif nday == "6":
            nday = int(self.ndays.currentText())
        else:
            nday = int(self.ndays.currentText())
        return nday

    def savecont(self):  # 저장 누른경우
        ck = self.changedck()  # 요일 반복
        com = self.changedcom()  # 며칠 반복
        date, startday, endday = self.changeddate()  # 기간 반복
        sdate = self.changedsdate()  # 지정일 반복
        if ck != None and com == None and sdate == None and len(date) != 1:  # 요일 반복 db 저장
            try:
                day_ck = change_date(startday, endday, "day", ck)
                conn = sqlite3.connect("conaTimetable.db")  # db 연결
                db_cur = conn.cursor()  # 커서 생성
                for date_ck in day_ck:
                    db_cur.execute(
                        "INSERT INTO timetable (date) VALUES (?)", (date_ck,)
                    )  # date에 db 추가
                conn.commit()
                conn.close()
                msg = QMessageBox.information(
                    self, "반복 저장 완료", "{}일 반복됩니다.".format(day_ck),
                    QMessageBox.Ok
                )
                if msg == QMessageBox.Ok:
                    result = self.close()
                else:
                    return

                if result:
                    self.close()
            except:
                QMessageBox.warning(
                    self, "반복 저장 실패", "입력 오류 \n요일 반복과 시작일, 종료일을 올바른 형식으로 입력해주세요.",
                    QMessageBox.Ok
                )
        elif ck == None and com != None and sdate == None and len(date) != 1:  # 며칠 반복 db 저장
            try:
                day_com = change_date(startday, endday, "nday", com)
                conn = sqlite3.connect("conaTimetable.db")
                db_cur = conn.cursor()  # 커서 생성
                for date_com in day_com:
                    db_cur.execute(
                        "INSERT INTO timetable (date) VALUES (?)", (date_com,)
                    )  # date에 db 추가
                conn.commit()
                conn.close()
                msg = QMessageBox.information(
                    self, "반복 저장 완료", "{}일 반복됩니다.".format(day_com),
                    QMessageBox.Ok
                )
                if msg == QMessageBox.Ok:
                    result = self.close()
                else:
                    return

                if result:
                    self.close()
            except:
                QMessageBox.warning(
                    self, "반복 저장 실패", "입력 오류 \n며칠 반복과 시작일, 종료일을 올바른 형식으로 입력해주세요.",
                    QMessageBox.Ok
                )
        elif ck == None and com == None and sdate != None and len(date) == 1:  # 지정일 반복 db 저장
            try:
                conn = sqlite3.connect("conaTimetable.db")
                db_cur = conn.cursor()  # 커서 생성
                for date_s in sdate:
                    db_cur.execute(
                        "INSERT INTO timetable (date) VALUES (?)", (date_s,)
                    )  # date에 db 추가
                conn.commit()
                conn.close()
                msg = QMessageBox.information(
                    self, "반복 저장 완료", "{}일 반복됩니다.".format(sdate),
                    QMessageBox.Ok
                )
                if msg == QMessageBox.Ok:
                    result = self.close()
                else:
                    return

                if result:
                    self.close()
            except:
                QMessageBox.warning(
                    self, "반복 저장 실패",
                    "입력 오류 \n올바른 형식으로 입력해주세요.\n지정일 반복만 입력해주세요.\n날짜 지정 기간 반복의 시작일과 종료일을 오늘로 입력해주세요.",
                    QMessageBox.Ok
                )
        elif ck == None and com == None and sdate == None and len(date) != 1:  # 지정 범위 반복 db 저장
            try:
                conn = sqlite3.connect("conaTimetable.db")
                db_cur = conn.cursor()  # 커서 생성
                for date_term in date:
                    db_cur.execute(
                        "INSERT INTO timetable (date) VALUES (?)", (date_term,)
                    )  # date에 db 추가
                conn.commit()
                conn.close()
                msg = QMessageBox.information(
                    self, "반복 저장 완료", "{}일 반복됩니다.".format(date),
                    QMessageBox.Ok
                )
                if msg == QMessageBox.Ok:
                    result = self.close()
                else:
                    return

                if result:
                    self.close()
            except:
                QMessageBox.warning(
                    self, "반복 저장 실패", "입력 오류 \n날짜 지정 기간 반복의 시작일과 종료일만 올바른 형식으로 입력해주세요.",
                    QMessageBox.Ok
                )
        else:
            QMessageBox.warning(
                self, "반복 저장 실패",
                "입력 오류\n반복은 한 종류만 가능합니다.\n요일 반복, 며칠 반복은 시작일과 종료일까지 입력해주세요.\n지정일 반복일 경우 시작일과 종료일을 오늘로 입력해주세요.\n",
                QMessageBox.Ok
            )

    def cancelcont(self):
        # 취소누르면 추가 팝업의 반복 체크 박스도 False로 하고싶지만 오류
        msg = QMessageBox.warning(

            self, "반복 취소", "지금까지 입력하신 정보는 사라집니다. 취소하시겠습니까?",

            QMessageBox.Yes | QMessageBox.No,

            QMessageBox.No

        )
        if msg == QMessageBox.Yes:
            self.contck = 0
            result = self.close()
        else:
            return

        if result:
            self.close()

class add_popup(QDialog):  # 추가 팝업
    def __init__(self, parent):
        super(add_popup, self).__init__(parent)
        form_class3 = './addpopup.ui'
        uic.loadUi(form_class3, self)
        self.show()
        #   ui 설정
        self.setWindowTitle("시간표 추가")
        self.setWindowIcon(QIcon('conalogo.png'))
        self.setFixedSize(400, 300)
        self.dateEdit.setDate(QDate.currentDate())  # dateedit에 현재 날짜로 표시하기
        self.dateEdit.setMinimumDate(QDate.currentDate())  # 최소 날짜 오늘로
        self.dateEdit.setCalendarPopup(True)  # 캘린더형으로 날짜 선택
        self.st_tm.setRange(6, 23)  # spinbox 선택범위
        self.ed_tm.setRange(7, 24)
        self.classcheck.setChecked(True)  # 수업을 기본 체크로
        self.contcheck.stateChanged.connect(self.truecontcheck)  # 반복체크박스 상태가 변하면 반복팝업
        self.plancheck.stateChanged.connect(self.changecheckplan)  # 계획체크박스 상태가 변하면 수업 토글
        self.classcheck.stateChanged.connect(self.changecheckclass)  # 수업체크박스 상태가 변하면 계획 토글
        self.rgb1.clicked.connect(self.rgbradioClicked)  # rgb1 라디오 버튼 클릭하면
        self.rgb2.clicked.connect(self.rgbradioClicked)  # rgb2 라디오 버튼 클릭하면
        self.rgb3.clicked.connect(self.rgbradioClicked)  # rgb3 라디오 버튼 클릭하면
        self.rgb4.clicked.connect(self.rgbradioClicked)  # rgb4 라디오 버튼 클릭하면
        self.rgb5.clicked.connect(self.rgbradioClicked)  # rgb5 라디오 버튼 클릭하면
        self.rgb6.clicked.connect(self.rgbradioClicked)  # rgb6 라디오 버튼 클릭하면
        self.rgb7.clicked.connect(self.rgbradioClicked)  # rgb7 라디오 버튼 클릭하면
        #   ui 설정 끝

        self.save_bt.clicked.connect(self.saved_bt)  # 추가팝업에서 저장버튼 누를시
        self.cancel_bt.clicked.connect(self.canceled_bt)  # 추가팝업에서 취소버튼 누를시

    def truecontcheck(self):  # 반복 체크 상태에 따른 popup 띄우기
        if self.contcheck.checkState() == 2:  # 반복 체크 상태가 선택일 때
            cont_popup(self)  # 반복 팝업띄우기
        else:
            return

    def changecheckplan(self):  # 계획이 눌려지고 수업 토글
        if self.plancheck.isChecked() == True:
            self.classcheck.setChecked(False)
        else:
            self.classcheck.setChecked(True)

    def changecheckclass(self):  # 수업이 눌려지고 계획 토글
        if self.classcheck.isChecked() == True:
            self.plancheck.setChecked(False)
        else:
            self.plancheck.setChecked(True)

    def rgbradioClicked(self):  # 라디오 버튼이 클릭되면 rgb값 리턴
        if self.rgb1.isChecked():
            rgbr = "192,000,000"
        elif self.rgb2.isChecked():
            rgbr = "244,177,131"
        elif self.rgb3.isChecked():
            rgbr = "255,230,153"
        elif self.rgb4.isChecked():
            rgbr = "169,209,142"
        elif self.rgb5.isChecked():
            rgbr = "157,195,230"
        elif self.rgb6.isChecked():
            rgbr = "000,032,096"
        elif self.rgb7.isChecked():
            rgbr = "112,048,160"
        else:
            rgbr = ""
        return rgbr

    def saved_bt(self):  # 저장 버튼 눌렀을때 day 리스트에 같은 날짜가 들어있으면 안됨.
        namee = self.nameedit.text()
        memoe = self.memoedit.text()  # str
        datee = self.dateEdit.date()  # PyQt5.QtCore.QDate(2020, 11, 25) <class 'PyQt5.QtCore.QDate'>
        dateee = str(datee.toPyDate())  # 2020-12-25 <class 'datetime.date'> -> str로
        dateslice = dateee[2:]  # 2020-12-25을 20-12-25로
        datesplit = dateslice.split('-')  # 2020-12-25을 20,12,25로
        datejoin = "".join(datesplit)  # 20,12,25을 201225으로
        sts = self.st_tm.value()  # int
        eds = self.ed_tm.value()  # int
        class_planck = int(self.classcheck.isChecked())  # 수업 <class 'bool'> -> int로 true = 1 false = 0, 1이면 수업 0이면 계획
        rgbr = self.rgbradioClicked()  # 라디오 버튼으로 블록색 받아오기
        if self.contcheck.checkState() == 2 and namee != "" and rgbr != "" and sts < eds:
            try:
                conn = sqlite3.connect("conaTimetable.db")
                db_cur = conn.cursor()  # 커서 생성
                db_cur.execute(
                    "UPDATE timetable SET class_plan = {}, name = '{}', start_tm = {}, end_tm = {}, memo = '{}', block = '{}' WHERE date is not NULL AND name is NULL;".format(class_planck, namee, sts, eds, memoe, rgbr)
                )  # 기존 반복팝업으로 저장한 컬럼에 나머지 데이터값 db 추가
                conn.commit()
                conn.close()
                msg = QMessageBox.information(
                    self, "시간표 저장 완료", "계획이름: {}, 메모: {}, 시작시각: {}시, 종료시각: {}시".format(namee, memoe, sts, eds),
                    QMessageBox.Ok
                )
                if msg == QMessageBox.Ok:
                    result = self.close()
                else:
                    return
                if result:
                    self.close()
            except:
                QMessageBox.warning(
                    self, "시간표 저장 실패", "입력 오류 \n올바른 형식의 입력이 아닙니다.",
                    QMessageBox.Ok
                )
                return

        elif self.contcheck.checkState() == 0 and namee != "" and rgbr != "" and sts < eds:
            try:
                conn = sqlite3.connect("conaTimetable.db")
                cur = conn.cursor()  # 커서 생성
                cur.execute(
                    "INSERT INTO timetable (class_plan, name, date, start_tm, end_tm, memo, block) VALUES (?, ?, ?, ?, ?, ?, ?);", (class_planck, namee, datejoin, sts, eds, memoe, rgbr)
                )  # timetable에 데이터값 db 추가
                conn.commit()
                conn.close()
                msg = QMessageBox.information(
                    self, "시간표 저장 완료","계획이름: {}, 계획일: {}, 메모: {}\n시작시각: {}시, 종료시각: {}시".format(namee, datejoin, memoe, sts, eds),
                    QMessageBox.Ok
                )
                if msg == QMessageBox.Ok:
                    result = self.close()
                else:
                    return

                if result:
                    self.close()

            except:
                QMessageBox.warning(
                    self, "시간표 저장 실패", "입력 오류 \n계획 이름과 블록색상을 올바른 형식으로 지정해주세요.",
                    QMessageBox.Ok
                )
                return
        else:
            QMessageBox.warning(
                self, "시간표 저장 실패", "입력 오류 \n계획 이름과 블록색상을 지정을 반드시 해주세요.\n계획 종료 시각이 시작 시각보다 빠를 수 없습니다.",
                QMessageBox.Ok
            )
            return

    def canceled_bt(self):  # 취소 버튼 눌렀을때
        msg = QMessageBox.warning(

            self, "시간표 추가 취소", "지금까지 입력하신 정보는 사라집니다. 취소하시겠습니까?",

            QMessageBox.Yes | QMessageBox.No,

            QMessageBox.No

        )
        if msg == QMessageBox.Yes:
            if self.contcheck.checkState() == 2 or self.contcheck.checkState() == 0:
                conn = sqlite3.connect("conaTimetable.db")
                db_cur = conn.cursor()  # 커서 생성
                db_cur.execute(
                    "DELETE FROM timetable WHERE date != NULL and start_tm == NULL;"
                )  # 만약 반복 체크 된 상태/안 된 상태인데 NULL 값 인 db가 있으면 저장된 db값 삭제후 종료
                conn.commit()
                conn.close()
            result = self.close()
        else:
            return

        if result:
            self.close()

class share_popup(QDialog):  # 공유 팝업
    def __init__(self, parent):
        super(share_popup, self).__init__(parent)
        form_class2 = './sharepopup.ui'
        uic.loadUi(form_class2, self)
        self.show()
        self.setWindowTitle("공유하기")
        self.setWindowIcon(QIcon('conalogo.png'))
        self.setFixedSize(265, 130)
        self.share_image_bt.clicked.connect(self.sharepopup)  # 사진 저장하기 클릭 이벤트 sharepopup() 호출
        self.share_cafe_bt.clicked.connect(self.cafeurl)  # 카페 공유하기 클릭 이벤트 cafeurl() 호출

    def sharepopup(self):   # 캡쳐하기
        self.close()

    def cafeurl(self):  # 카페 연결 url 표시하기
        self.label.setText("<a href=\"https://cafe.naver.com/conatimetable\">CAFE로 이동하기</a>")
        self.label.setOpenExternalLinks(True)

class timetable_page(QDialog, form_class):  # 시간표 페이지 클래스
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # ui설정
        self.setWindowTitle("CONA")
        self.setWindowIcon(QIcon('conalogo.png'))
        self.add_bt.clicked.connect(self.timetable_add)  # 추가 버튼 클릭 이벤트 timetable_add() 호출
        self.share_bt.clicked.connect(self.timetable_share)  # 공유 버튼 클릭 이벤트 timetable_share() 호출
        #self.timetable_load()

    def enterEvent(self, QEvent):  # DB에서 시간표를 불러오기 위한 메소드 콜백 함수로 창을 건드릴때마다
        print("callback")
        conn = sqlite3.connect("conaTimetable.db")  # db 연결
        db_cur = conn.cursor()  # 커서 생성
        now = time.localtime(time.time())
        db_cur.execute("DELETE FROM timetable WHERE class_plan is NULL AND name is NULL AND start_tm is NULL AND end_tm is NULL AND block is NULL;")
        conn.commit()
        def What_day():  # 시작 할 때마다 요일 받아 일주일 날짜 리스트 받기
            if now.tm_wday == 0:  # 오늘이 월요일이면 월요일~일요일 날짜 리스트 받기
                today = int(time.strftime("%y%m%d", now))  # 오늘 날짜 yymmdd 형식
                start_date = time_to_date(today)
                endday = start_date + timedelta(days=6)
                st_date = date_to_time(start_date)
                ed_date = date_to_time(endday)
                daylist = change_date(st_date, ed_date, "nday", 1)
                return daylist
            elif now.tm_wday == 1:  # 오늘이 화요일이면 월요일(전날)~일요일 날짜 리스트 받기
                today = int(time.strftime("%y%m%d", now))
                start_date = time_to_date(today)
                mon_date = start_date - timedelta(days=1)
                endday = start_date + timedelta(days=5)
                st_date = date_to_time(mon_date)
                ed_date = date_to_time(endday)
                daylist = change_date(st_date, ed_date, "nday", 1)
                return daylist
            elif now.tm_wday == 2:  # 오늘이 수요일이면 월요일~일요일 날짜 리스트 받기
                today = int(time.strftime("%y%m%d", now))
                start_date = time_to_date(today)
                mon_date = start_date - timedelta(days=2)
                endday = start_date + timedelta(days=4)
                st_date = date_to_time(mon_date)
                ed_date = date_to_time(endday)
                daylist = change_date(st_date, ed_date, "nday", 1)
                return daylist
            elif now.tm_wday == 3:  # 오늘이 목요일이면 월요일~일요일 날짜 리스트 받기
                today = int(time.strftime("%y%m%d", now))
                start_date = time_to_date(today)
                mon_date = start_date - timedelta(days=3)
                endday = start_date + timedelta(days=3)
                st_date = date_to_time(mon_date)
                ed_date = date_to_time(endday)
                daylist = change_date(st_date, ed_date, "nday", 1)
                return daylist
            elif now.tm_wday == 4:  # 오늘이 금요일이면 월요일~일요일 날짜 리스트 받기
                today = int(time.strftime("%y%m%d", now))
                start_date = time_to_date(today)
                mon_date = start_date - timedelta(days=4)
                endday = start_date + timedelta(days=2)
                st_date = date_to_time(mon_date)
                ed_date = date_to_time(endday)
                daylist = change_date(st_date, ed_date, "nday", 1)
                return daylist
            elif now.tm_wday == 5:  # 오늘이 토요일이면 월요일~일요일 날짜 리스트 받기
                today = int(time.strftime("%y%m%d", now))
                start_date = time_to_date(today)
                mon_date = start_date - timedelta(days=5)
                endday = start_date + timedelta(days=1)
                st_date = date_to_time(mon_date)
                ed_date = date_to_time(endday)
                daylist = change_date(st_date, ed_date, "nday", 1)
                return daylist
            else:  # 오늘이 일요일이면 월요일~일요일 날짜 리스트 받기
                today = int(time.strftime("%y%m%d", now))
                start_date = time_to_date(today)
                mon_date = start_date - timedelta(days=6)
                st_date = date_to_time(mon_date)
                ed_date = date_to_time(start_date)
                daylist = change_date(st_date, ed_date, "nday", 1)
                return daylist
        week_list = What_day()
        # cur.execute 통해 timetable 테이블에서 SELECT 계획이름, 요일, 시작 시각, 종료 시각, 블록색상, 계획/수업 불러오기
        db_list = list()
        for item in week_list:  # 날짜 별로 리스트에 담아 오기
            db_cur.execute("SELECT name, date, start_tm, end_tm, memo, block, class_plan FROM timetable WHERE date = '{}'".format(item))
            table = db_cur.fetchall()  # cur.execute 통해 가져온 결과의 행을 가져와 리스트로 가져오기
            db_list.append(table)
        conn.close()  # db 연결 해제
        for date_list in db_list:  # 요일 하나씩 다루기
            list(set(date_list))
            for schedule in date_list:  # 한 요일안에 있는 시간표 하나씩 다루기 ('국어', '201204', 6, 7, 'zoom', '255,230,153')
                what_date = time_to_date(schedule[1])  # datetime객체로
                what_day = what_date.weekday()  # 4(금요일) 반환
                rgb = schedule[5]
                if int(schedule[3]) - int(schedule[2]) > 1:
                    st_tm = int(schedule[2])
                    if (schedule[0], schedule[1], st_tm + 1, schedule[3], schedule[4], schedule[5], schedule[6]) not in date_list:
                        while int(schedule[3]) - 1 != st_tm:
                            st_tm += 1
                            tm_plus = (schedule[0], schedule[1], st_tm, schedule[3], schedule[4], schedule[5], schedule[6])
                            date_list.append(tm_plus)
                            list(set(date_list))    # 중복제거
                if schedule[2] == 6 and what_day == 0 and self.m6.text() == "":  # 시작 시각 6시, 월요일
                    self.m6.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))  # 최대 6글자 표시
                    self.m6.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m6.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m6.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 7 and what_day == 0 and self.m7.text() == "":
                    self.m7.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m7.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m7.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m7.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 8 and what_day == 0 and self.m8.text() == "":
                    self.m8.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m8.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m8.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m8.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 9 and what_day == 0 and self.m9.text() == "":  # schedule[0][:6], schedule[4][:6] 변경.
                    self.m9.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m9.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m9.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m9.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 10 and what_day == 0 and self.m10.text() == "":
                    self.m10.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m10.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m10.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m10.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 11 and what_day == 0 and self.m11.text() == "":
                    self.m11.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m11.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m11.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m11.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 12 and what_day == 0 and self.m12.text() == "":
                    self.m12.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m12.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m12.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m12.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 13 and what_day == 0 and self.m13.text() == "":
                    self.m13.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m13.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m13.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m13.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 14 and what_day == 0 and self.m14.text() == "":
                    self.m14.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m14.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m14.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m14.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 15 and what_day == 0 and self.m15.text() == "":
                    self.m15.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m15.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m15.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m15.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 16 and what_day == 0 and self.m16.text() == "":
                    self.m16.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m16.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m16.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m16.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 17 and what_day == 0 and self.m17.text() == "":
                    self.m17.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m17.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m17.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m17.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 18 and what_day == 0 and self.m18.text() == "":
                    self.m18.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m18.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m18.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m18.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 19 and what_day == 0 and self.m19.text() == "":
                    self.m19.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m19.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m19.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m19.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 20 and what_day == 0 and self.m20.text() == "":
                    self.m20.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m20.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m20.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m20.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 21 and what_day == 0 and self.m21.text() == "":
                    self.m21.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m21.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m21.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m21.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 22 and what_day == 0 and self.m22.text() == "":
                    self.m22.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m22.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m22.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m22.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 23 and what_day == 0 and self.m23.text() == "":
                    self.m23.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.m23.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.m23.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.m23.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 6 and what_day == 1 and self.t6.text() == "":
                    self.t6.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t6.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t6.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t6.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 7 and what_day == 1 and self.t7.text() == "":
                    self.t7.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t7.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t7.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t7.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 8 and what_day == 1 and self.t8.text() == "":
                    self.t8.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t8.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t8.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t8.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 9 and what_day == 1 and self.t9.text() == "":
                    self.t9.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t9.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t9.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t9.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 10 and what_day == 1 and self.t10.text() == "":
                    self.t10.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t10.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t10.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t10.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 11 and what_day == 1 and self.t11.text() == "":
                    self.t11.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t11.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t11.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t11.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 12 and what_day == 1 and self.t12.text() == "":
                    self.t12.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t12.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t12.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t12.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 13 and what_day == 1 and self.t13.text() == "":
                    self.t13.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t13.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t13.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t13.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 14 and what_day == 1 and self.t14.text() == "":
                    self.t14.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t14.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t14.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t14.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 15 and what_day == 1 and self.t15.text() == "":
                    self.t15.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t15.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t15.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t15.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 16 and what_day == 1 and self.t16.text() == "":
                    self.t16.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t16.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t16.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t16.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 17 and what_day == 1 and self.t17.text() == "":
                    self.t17.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t17.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t17.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t17.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 18 and what_day == 1 and self.t18.text() == "":
                    self.t18.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t18.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t18.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t18.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 19 and what_day == 1 and self.t19.text() == "":
                    self.t19.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t19.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t19.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t19.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 20 and what_day == 1 and self.t20.text() == "":
                    self.t20.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t20.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t20.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t20.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 21 and what_day == 1 and self.t21.text() == "":
                    self.t21.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t21.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t21.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t21.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 22 and what_day == 1 and self.t22.text() == "":
                    self.t22.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t22.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t22.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t22.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 23 and what_day == 1 and self.t23.text() == "":
                    self.t23.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t23.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t23.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t23.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 6 and what_day == 2 and self.w6.text() == "":
                    self.w6.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w6.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w6.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w6.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 7 and what_day == 2 and self.w7.text() == "":
                    self.w7.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w7.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w7.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w7.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 8 and what_day == 2 and self.w8.text() == "":
                    self.w8.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w8.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w8.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w8.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 9 and what_day == 2 and self.w9.text() == "":
                    self.w9.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w9.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w9.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w9.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 10 and what_day == 2 and self.w10.text() == "":
                    self.w10.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w10.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w10.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w10.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 11 and what_day == 2 and self.w11.text() == "":
                    self.w11.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w11.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w11.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w11.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 12 and what_day == 2 and self.w12.text() == "":
                    self.w12.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w12.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w12.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w12.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 13 and what_day == 2 and self.w13.text() == "":
                    self.w13.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w13.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w13.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w13.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 14 and what_day == 2 and self.w14.text() == "":
                    self.w14.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w14.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w14.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w14.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 15 and what_day == 2 and self.w15.text() == "":
                    self.w15.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w15.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w15.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w15.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 16 and what_day == 2 and self.w16.text() == "":
                    self.w16.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w16.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w16.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w16.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 17 and what_day == 2 and self.w17.text() == "":
                    self.w17.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w17.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w17.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w17.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 18 and what_day == 2 and self.w18.text() == "":
                    self.w18.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w18.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w18.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w18.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 19 and what_day == 2 and self.w19.text() == "":
                    self.w19.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w19.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w19.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w19.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 20 and what_day == 2 and self.w20.text() == "":
                    self.w20.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w20.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w20.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w20.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 21 and what_day == 2 and self.w21.text() == "":
                    self.w21.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w21.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w21.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w21.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 22 and what_day == 2 and self.w22.text() == "":
                    self.w22.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w22.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w22.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w22.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 23 and what_day == 2 and self.w23.text() == "":
                    self.w23.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.w23.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.w23.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.w23.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 6 and what_day == 3 and self.t_6.text() == "":
                    self.t_6.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_6.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_6.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_6.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 7 and what_day == 3 and self.t_7.text() == "":
                    self.t_7.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_7.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_7.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_7.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 8 and what_day == 3 and self.t_8.text() == "":
                    self.t_8.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_8.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_8.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_8.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 9 and what_day == 3 and self.t_9.text() == "":
                    self.t_9.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_9.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_9.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_9.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 10 and what_day == 3 and self.t_10.text() == "":
                    self.t_10.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_10.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_10.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_10.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 11 and what_day == 3 and self.t_11.text() == "":
                    self.t_11.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_11.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_11.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_11.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 12 and what_day == 3 and self.t_12.text() == "":
                    self.t_12.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_12.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_12.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_12.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 13 and what_day == 3 and self.t_13.text() == "":
                    self.t_13.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_13.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_13.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_13.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 14 and what_day == 3 and self.t_14.text() == "":
                    self.t_14.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_14.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_14.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_14.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 15 and what_day == 3 and self.t_15.text() == "":
                    self.t_15.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_15.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_15.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_15.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 16 and what_day == 3 and self.t_16.text() == "":
                    self.t_16.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_16.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_16.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_16.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 17 and what_day == 3 and self.t_17.text() == "":
                    self.t_17.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_17.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_17.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_17.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 18 and what_day == 3 and self.t_18.text() == "":
                    self.t_18.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_18.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_18.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_18.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 19 and what_day == 3 and self.t_19.text() == "":
                    self.t_19.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_19.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_19.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_19.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 20 and what_day == 3 and self.t_20.text() == "":
                    self.t_20.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_20.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_20.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_20.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 21 and what_day == 3 and self.t_21.text() == "":
                    self.t_21.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_21.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_21.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_21.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 22 and what_day == 3 and self.t_22.text() == "":
                    self.t_22.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_22.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_22.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_22.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 23 and what_day == 3 and self.t_23.text() == "":
                    self.t_23.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.t_23.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.t_23.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.t_23.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 6 and what_day == 4 and self.f6.text() == "":
                    self.f6.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f6.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f6.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f6.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 7 and what_day == 4 and self.f7.text() == "":
                    self.f7.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f7.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f7.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f7.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 8 and what_day == 4 and self.f8.text() == "":
                    self.f8.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f8.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f8.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f8.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 9 and what_day == 4 and self.f9.text() == "":
                    self.f9.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f9.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f9.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f9.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 10 and what_day == 4 and self.f10.text() == "":
                    self.f10.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f10.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f10.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f10.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 11 and what_day == 4 and self.f11.text() == "":
                    self.f11.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f11.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f11.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f11.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 12 and what_day == 4 and self.f12.text() == "":
                    self.f12.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f12.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f12.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f12.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 13 and what_day == 4 and self.f13.text() == "":
                    self.f13.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f13.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f13.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f13.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 14 and what_day == 4 and self.f14.text() == "":
                    self.f14.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f14.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f14.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f14.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 15 and what_day == 4 and self.f15.text() == "":
                    self.f15.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f15.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f15.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f15.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 16 and what_day == 4 and self.f16.text() == "":
                    self.f16.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f16.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f16.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f16.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 17 and what_day == 4 and self.f17.text() == "":
                    self.f17.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f17.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f17.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f17.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 18 and what_day == 4 and self.f18.text() == "":
                    self.f18.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f18.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f18.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f18.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 19 and what_day == 4 and self.f19.text() == "":
                    self.f19.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f19.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f19.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f19.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 20 and what_day == 4 and self.f20.text() == "":
                    self.f20.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f20.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f20.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f20.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 21 and what_day == 4 and self.f21.text() == "":
                    self.f21.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f21.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f21.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f21.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 22 and what_day == 4 and self.f22.text() == "":
                    self.f22.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f22.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f22.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f22.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 23 and what_day == 4 and self.f23.text() == "":
                    self.f23.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.f23.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.f23.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.f23.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 6 and what_day == 5 and self.s6.text() == "":
                    self.s6.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s6.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s6.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s6.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 7 and what_day == 5 and self.s7.text() == "":
                    self.s7.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s7.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s7.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s7.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 8 and what_day == 5 and self.s8.text() == "":
                    self.s8.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s8.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s8.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s8.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 9 and what_day == 5 and self.s9.text() == "":
                    self.s9.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s9.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s9.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s9.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 10 and what_day == 5 and self.s10.text() == "":
                    self.s10.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s10.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s10.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s10.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 11 and what_day == 5 and self.s11.text() == "":
                    self.s11.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s11.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s11.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s11.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 12 and what_day == 5 and self.s12.text() == "":
                    self.s12.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s12.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s12.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s12.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 13 and what_day == 5 and self.s13.text() == "":
                    self.s13.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s13.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s13.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s13.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 14 and what_day == 5 and self.s14.text() == "":
                    self.s14.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s14.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s14.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s14.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 15 and what_day == 5 and self.s15.text() == "":
                    self.s15.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s15.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s15.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s15.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 16 and what_day == 5 and self.s16.text() == "":
                    self.s16.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s16.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s16.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s16.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 17 and what_day == 5 and self.s17.text() == "":
                    self.s17.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s17.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s17.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s17.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 18 and what_day == 5 and self.s18.text() == "":
                    self.s18.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s18.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s18.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s18.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 19 and what_day == 5 and self.s19.text() == "":
                    self.s19.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s19.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s19.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s19.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 20 and what_day == 5 and self.s20.text() == "":
                    self.s20.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s20.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s20.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s20.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 21 and what_day == 5 and self.s21.text() == "":
                    self.s21.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s21.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s21.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s21.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 22 and what_day == 5 and self.s22.text() == "":
                    self.s22.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s22.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s22.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s22.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 23 and what_day == 5 and self.s23.text() == "":
                    self.s23.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s23.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s23.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s23.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 6 and what_day == 6 and self.s_6.text() == "":
                    self.s_6.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_6.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_6.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_6.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 7 and what_day == 6 and self.s_7.text() == "":
                    self.s_7.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_7.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_7.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_7.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 8 and what_day == 6 and self.s_8.text() == "":
                    self.s_8.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_8.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_8.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_8.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 9 and what_day == 6 and self.s_9.text() == "":
                    self.s_9.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_9.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_9.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_9.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 10 and what_day == 6 and self.s_10.text() == "":
                    self.s_10.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_10.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_10.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_10.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 11 and what_day == 6 and self.s_11.text() == "":
                    self.s_11.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_11.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_11.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_11.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 12 and what_day == 6 and self.s_12.text() == "":
                    self.s_12.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_12.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_12.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_12.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 13 and what_day == 6 and self.s_13.text() == "":
                    self.s_13.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_13.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_13.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_13.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 14 and what_day == 6 and self.s_14.text() == "":
                    self.s_14.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_14.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_14.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_14.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 15 and what_day == 6 and self.s_15.text() == "":
                    self.s_15.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_15.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_15.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_15.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 16 and what_day == 6 and self.s_16.text() == "":
                    self.s_16.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_16.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_16.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_16.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 17 and what_day == 6 and self.s_17.text() == "":
                    self.s_17.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_17.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_17.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_17.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 18 and what_day == 6 and self.s_18.text() == "":
                    self.s_18.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_18.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_18.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_18.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 19 and what_day == 6 and self.s_19.text() == "":
                    self.s_19.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_19.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_19.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_19.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 20 and what_day == 6 and self.s_20.text() == "":
                    self.s_20.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_20.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_20.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_20.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 21 and what_day == 6 and self.s_21.text() == "":
                    self.s_21.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_21.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_21.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_21.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 22 and what_day == 6 and self.s_22.text() == "":
                    self.s_22.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_22.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_22.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_22.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))
                if schedule[2] == 23 and what_day == 6 and self.s_23.text() == "":
                    self.s_23.setText("{}\n{}".format(schedule[0][:6], schedule[4][:6]))
                    self.s_23.setFont(QtGui.QFont("Gulim", 9, QtGui.QFont.Bold))
                    self.s_23.setStyleSheet("color: white; background-color : rgb({}); border-radius: 5px;".format(rgb))
                    self.s_23.clicked.connect(lambda state, name=schedule[0], date=schedule[1], sts=schedule[2], eds=schedule[3], memo=schedule[4], rgbs=schedule[5], cp=schedule[6]: self.timetable_clicked(state, name, date, sts, eds, memo, rgbs, cp))

    # 시간표 블럭을 클릭했을때 정보를 보여주고 일정삭제도 가능하게 하기 위한 메소드
    def timetable_clicked(self, state, name, date, sts, eds, memo, rgbs, cp):
        clicked_popup(self, name, date, sts, eds, memo, rgbs, cp)

    def timetable_add(self):  # 시간표를 추가하여 DB에 저장하기 위한 메소드
        add_popup(self)

    def timetable_share(self):  # 작성한 시간표 공유하기 위한 메소드
        share_popup(self)
        rect = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(cp)
        x = rect.x()  # 0
        y = rect.y()  # 0
        w = rect.width() + x  # 677
        h = rect.height() + y  # 523
        box = (x, y, w, h)
        img = ImageGrab.grab(box)
        saveas = 'capture.png'
        img.save(saveas)

    # ============================================================================================================

# 시퀀스 자료형 언팩용 메소드
def unpacked(tu):
    return tu


# DB의 테이블 만들기 - 프로그램 설치 시 최초 1회 실행
def create_time_table():
    conn = sqlite3.connect("conaTimetable.db")
    db_curs = conn.cursor()
    db_curs.execute("create table time (save_day text, save_time integer);")
    db_curs.execute("create table setting (before_alarm integer, start_alarm integer, advice integer);")
    db_curs.execute("create table total (total_time integer);")
    conn.commit()
    db_curs.close()


# 초 단위 시간을 시분초로 변경 / 반환 = (h, m, s)
def show_time(data):
    minuit = (data // 60) % 60
    hour = data // 3600
    second = data % 60

    return hour, minuit, second


# 오늘 요일을 한글로 반환
def today_is_day():
    day = time.strftime('%a', time.localtime(time.time()))

    if day == 'Mon':
        return "월요일"
    elif day == 'Tue':
        return "화요일"
    elif day == 'Wed':
        return "수요일"
    elif day == 'Thu':
        return "목요일"
    elif day == 'Fri':
        return "금요일"
    elif day == 'Sat':
        return "토요일"
    else:
        return "일요일"


# 숫자 형식의 시간(tuple형 data)을 hh:mm:ss 꼴의 문자열로 반환해줌 / 반환 = hh:mm:ss (string)
def set_time(data):
    hou = ""
    minu = ""
    sec = ""
    if data[0] < 10:
        hou = "0" + str(data[0])
    else:
        hou = str(data[0])

    if data[1] < 10:
        minu = "0" + str(data[1])
    else:
        minu = str(data[1])

    if data[2] < 10:
        sec = "0" + str(data[2])
    else:
        sec = str(data[2])

    return hou + ":" + minu + ":" + sec


# h, m, s를 받아 "00시간\n00분\n00초" 꼴로 반환
def view_hms(h, m, s):
    hou = ""
    minu = ""
    sec = ""
    if h < 10:
        hou = "0" + str(h)
    else:
        hou = str(h)

    if m < 10:
        minu = "0" + str(m)
    else:
        minu = str(m)

    if s < 10:
        sec = "0" + str(s)
    else:
        sec = str(s)

    return hou + "시간\n" + minu + "분\n" + sec + "초"


# value의 whole에 대한 퍼센트를 계산 / 반환 = 00
def sum_percent(value, whole):
    if whole == 0:
        return 100

    result = value / whole * 100
    print(result)
    return int(result)


# total 테이블에 접근해 총 누적 시간을 받아옴 / 반환 = 총 시간 초
def get_total():
    conn = sqlite3.connect(DBfile)
    db_curs = conn.cursor()
    db_curs.execute("SELECT * FROM total")
    conn.commit()
    data_list = db_curs.fetchall()  # data_list는 각 record tuple을 원소로 가진 list
    conn.close()

    if data_list:
        totalTime = unpacked(*data_list[len(data_list) - 1])  # 맨 마지막 값
        return totalTime
    else:
        return False


# 조언 사용 여부를 받아옴 / 반환 = 1 or 0
def get_setting_advice():
    conn = sqlite3.connect(DBfile)
    db_curs = conn.cursor()

    db_curs.execute("SELECT * FROM setting;")  # 전체 내용 검색
    conn.commit()
    setting_value = db_curs.fetchall()

    if setting_value:
        _, _, result = setting_value[0]
    else:  # 알람 사용 설정값이 없는 경우
        result = 0
    conn.close()

    return result


# DB에서 day의 누적 공부 시간을 받아오기 위한 메소드 / 반환 = (date, time)
def get_time(day):
    if type(day) is not str:  # 날짜 값이 string이 아닌 경우, DB의 키 값이 문자열이라 오류가 남. 따라서 string으로 바꿔줌.
        day = str(day)

    conn = sqlite3.connect(DBfile)
    db_curs = conn.cursor()
    db_curs.execute("SELECT * FROM time WHERE save_day=" + day)  # 찾으려는 날짜를 key로 값 검색
    data_list = db_curs.fetchall()  # data_list는 각 record tuple을 원소로 가진 list
    conn.close()

    if not data_list:  # 저장된 데이터가 없는 경우
        return day, 0

    else:
        date, times = data_list[len(data_list) - 1]
        return date, times  # 하나의 값을 받아왔기 때문에 [('날짜', 시간)] 형식으로 반환됨
    # 만약 저장 과정에서 꼬여서 같은 키로 여러 값이 저장된 경우 가장 나중 값을 받아와야 하기 때문에


# day의 목표 시간(계획한 총 공부 시간)을 반환해줌 / 반환 = 총 시간 초
def get_day_target(day):
    # day는 반드시 yymmdd 꼴이어야.
    if type(day) is not str:  # 날짜 값이 string이 아닌 경우, DB의 키 값이 문자열이라 오류가 남. 따라서 string으로 바꿔줌.
        day = str(day)

    conn = sqlite3.connect(DBfile)
    db_curs = conn.cursor()
    db_curs.execute("SELECT start_tm, end_tm FROM timetable WHERE date=" + day + " AND class_plan=0")
    # 날짜가 day이고 계획인 열의 시작, 끝 시간 불러옴
    data_list = db_curs.fetchall()  # data_list는 각 record tuple을 원소로 가진 list
    conn.close()

    result = 0

    for start, end in data_list:
        result += end - start
    result = result * 60 * 60
    print(result)
    return result

def get_todolist(day):
    nolist = ["계획이", "없습니다"]
    if type(day) is not str:  # 날짜 값이 string이 아닌 경우, DB의 키 값이 문자열이라 오류가 남. 따라서 string으로 바꿔줌.
        day = str(day)
    conn = sqlite3.connect(DBfile)
    db_cur = conn.cursor()
    db_cur.execute("SELECT name FROM timetable WHERE class_plan = 0 AND date =" + day + ";")
    data_list = db_cur.fetchall()
    conn.close()  # db 연결 해제

    if not data_list:
        return nolist
    else:
        todolist = list()
        for i in data_list:
            x = unpacked(*i)
            print(x)
            todolist.append(x)
        return todolist


def get_schedule(day):
    nolist = ["", "", "", "", "", "", "", ""]
    if type(day) is not str:  # 날짜 값이 string이 아닌 경우, DB의 키 값이 문자열이라 오류가 남. 따라서 string으로 바꿔줌.
        day = str(day)
    conn = sqlite3.connect(DBfile)
    db_cur = conn.cursor()
    db_cur.execute("SELECT name FROM timetable WHERE class_plan = 1 AND date =" + day)
    data_list = db_cur.fetchall()
    conn.close()  # db 연결 해제

    todolist = list()
    for i in data_list:
        x = unpacked(*i)
        print(x)
        todolist.append(x)

    if len(todolist) < 8:
        for i in range(8-len(todolist)):
            todolist.append("")
    elif len(todolist) > 8:
        todolist = todolist[:8]

    if not data_list:
        return nolist

    else:
        return todolist


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = Form()
    ui.show()
    sys.exit(app.exec_())
