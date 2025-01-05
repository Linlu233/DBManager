import sys
import pyodbc
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, \
    QWidget, QLineEdit, QMessageBox, QComboBox, QHBoxLayout


class SchoolInfoManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initDB()

    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('学校信息管理系统')
        self.setGeometry(100, 100, 1000, 800)

        # 主布局
        self.mainLayout = QVBoxLayout()

        # 顶部选择框布局
        self.topLayout = QHBoxLayout()

        # 实体选择下拉框
        self.entitySelector = QComboBox(self)
        self.entitySelector.addItems(['学生', '班级', '教师', '课程', '分数'])
        self.entitySelector.currentIndexChanged.connect(self.loadData)
        self.topLayout.addWidget(self.entitySelector)

        # 表格选择下拉框
        self.tableSelector = QComboBox(self)
        self.topLayout.addWidget(self.tableSelector)

        # 添加顶部布局到主布局
        self.mainLayout.addLayout(self.topLayout)

        # 显示数据的表格
        self.tableWidget = QTableWidget()
        self.mainLayout.addWidget(self.tableWidget)

        # 输入字段
        self.inputField = QLineEdit(self)
        self.inputField.setPlaceholderText('输入数据 (例如: 姓名, 年龄, 班级, 课程, 教师)')
        self.mainLayout.addWidget(self.inputField)

        # 操作按钮
        self.addButton = QPushButton('添加数据', self)
        self.addButton.clicked.connect(self.addData)
        self.mainLayout.addWidget(self.addButton)

        self.updateButton = QPushButton('更新数据', self)
        self.updateButton.clicked.connect(self.updateData)
        self.mainLayout.addWidget(self.updateButton)

        self.deleteButton = QPushButton('删除数据', self)
        self.deleteButton.clicked.connect(self.deleteData)
        self.mainLayout.addWidget(self.deleteButton)

        # 主窗口小部件
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

    def initDB(self):
        # 使用 pyodbc 连接到 SQL Server 数据库
        try:
            self.connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                                             'SERVER=localhost;'
                                             'DATABASE=Test;'
                                             'Trusted_Connection=yes;')
            self.cursor = self.connection.cursor()

            # 创建各个实体的表格
            self.cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Classes' AND xtype='U')
                CREATE TABLE Classes (
                    ClassName VARCHAR(50) PRIMARY KEY,
                    HeadTeacher VARCHAR(50),
                    CourseName VARCHAR(100)
                )
            ''')

            self.cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Courses' AND xtype='U')
                CREATE TABLE Courses (
                    CourseID INT PRIMARY KEY,
                    CourseName VARCHAR(50),
                    Credit INT
                )
            ''')

            self.cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Students' AND xtype='U')
                CREATE TABLE Students (
                    StudentID INT IDENTITY(1,1) PRIMARY KEY,
                    StudentName VARCHAR(50),
                    Gender VARCHAR(10),
                    BirthDate DATE,
                    ClassName VARCHAR(50),
                    FOREIGN KEY (ClassName) REFERENCES Classes(ClassName)
                )
            ''')

            self.cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Teachers' AND xtype='U')
                CREATE TABLE Teachers (
                    TeacherID INT PRIMARY KEY,
                    TeacherName VARCHAR(50),
                    CourseID INT,
                    ClassName VARCHAR(50),
                    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID),
                    FOREIGN KEY (ClassName) REFERENCES Classes(ClassName)
                )
            ''')

            self.cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Scores' AND xtype='U')
                CREATE TABLE Scores (
                    StudentID INT,
                    CourseID INT,
                    RegularScore INT,
                    FinalScore INT,
                    PRIMARY KEY (StudentID, CourseID),
                    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
                    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
                )
            ''')

            self.connection.commit()
            self.updateTableSelector()
            self.loadData()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'数据库连接失败: {str(e)}')

    def updateTableSelector(self):
        # 更新表格选择下拉框，仅显示已创建的表格
        self.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type='BASE TABLE'")
        tables = [table[0] for table in self.cursor.fetchall()]
        self.tableSelector.clear()
        self.tableSelector.addItems(tables)

    def loadData(self):
        # 根据选择的实体加载数据
        entity = self.entitySelector.currentText()
        if entity == '学生':
            self.cursor.execute("SELECT * FROM Students")
            rows = self.cursor.fetchall()
            self.tableWidget.setRowCount(len(rows))
            self.tableWidget.setColumnCount(6)
            self.tableWidget.setHorizontalHeaderLabels(['学生ID', '姓名', '性别', '出生日期', '班级'])
        elif entity == '班级':
            self.cursor.execute("SELECT * FROM Classes")
            rows = self.cursor.fetchall()
            self.tableWidget.setRowCount(len(rows))
            self.tableWidget.setColumnCount(3)
            self.tableWidget.setHorizontalHeaderLabels(['班级名称', '班主任', '课程名称'])
        elif entity == '教师':
            self.cursor.execute("SELECT * FROM Teachers")
            rows = self.cursor.fetchall()
            self.tableWidget.setRowCount(len(rows))
            self.tableWidget.setColumnCount(4)
            self.tableWidget.setHorizontalHeaderLabels(['教师ID', '教师姓名', '课程ID', '班级名称'])
        elif entity == '课程':
            self.cursor.execute("SELECT * FROM Courses")
            rows = self.cursor.fetchall()
            self.tableWidget.setRowCount(len(rows))
            self.tableWidget.setColumnCount(3)
            self.tableWidget.setHorizontalHeaderLabels(['课程ID', '课程名称', '学分'])
        elif entity == '分数':
            self.cursor.execute("SELECT * FROM Scores")
            rows = self.cursor.fetchall()
            self.tableWidget.setRowCount(len(rows))
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setHorizontalHeaderLabels(['学生ID', '课程ID', '平时成绩', '期末成绩'])

        for rowIndex, row in enumerate(rows):
            for colIndex, col in enumerate(row):
                self.tableWidget.setItem(rowIndex, colIndex, QTableWidgetItem(str(col)))

    def addData(self):
        # 根据选择的实体添加数据到数据库
        try:
            entity = self.entitySelector.currentText()
            if entity == '学生':
                student_name, gender, birth_date, class_name = self.inputField.text().split(',')
                self.cursor.execute(
                    "INSERT INTO Students (StudentName, Gender, BirthDate, ClassName) VALUES (?, ?, ?, ?)",
                    (student_name.strip(), gender.strip(), birth_date.strip(), class_name.strip()))
            elif entity == '班级':
                class_name, head_teacher, course_name = self.inputField.text().split(',')
                self.cursor.execute("INSERT INTO Classes (ClassName, HeadTeacher, CourseName) VALUES (?, ?, ?)",
                                    (class_name.strip(), head_teacher.strip(), course_name.strip()))
            elif entity == '教师':
                teacher_name, course_id, class_name = self.inputField.text().split(',')
                self.cursor.execute("INSERT INTO Teachers (TeacherName, CourseID, ClassName) VALUES (?, ?, ?)",
                                    (teacher_name.strip(), int(course_id.strip()), class_name.strip()))
            elif entity == '课程':
                course_name, credit = self.inputField.text().split(',')
                self.cursor.execute("INSERT INTO Courses (CourseName, Credit) VALUES (?, ?)",
                                    (course_name.strip(), int(credit.strip())))
            elif entity == '分数':
                student_id, course_id, regular_score, final_score = self.inputField.text().split(',')
                self.cursor.execute(
                    "INSERT INTO Scores (StudentID, CourseID, RegularScore, FinalScore) VALUES (?, ?, ?, ?)",
                    (int(student_id.strip()), int(course_id.strip()), int(regular_score.strip()),
                     int(final_score.strip())))

            self.connection.commit()
            self.loadData()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'添加数据失败: {str(e)}')

    def updateData(self):
        # 根据选择的实体更新数据库中的数据
        try:
            selectedRow = self.tableWidget.currentRow()
            if selectedRow == -1:
                QMessageBox.warning(self, '警告', '请先选择要更新的数据!')
                return

            entity = self.entitySelector.currentText()
            values = [self.tableWidget.item(selectedRow, i).text() for i in range(self.tableWidget.columnCount())]

            if entity == '学生':
                self.cursor.execute(
                    "UPDATE Students SET StudentName = ?, Gender = ?, BirthDate = ?, ClassName = ? WHERE StudentID = ?",
                    (values[1], values[2], values[3], values[4], values[0]))
            elif entity == '班级':
                self.cursor.execute("UPDATE Classes SET HeadTeacher = ?, CourseName = ? WHERE ClassName = ?",
                                    (values[1], values[2], values[0]))
            elif entity == '教师':
                self.cursor.execute(
                    "UPDATE Teachers SET TeacherName = ?, CourseID = ?, ClassName = ? WHERE TeacherID = ?",
                    (values[1], values[2], values[3], values[0]))
            elif entity == '课程':
                self.cursor.execute("UPDATE Courses SET CourseName = ?, Credit = ? WHERE CourseID = ?",
                                    (values[1], values[2], values[0]))
            elif entity == '分数':
                self.cursor.execute(
                    "UPDATE Scores SET RegularScore = ?, FinalScore = ? WHERE StudentID = ? AND CourseID = ?",
                    (values[2], values[3], values[0], values[1]))

            self.connection.commit()
            self.loadData()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'更新数据失败: {str(e)}')

    def deleteData(self):
        # 根据选择的实体删除数据库中的数据
        try:
            selectedRow = self.tableWidget.currentRow()
            if selectedRow == -1:
                QMessageBox.warning(self, '警告', '请先选择要删除的数据!')
                return

            entity = self.entitySelector.currentText()
            id_value = self.tableWidget.item(selectedRow, 0).text()

            if entity == '学生':
                self.cursor.execute("DELETE FROM Students WHERE StudentID = ?", (id_value,))
            elif entity == '班级':
                self.cursor.execute("DELETE FROM Classes WHERE ClassName = ?", (id_value,))
            elif entity == '教师':
                self.cursor.execute("DELETE FROM Teachers WHERE TeacherID = ?", (id_value,))
            elif entity == '课程':
                self.cursor.execute("DELETE FROM Courses WHERE CourseID = ?", (id_value,))
            elif entity == '分数':
                course_id = self.tableWidget.item(selectedRow, 1).text()
                self.cursor.execute("DELETE FROM Scores WHERE StudentID = ? AND CourseID = ?", (id_value, course_id))

            self.connection.commit()
            self.loadData()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'删除数据失败: {str(e)}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SchoolInfoManagementSystem()
    window.show()
    sys.exit(app.exec_())
