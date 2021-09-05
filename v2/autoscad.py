#!/usr/bin/python3

import sys
import os
import pathlib
import psutil
import inotify.adapters
import inotify.constants as IN

def execute(filename):
    print(f'[RUNNING] {filename}')
    os.system(f'{sys.executable} "{filename}"')

def run_openscad_maybe(scadfile):
    # first, try to see whether there is already an openscad process for this
    # file (this is imprecise, but good enough for my use case)
    for proc in psutil.process_iter():
        if proc.name() == 'openscad' and str(scadfile) in proc.cmdline():
            print(f'Found existing openscad process for file {scadfile}, PID {proc.pid}')
            return
    print('Running openscad...')
    os.system(f'openscad "{scadfile}" &')

def main():
    if len(sys.argv) != 2:
        print('Usage: autoscad.py FILE.py')
        return
    pyfile = pathlib.Path(sys.argv[1])
    execute(pyfile)
    # XXX: this assumes that executing FILE.py produces /tmp/autoscad.scad
    scadfile = '/tmp/autoscad.scad'
    run_openscad_maybe(scadfile)

    # rerun FILE.py as soon as any *.py file is created/modified/deleted
    MASK = IN.IN_CLOSE_WRITE | IN.IN_CREATE | IN.IN_DELETE
    i = inotify.adapters.InotifyTree('.', mask=MASK)
    try:
        for event in i.event_gen():
            if event is None:
                continue
            (header, type_names, watch_path, filename) = event
            if filename.endswith('.py') and not filename.startswith('.#'):
                execute(pyfile)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()

