avg_check = 120
avg_ppl = 4
stripe_fee, stripe_base = .03, 0.3
cm_fee, cm_base = .025, 0.3
spend_target = 1000000

paying_users = avg_ppl - 1
check_pay_size = ((avg_check / avg_ppl) * paying_users)

per_check_cost = check_pay_size * stripe_fee + stripe_base*paying_users
per_check_rev = check_pay_size * cm_fee + cm_base*paying_users

total_spent_cm = 0
money_spent_irl = 0
stripe_cost = 0
checks = 0
cm_rev = 0
while money_spent_irl <= spend_target:
    total_spent_cm += per_check_cost
    cm_rev += per_check_rev
    checks += 1
    money_spent_irl += avg_check
    if total_spent_cm >= 500:
        stripe_cost += per_check_cost
print(f"${money_spent_irl} of checks, on {checks} receipts will cost us {round(stripe_cost, 2)}")
print(f" our additional revenue will be {round(cm_rev, 2)} give a P/L of {round(cm_rev - stripe_cost, 2)}")
print(total_spent_cm)
print(f"each persons ${avg_check / avg_ppl} bill would cost {(avg_check / avg_ppl)*(1+cm_fee) + cm_base}")
ad_rev = (avg_ppl * checks * 20 * 2)/1000
print(ad_rev)