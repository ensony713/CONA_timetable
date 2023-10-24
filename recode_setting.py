import time
import sqlite3
import sys
import random
from PyQt5.QtCore import QObject, QTimer, QTime, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from PyQt5 import QtCore, QtGui, QtWidgets
import setting_rc

window_width = 700
window_height = 500
toolbar_width = 70
toolbar_height = 510
rect_width = window_width - toolbar_width
rect_height = window_height
max_window = 500

DataBase = "./data/"  # DB 경로
DBfile = "conaTimetable.db"

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

        self.stack.addWidget(QTextEdit())
        self.stack.addWidget(QTextEdit())
        self.stack.addWidget(QTextEdit())
        self.stack.addWidget(recode())
        self.stack.addWidget(QTextEdit())
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
        self.day_goal = 0  # get_day_target(time.strftime('%y%m%d', self.now))
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
        date, times, _ = data_list[len(data_list) - 1]
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
    return result


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = Form()
    ui.show()
    sys.exit(app.exec_())
