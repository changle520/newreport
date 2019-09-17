#coding:utf8

class Student(object):
    count = 0

    def __init__(self, name):
        self.name = name
        Student.count = Student.count + 1


rey=Student('rey')
print(rey.count)

rey=Student('cale')
print(rey.count)

chang=Student('changle')
print(chang.count)