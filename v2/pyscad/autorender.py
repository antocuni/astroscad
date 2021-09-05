#!/usr/bin/python3

import sys
import os
import psutil
import inotify.adapters
import inotify.constants as IN

def run_openscad_maybe(scadfile):
    # first, try to see whether there is already an openscad process for this
    # file (this is imprecise, but good enough for my use case)
    for proc in psutil.process_iter():
        if proc.name() == 'openscad' and str(scadfile) in proc.cmdline():
            #print(f'Found existing openscad process for file {scadfile}, PID {proc.pid}')
            return
    print('Running openscad...')
    os.system(f'openscad "{scadfile}" &')

def autorender(obj, filename, **kwargs):
    obj.render_to_file(filename, **kwargs)
    run_openscad_maybe(filename)

    # reload as soon as any *.py file is created/modified/deleted
    MASK = IN.IN_CLOSE_WRITE | IN.IN_CREATE | IN.IN_DELETE
    i = inotify.adapters.InotifyTree('.', mask=MASK)
    try:
        for event in i.event_gen():
            if event is None:
                continue
            (header, type_names, watch_path, filename) = event
            if filename.endswith('.py') and not filename.startswith('.#'):
                print(f'change detected, reloading: {filename}')
                os.execl(sys.executable, 'python3', *sys.argv)
    except KeyboardInterrupt:
        pass
