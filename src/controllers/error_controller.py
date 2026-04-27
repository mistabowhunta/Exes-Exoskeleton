#!/usr/bin/env python3
import os
import logging

logging.basicConfig(filename="my_stuffs.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def main():
    logger.debug('')

def msg(filename, function, msg):
    logger.debug('Filename: ' + filename + ' | ' + 'Function: ' + function + ' | Msg: ' + str(msg))

def one_variable(filename, function, msg, variable):
    logger.debug('Filename: ' + filename + ' | Function: ' + function + ' | Msg: ' + str(msg) + ' | Variable: ' + str(variable))

def two_variables(filename, function, msg, variable_one, variabl_two):
    logger.debug('Filename: ' + filename + ' | Function: ' + function + ' | Msg: ' + str(msg) + ' | Variable 1: ' + str(variable_one) + ' | Variable 2: ' + str(variabl_two))

def three_variables(filename, function, msg, variable_one, variable_two, variable_three):
    logger.debug('Filename: ' + filename + ' | Function: ' + function + ' | Msg: ' + str(msg) + ' | Variable 1: ' + str(variable_one) + ' | Variable 2: ' + str(variabl_two) + ' | Variable 3: ' + str(variable_three))

if __name__ == '__main__':
    main()