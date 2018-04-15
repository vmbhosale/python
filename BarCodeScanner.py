#!/usr/bin/python

import sys
import datetime
import sqlite3 as lite
from collections import deque
import csv

DAT_FILE='/apps/dataio/test.txt'
DEV_FILE='/dev/hidraw3'

def GetLastRow(csv_file):
        with open(csv_file, 'r') as f:
                try:
                        lastrow = deque(csv.reader(f), 1)[0]
                except IndexError:
                        lastrow = None
                return lastrow

def FileOperations():
        try:
                fileobj=open(DAT_FILE, 'a+')
                ExistingDishCount=fileobj.read()
                lastrow = GetLastRow(DAT_FILE)
                if lastrow is not None:
                        ExistingDishCount= int(lastrow[1])
                        NewCount=int(ExistingDishCount) + 1
                else:
                        NewCount = 1
                fileobj.seek(0)
                Dat= str(datetime.datetime.now()) + "," + str(NewCount)
                fileobj.write(str(Dat) + "\n")
                print "New count is " + str(NewCount)
                fileobj.close()
        except IOError:
                print "Error: can\'t find file or read data..."

def SleepSomeTime(tm):
        from time import sleep
        sleep(tm)

def QueryBarCodesDB():
        codestr=""
        try:
                conn1=lite.connect('mypidb.db')
                with conn1:
                        curs=conn1.cursor()
                        for bcodes in curs.execute("select code from barcodetbl"):
                                codestr=bcodes[0] + " " + codestr
                return codestr
        except lite.Error, e:
                if conn1:
                        conn1.rollback()
                print "Error %s:" %e.args[0]
                sys.exit(1)
        finally:
                if conn1:
                        conn1.close()

def QueryMaxID():
        Maxid=""
        try:
                conn2=lite.connect('mypidb.db')
                with conn2:
                        curs=conn2.cursor()
                        for ids in curs.execute("select max(id) from barcodetbl"):
                                Maxid=ids[0]
                        return str(Maxid)
        except lite.Error, e:
                if conn2:
                        conn2.rollback()
                print "Error %s:" %e.args[0]
                sys.exit(1)
        finally:
                if conn2:
                        conn2.close()

def AddRecordInDB(BarCode):
        try:
                conn3=lite.connect('mypidb.db')
                with conn3:
                        Maxid = QueryMaxID()
                        Nextid = int(Maxid) + 1
                        curs=conn3.cursor()
                        curs.execute("insert into scanrecordtbl values ((?), (?), date('now'), time('now'))", (Nextid, BarCode))
                        conn3.commit()
        except lite.Error, e:
                if conn3:
                        conn3.rollback()
                print "Error %s:" %e.args[0]
                sys.exit(1)
        finally:
                if conn3:
                        conn3.close()


def GetData():
        hid = { 4: 'a', 5: 'b', 6: 'c', 7: 'd', 8: 'e', 9: 'f', 10: 'g', 11: 'h', 12: 'i', 13: 'j', 14: 'k', 15: 'l', 16: 'm', 17: 'n', 18: 'o', 19: 'p', 20: 'q', 21: 'r', 22: 's', 23: 't', 24: 'u', 25: 'v', 26: 'w', 27: 'x', 28: 'y', 29: 'z', 30: '1', 31: '2', 32: '3', 33: '4', 34: '5', 35: '6', 36: '7', 37: '8', 38: '9', 39: '0', 44: ' ', 45: '-', 46: '=', 47: '[', 48: ']', 49: '\\', 51: ';' , 52: '\'', 53: '~', 54: ',', 55: '.', 56: '/'  }

        hid2 = { 4: 'A', 5: 'B', 6: 'C', 7: 'D', 8: 'E', 9: 'F', 10: 'G', 11: 'H', 12: 'I', 13: 'J', 14: 'K', 15: 'L', 16: 'M', 17: 'N', 18: 'O', 19: 'P', 20: 'Q', 21: 'R', 22: 'S', 23: 'T', 24: 'U', 25: 'V', 26: 'W', 27: 'X', 28: 'Y', 29: 'Z', 30: '!', 31: '@', 32: '#', 33: '$', 34: '%', 35: '^', 36: '&', 37: '*', 38: '(', 39: ')', 44: ' ', 45: '_', 46: '+', 47: '{', 48: '}', 49: '|', 51: ':' , 52: '"', 53: '~', 54: '<', 55: '>', 56: '?'  }

        fp = open('/dev/hidraw3', 'rb', buffering=-1)
        BarCodeVal = ""
        shift = False
        done = False
        while not done:
                ## Get the character from the HID
                buffer = fp.read(8)
                SleepSomeTime(0.001)
                for c in buffer:
                        if ord(c) > 0:
                                if int(ord(c)) == 40:
                                        done = True
                                        break;
                                if shift:
                                        if int(ord(c)) == 2 :
                                                shift = True
                                        else:
                                                BarCodeVal += hid2[ int(ord(c)) ]
                                                shift = False
                                else:
                                        if int(ord(c)) == 2 :
                                                shift = True
                                        else:
                                                BarCodeVal += hid[ int(ord(c)) ]
        fp.close()
        NoSpecCharBarCode = str(BarCodeVal).replace('\n','').replace('\r','').replace('\t','')
        from itertools import islice
        gen = (e for e in NoSpecCharBarCode if e.isalnum())
        PureBarCode = ''.join(gen)
        BarCodeConStr=QueryBarCodesDB()
        BarCodeStr=str(BarCodeConStr)
        if PureBarCode in BarCodeStr:
                AddRecordInDB(PureBarCode)
                print "Yesss! Barcode IS FOUND in the DB..."
        else:
                print "Barcode database is NOT INITIALIZED or this barcode is NOT FOUND in the database!"

def CheckForData():
        try:
                GetData()
        except IOError:
                print "Error: Please make sure that you are reading a correct hidraw device!"
                sys.exit(1)

while True:
        CheckForData()
