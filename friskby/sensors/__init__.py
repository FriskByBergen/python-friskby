"""The sensors submodule of friskby.

Contains drivers for all known sensors, currently only SDS011, though.
"""
from __future__ import absolute_import

from .sds011 import SDS011

__all__ = ['SDS011']
