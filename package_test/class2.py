#!/usr/bin/env python


class Class2():
    def __init__(self, obj):
        self.class1_obj: Class1 = obj
        self.class1_obj.do_thing()