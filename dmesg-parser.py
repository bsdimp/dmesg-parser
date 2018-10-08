#!/usr/bin/env python3
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import argparse
import os
import re
import copy

class DmesgFile(object):
    release = None
    memory = None
    cpu = None
    freq = None
    ncpu = None
    drivers = set([])

    RELEASE_RE = re.compile(r'^FreeBSD (\d+).\d+[^-]*-.*$')
    MEMORY_RE = re.compile(r'^real memory\s+=\s+(\d+).*$')
    CPU_RE = re.compile(r'^CPU: (.*)$')
    # This works only for x86 systems
    # ARM has less defined format for CPU models
    FREQ_RE = re.compile(r'\((\d+\.\d+)-MHz')
    DEVICE_RE = re.compile(r'([a-z]+)\d+: .* on \w+$')
    NCPU_RE = re.compile('FreeBSD/SMP: Multiprocessor System Detected: (\d+) CPUs')

    def __init__(self, path):
        self.__path = path
        self.drivers = set([])
        self.__parse()

    def __repr__(self):
        return 'Dmesg({}, {}, {})'.format(self.release, self.cpu, self.memory)

    def __parse(self):
        dmesg_data = None
        with open(self.__path, 'r') as f:
            try:
                dmesg_data = f.read()
            except:
#               print('Bad file ', self.__path);
                dmesg_data = ''
        lines = dmesg_data.split('\n')
        for line in lines:
            if self.release is None:
                match = self.RELEASE_RE.match(line)
                if match:
                    self.release = match.group(1)
                    continue
            if self.memory is None:
                match = self.MEMORY_RE.match(line)
                if match:
                    self.memory = int(match.group(1))
                    continue
            if self.cpu is None:
                match = self.CPU_RE.match(line)
                if match:
                    self.cpu = match.group(1)
                    freq_match = self.FREQ_RE.search(self.cpu)
                    if freq_match:
                        self.freq = freq_match.group(1)
                    continue
            if self.ncpu is None:
                match = self.NCPU_RE.match(line)
                if match:
                    self.ncpu = match.group(1)
                    continue
            match = self.DEVICE_RE.match(line)
            if match:
                driver = match.group(1)
                self.drivers.add(driver)

parser = argparse.ArgumentParser()
parser.add_argument('datadir', type=str, help='directory with dmesg files')
args = parser.parse_args()

dmesgs = []
for path in os.listdir(args.datadir):

    # Ignore hidden files
    if path.startswith('.'):
        continue

    full_path = os.path.join(args.datadir, path)

    # Ignore everythin taht is not regular file
    if not (os.path.isfile(full_path)):
        continue

    dmesg = DmesgFile(full_path)
    if dmesg.release is None:
        continue
    dmesgs.append(copy.deepcopy(dmesg))

release = {}
for d in dmesgs:
    r = int(d.release)
    if r in release:
        release[r] = release[r] + 1
    else:
        release[r] = 1
# This works 
print ('major, count')
total = 0
for r in release:
    print (r, ',', release[r])
    total = total + release[r]
print('total', ',', total)
print('')

# and this works
drv_count = {}
for d in dmesgs:
    r = int(d.release)
    for drv in d.drivers:
        if drv in drv_count:
            drv_count[drv] = drv_count[drv] + 1
        else:
            drv_count[drv] = 1
for d in drv_count:
    print (d, drv_count[d])

# but this doesn't work, ideas
d_vs_r = [[0 for x in drv_count] for y in release]
for d in dmesgs:
    r = int(d.release)
    for drv in d.drivers:
        d_vs_r[drv][r] = d_vs_r[drv][r] + 1
for d in drv_count:
    print (drv, d_vs_r[drv])
