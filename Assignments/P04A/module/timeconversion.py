#!/usr/bin/env python3
##############################################################################
# Author: Caleb Sneath
# Assignment: P04 - Missile Defence Part 2
# Date: October 31, 2022
# Python 3.9.5
# Project Version: 0.2.0
#
# Description: A simple Python library to convert times between various 
#              different formats.
#
##############################################################################

import time
import datetime

"""
convertTimeToSecondsSimple
Converts a timestamp in a day containing hour, minute, and second units
into a plain timestamp containing only the timestamp in seconds.
Parameters:         inTime: String containing a time code in the format of
                            "hour:minute:second" without quotes
Returns:            timecode converted into plain seconds as a string.
"""
def convertTimeToSecondsSimple(inTime):
    # Example inTime: "12:12:07"
    # Split the segments, convert them to seconds
    tempTime2 = inTime.split(':')
    return str(int(tempTime2[0]) * 3600 + int(tempTime2[1]) * 60 + float(tempTime2[2]))

"""
convertTimeFromSecondsNoDate
Converts a timestamp in a day from seconds to contain an hour, minute, and second units
into a plain timestamp containing only the timestamp in seconds. This isn't the real
time, just a simulation time
Parameters:         inTime: timecode in plain seconds as a string.
Returns:            String containing a time code in the format of
                            "hour:minute:second" without quotes
"""
def convertTimeFromSecondsNoDate(inTime):
    hourMark = int(inTime) / 3600
    tempTime = float(inTime) - (hourMark * 3600)
    minuteMark = int(tempTime / 60)
    tempTime = float (tempTime) - minuteMark * 60
    return str(hourMark) + ":" + str(minuteMark) + ":" + str(tempTime)

"""
convertTimeToSecondsNoDate
Converts a timestamp in a day containing hour, minute, and second units
into a plain timestamp containing only the timestamp in seconds.
Parameters:         inTime: String containing a time code in the format of
                            "hour:minute:second" without quotes
Returns:            timecode converted into plain seconds as a string.
"""
def convertTimeToSecondsNoDate(inTime):
    # Example inTime: "2022-10-27 12:12:07.833257"
    # Split the space, grab only the second part
    temptime1 = inTime.split(' ')[1]
    tempTime2 = temptime1.split(':')
    return str(int(tempTime2[0]) * 3600 + int(tempTime2[1]) * 60 + float(tempTime2[2]))


def convertTimeToSeconds(inTime):
    """
    convertTimeToSeconds
    Converts a timestamp in a day containing hour, minute, and second units
    into a plain timestamp containing only the timestamp in seconds.
    Parameters:         inTime: String containing a time code in the format of
                                "year-month-day hour:minute:second" without quotes
    Returns:            timecode converted into plain seconds as a string.
    """
    # Example inTime: "2022-10-27 12:12:07.833257"
    return ((datetime.datetime.fromisoformat(inTime)).timestamp())


def convertTimeFromSeconds(inTime):
    """
    convertTimeFromSeconds
    Converts a timestamp in a day from seconds to contain an hour, minute, and second units
    into a plain timestamp containing only the timestamp in seconds. This isn't the real
    time, just a simulation time
    Parameters:         inTime: timecode in plain seconds as a string.
    Returns:            String containing a time code in the format of
                                "year-month-day hour:minute:second" without quotes
    """
    # Example return time: "2022-10-27 12:12:07.833257"
    return str(datetime.datetime.fromtimestamp(int(inTime)).isoformat(' '))

def convertDateToOtherDate(inTime):
    """
    convertDateToOtherDate
    Converts a timestamp in a day from datetime to a different date format.
    Warning: Won't work beginning year 10,000.
    Parameters:         inTime: timecode in datetime format.
    Returns:            String containing a time code in the format of
                                "day/month/year hour:minute:second" without quotes
    """
    # Example input time:  "2022-10-27 12:12:07.833257"
    # Example return time: “27/10/22 12:12:07”
    tempString = str(inTime)
    rawString = str(tempString.replace(" ", "-")).split("-")
    print(rawString)
    year = str(rawString[0][2::])
    return (rawString[2] + '/' + rawString[1] + '/' + year + ' ' + rawString[3])
    

print(convertTimeFromSeconds("1555555555"))