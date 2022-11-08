#!/usr/bin/env python


class Class2():
    def __init__(self, obj):
        self.class1_obj: Class1 = obj
    
    def do_thing(self):
        Class2.gen_random(self.class1_obj.rand)
    
    @staticmethod
    def gen_random(rand):
        print(f"Random number: {rand.normal(0,1)}")