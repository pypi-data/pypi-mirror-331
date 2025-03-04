#!/usr/bin/env python3
#coding:utf-8

__author__ = 'xmxoxo<xmxoxo@qq.com>'

import time

class TimeCount():
    '''简单计时器'''

    def __init__(self):
        self.clean()

    def clean(self):
        '''重置计时器'''
        self.total_time = 0
        self.time_list = []
        self.split_times = []
        self.current_split_start = None
        self.status = 0

    def stop(self):
        '''停止计时器并重置'''
        self.clean()

    def restart(self):
        self.pause()
        self.resume()

    def start(self):
        self.resume()

    def begin(self, show=0):
        '''开始或继续计时'''
        if self.status == 0:
            self.current_split_start = time.time()
        else:
            self.resume()
        self.status = 1
        if show:
            print('计时开始...')

    def pause(self, pause=1):
        '''暂停计时，记录当前分段时间'''
        if self.status == 1:
            current_time = time.time()
            split_time = current_time - self.current_split_start

            self.time_list.append((self.current_split_start, current_time))
            self.split_times.append(split_time)
            self.total_time += split_time
            if pause==1:
                self.status = 0
            return split_time #* 1000, split_time * 1000 / 1000  # ms 和 s 单位

    def resume(self):
        '''恢复计时'''
        if self.status == 0:
            self.begin(show=False)

    def show_splits(self, pre_text='用时', unit='ms'):
        '''显示所有分段时间'''
        for i, split in enumerate(self.split_times):
            if unit == 'ms':
                outtxt = f'{pre_text} 第{i + 1}段: {split * 1000:.3f} [毫秒]'
            elif unit == 's':
                outtxt = f'{pre_text} 第{i + 1}段: {split:.3f} [秒]'
            print(outtxt)

    def show(self, pre_text='总用时:', unit='ms', showmsg=1):
        ret = self.show_total(pre_text=pre_text, unit=unit, showmsg=showmsg)
        return ret

    def show_total(self, pre_text='总用时:', unit='ms', showmsg=1):
        '''显示总计时'''
        last_times = self.pause(pause=0)
        last_times_ms = last_times * 1000

        total_time_ms = self.total_time * 1000
        total_time_s = self.total_time

        if unit == 'ms':
            outtxt = f'{pre_text} {total_time_ms:.3f} [{last_times_ms:.3f}]毫秒'
            last_times = last_times_ms
        elif unit == 's':
            outtxt = f'{pre_text} {total_time_s:.3f} [{last_times:.3f}]秒'
        if showmsg==1:
            print(outtxt)

        return total_time_ms, last_times, outtxt

def test_timecount():
    ''' 单元测试 '''

    tc = TimeCount()
    tc.start()
    # ... 进行某项操作 ...
    time.sleep(2.7)
    elapsed_time  = tc.pause()
    print(f"第一段时间: {elapsed_time} ms")

    tc.resume()
    # ... 继续进行其他操作 ...
    time.sleep(3.46)
    another_elapsed_time = tc.pause()
    print(f"第二段时间: {another_elapsed_time} ms")

    tc.show_splits()
    tc.show_total()

# -----------------------------------------
class TimeCount1():
    '''简单计时器 '''

    def __init__(self):
        self.clean()

    def clean(self):
        ''' 重置计时器
        '''
        self.ntime = 0
        self.time_list = []
        self.status = 0

    def stop(self):
        ''' 停止计时器
        '''
        self.clean()

    def restart(self):
        self.stop()
        self.begin()

    def start(self):
        self.begin()

    def begin(self, show=0):
        ''' 开始计时
        '''
        self.ntime = time.time()
        self.status = 1
        if show:
            print('计时开始...')

    def pause(self):
        ''' 记录当前计时，返回开始到当前的时间: 毫秒
        '''
        if self.status == 0:
            self.begin()

        n = (time.time() - self.ntime)*1000
        self.time_list.append(n)
        return n

    def tcount(self):
        ''' 返回计时器所有清单
        '''
        tlist = self.time_list
        # usetime_list = np.diff(tlist).tolist()
        # dat = dict(zip(tlist, [0] + usetime_list))
        return self.time_list

    def show(self, pre_text='用时', unit='ms', showmsg=1):
        ''' 计时并显示时间
        '''
        t_total = self.pause()
        # 计算最后一次时间差
        last_utime = 0
        if len(self.time_list) > 1:
            last_utime = self.time_list[-1] - self.time_list[-2]

        if unit=='ms':
            outtxt = '%s:%.3f [%.3f](毫秒)'% (pre_text, et, last_utime)
        if unit=='s':
            outtxt = '%s:%.3f [%.3f](秒)'% (pre_text, et/1000, last_utime/1000)

        if showmsg:
            print(outtxt)
        # 返回：总用时以及最后一次时间差
        return t_total, last_utime, outtxt


if __name__ == '__main__':
    pass
    test_timecount()
