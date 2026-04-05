import random
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