# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2005  Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
import re
import linecache
import time
import sys
try:
    import thread as _thread
except ImportError:
    import dummy_thread as _thread

# tracing
_trace_ignore = set()
_trace_filter = set()


def trace_ignore (names):
    """
    Add given names to trace ignore set, or clear set if names is None.
    """
    if names is None:
        _trace_ignore.clear()
    else:
        _trace_ignore.update(names)


def trace_filter (patterns):
    """
    Add given patterns to trace filter set or clear set if patterns is None.
    """
    if patterns is None:
        _trace_filter.clear()
    else:
        _trace_filter.update([re.compile(pat) for pat in patterns])


def _trace (frame, event, arg):
    """
    Trace function calls.
    """
    if event in ('call', 'c_call'):
        _trace_line(frame, event, arg)
    elif event in ('return', 'c_return'):
        _trace_line(frame, event, arg)
        print "  return:", arg
    #elif event in ('exception', 'c_exception'):
    #    _trace_line(frame, event, arg)
    return _trace


def _trace_full (frame, event, arg):
    """
    Trace every executed line.
    """
    if event == "line":
        _trace_line(frame, event, arg)
    else:
        _trace(frame, event, arg)
    return _trace_full


def _trace_line (frame, event, arg):
    """
    Print current executed line.
    """
    name = frame.f_globals["__name__"]
    if name in _trace_ignore:
        return _traceit
    for pat in _trace_filter:
        if not pat.match(name):
            return _traceit
    lineno = frame.f_lineno
    filename = frame.f_globals["__file__"]
    if filename.endswith(".pyc") or filename.endswith(".pyo"):
        filename = filename[:-1]
    line = linecache.getline(filename, lineno)
    print "THREAD(%d) %.2f %s # %s:%d" % \
           (_thread.get_ident(), time.time(), line.rstrip(), name, lineno)


def trace_on (full=False):
    """
    Start tracing of the current thread (and the current thread only).
    """
    if full:
        sys.settrace(_trace_full)
    else:
        sys.settrace(_trace)


def trace_off ():
    """
    Stop tracing of the current thread (and the current thread only).
    """
    sys.settrace(None)

