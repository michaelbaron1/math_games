import random
"""
this game is just about how well you can calculate the day of the week for a given date.
======
LOGIC:
starts at year 400, with that months 7 days of week as follows:
jan: fri
feb: mon
mar: tues
apr: fri 
may: sun 
jun: wed 
jul: fri 
aug: mon 
sep: thurs 
oct: sat 
nov: tues 
dec: thurs
for tickers counting:
    +1 for each day, +1 for each year +1 for each leap year
    # a leap year is all divisible by 4, except for years that are divisible by 100, but not divisible by 400
    # ie +24 per century + possible century leap
    # always can simplify down with %7
    # if year is a leap year, then jan and feb dont get +1 till following year
    
logical check:
year = 1020
day = 18
def my_func(year, day):
    # step 1 - years
    days = (year - 400) % 7
    # step 2: LY per century
    cents = (year - 400) // 100
    days += (cents * 3) % 7
    # step 3: LY on the century
    #cents = -1
    for i in range(400, year, 100):
        
        if i%400 == 0 and i > 400:
            
            days +=1
    # step 3: leap years past the century
    days += (year % 100) // 4
    days += (day % 7)
    days = days % 7
    return days
print(my_func(year, day))
    
"""
def jf_pipeline(month, day, year):
    counter = 0
    for i in range(401,year+1):

        if (str(i-1)[-2:]) == "00":
            if (i-1)%400 == 0:
                counter += 2
            else:
                counter += 1
        else:
            if (i-1)%4 == 0:
                counter +=2
            else:
                counter +=1
    counter += day%7
    return counter

def rest_pipeline(month,day,year):
    counter = 0
    for i in range(401, year + 1):

        if (str(i)[-2:]) == "00":
            if i % 400 == 0:
                counter += 2
            else:
                counter += 1
        else:
            if (i) % 4 == 0:
                counter += 2
            else:
                counter += 1
    counter += day % 7
    return counter
def get_date():
    starter_days = {"jan": 5, "feb": 1, "mar": 2, "apr": 5, "may": 7, "jun": 3,
                     "jul": 5, "aug": 1, "sep": 4, "oct": 6, "nov": 2, "dec": 4}
    month_list = list(starter_days.keys())
    month = random.choice(month_list)
    day = random.randint(1,28)
    year = random.randint(400, 2025)
    print(f"{month}/{day}/{year}")
    proceed = input("would you like to proceed(Y)")
    if proceed == "yes" or proceed == "Yes" or proceed == "Y" or proceed == "y":
        if month == "jan" or month == "feb":
            extra = jf_pipeline(month, day, year)
        else:
            extra = rest_pipeline(month, day, year)
    day_key = ((starter_days[month] + extra)%7) - 1
    days_of_week = ["mon", "tues", "wed", "thurs", "fri", "sat", "sun"]
    return days_of_week[day_key]

print(get_date())
print(get_date())
print(get_date())