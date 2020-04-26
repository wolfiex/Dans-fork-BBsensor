import power, time

print('starting')
thread = power.blink_nonblock_inf(n=4000)


time.sleep(20)
print('stopping')
power.stopblink(thread)


time.sleep(10)
print('stop')
