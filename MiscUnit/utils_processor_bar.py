import sys, time


def procesor_bar(bar='=', lside='[', rside=']', total=20):
    sys.stdout.write(lside)
    sys.stdout.write(' ' * total)
    sys.stdout.write(rside)
    sys.stdout.flush()
    cur_pos = 1
    while cur_pos <= total:
        step = 0
        while step <= ((total + 1) - cur_pos):
            sys.stdout.write('\b')
            step += 1
        sys.stdout.write('%s' % bar)
        sys.stdout.write(' ' * (total - cur_pos))
        sys.stdout.write(rside)
        sys.stdout.flush()
        time.sleep(0.5)
        cur_pos += 1

if __name__ == '__main__':
    procesor_bar()
    pass