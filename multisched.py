#!/usr/bin/env python

import time
import threading

#  multisched is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  multisched is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with multisched.  If not, see <http://www.gnu.org/licenses/>.
#
# (C) 2012- by Adam Tauber, <asciimoo@gmail.com>


# http://code.activestate.com/recipes/114644-scheduler/


class Task(threading.Thread):
    def __init__(self, action, loopdelay, initdelay, threads=0):
        self._action        = action
        self._loopdelay     = loopdelay
        self._initdelay     = initdelay
        self._running       = 1
        self._threads       = threads
        self._cur_threads   = 0
        threading.Thread.__init__(self)

    def _action_wrapper(self):
        self._cur_threads += 1
        self._action()
        self._cur_threads -= 1

    def __repr__(self):
        return '[%-4d] %-20s %6s %6s' % (self._threads
                                       ,self._action.__name__
                                       ,self._loopdelay
                                       ,self._initdelay
                                       )

    def run(self):
        if self._initdelay:
            time.sleep(self._initdelay)
        self._runtime = time.time()
        is_called = False
        while self._running:
            start = time.time()
            if self._threads:
                if self._threads > self._cur_threads:
                    t = threading.Thread(target=self._action_wrapper, args=[])
                    t.start()
                #else:
                #     print '%s thread limit reached' % self._action.__name__
            else:
                self._action()
            self._runtime += self._loopdelay
            if self._runtime-start > 0:
                time.sleep( self._runtime - start )
            else:
                self._runtime = time.time()

    def stop(self):
        self._running = 0

class Scheduler:
    def __init__(self):
        self._tasks = []

    def __repr__(self):
        rep = ''
        for task in self._tasks:
            rep += '%s\n' % `task`
        return rep

    def AddTask(self, loopdelay, initdelay = 0, threads=0):
        def act(action):
            def new(self):
                return action(self)
            task = Task(action, loopdelay, initdelay, threads)
            self._tasks.append(task)
            return new
        return act

    def AddTasks(self, tasks):
        self._tasks.extend(Task(**task) for task in tasks)

    def StartAllTasks(self):
        for task in self._tasks:
            task.start()

    def StopAllTasks(self):
        for task in self._tasks:
            print 'Stopping task', task
            task.stop()
            print 'Stopped'

if __name__ == '__main__':

    # example "logger" function
    def timestamp(s):
        print '%.2f : %s' % (time.time(), s)

    # example callable task action
    class Action():
        def __init__(self, name):
            self.__name__       = name
            self.call_counter   = 0

        def __call__(self):
            self.call_counter  += 1
            print 'I am %s (%d)' % (self.__name__, self.call_counter)

    s = Scheduler()
    # ----------------------------------.
    #                                   |
    #  TASK PARAMS:                     |
    #                                   |
    #    loopdelay:   float, required   |
    #    initdelay:   float, default=0  |
    #    threads  :   int  , default=0  |
    #                                   |
    # ----------------------------------`
    @s.AddTask(loopdelay=1.3)
    def task1():
        timestamp('task1')

    @s.AddTask(loopdelay=1.0, initdelay=3)
    def task2():
        timestamp('task2')
        time.sleep(1.6)
        timestamp('task2 again')

    @s.AddTask(loopdelay=1.1, threads=4)
    def task3():
        timestamp('task3')
        time.sleep(4.4)
        timestamp('task3 again')

    s.AddTasks({'action'    : Action('Agent%03d' % n)
               ,'loopdelay' : 0.6
               ,'initdelay' : 1.1
               ,'threads'   : 0
               }
               for n in xrange(42))
    print s
    s.StartAllTasks()
    try:
        raw_input()
    except:
        pass
    s.StopAllTasks()