#!/usr/bin/env python2

import functools

class Cell():
    def __init__(self, value=None):
        self.set_value(value)

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def __str__(self):
        return str(self.value)

import logging

def add_before(my_class, fn_name, new_fn):
    fn = getattr(my_class, fn_name)
    def wrapper(*args):
        new_fn(*args)
        return fn(*args)
    setattr(my_class, fn_name, wrapper)
    return

def main():
    cell1 = Cell(1)
    print cell1

    def logit(self, value):
        print "value is " + str(value)
        
    #import pdb; pdb.set_trace()
    add_before(Cell, "set_value", logit)
    cell1.set_value(2)
    print cell1

if __name__ == '__main__':
    main()

# The End
# vim:foldmethod=indent:foldnestmax=2
