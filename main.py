"""
Math games: a series of mini math and brain teaser games
"""
# all imports
import random

# end imports and set up
"""
DOUBLING COUNTER: pretend a stop watch starts. 
when a second goes by 1 is added to a side counter (the first addition being at seconds = 1) 
However, after s seconds, the side counter increments by +1 every half second, for s more seconds
this pattern continues. i.e given periods j=0 to n, each period increases side counter +1 every 1/(2^j) seconds
given random target = T, the stop watch will stop when the side counter = T
calculate as fast and close as possible how many seconds the stop watch will run
"""
def get_seconds(target, period_duration ):
    print(f"=================\ntarget: {target}\nperiod duration: {period_duration}")
    side_counter, n = 0, 0
    get_answer = input("proceed (Y): ")
    if get_answer == "Y" or get_answer == "y":
        while side_counter < target:
            # how much would get added to counter if full period ran
            full_period = period_duration/(1 / 2**n)
            if (side_counter + full_period) <= target:
                side_counter += full_period
                n +=1
                #print(f"{(n*period_duration)} seconds: {side_counter}")
            else:
                seconds = (period_duration * n) + (target - side_counter) / (2**n)
                side_counter += (target - side_counter)
            if side_counter == target: return seconds
print(get_seconds(random.randint(50, 9000), 2))
print(get_seconds(100, 2))
