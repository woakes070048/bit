# coding=utf-8
from __future__ import absolute_import, unicode_literals
import re
from collections import OrderedDict

__all__ = ['FileDateTimeLookup']


class FileDateTimeLookup(object):
    expression = ".*/{folder}/(?P<date>\d{{4}}-\d{{2}}-\d{{2}})" \
                 "/(?P<time>\d{{2}}-\d{{2}})/{file_prefix}.*\\.json" \
                 "(\\.(?P<part_number>\d+)){{0,1}}"
    folder = None
    file_prefix = None

    @classmethod
    def lookup_files(cls, storage):
        """
        Lookup Files
        :param storage: Storage
        :type storage: Storage
        :return: Ordered Dict
        """
        pattern = cls.expression.format(
            folder=cls.folder, file_prefix=cls.file_prefix
        )

        expression = re.compile(pattern=pattern)
        files = OrderedDict()
        for key, match in storage.find(cls.folder, expression):
            date = match.group('date')
            time = match.group('time')
            part_number = match.group('part_number')

            if date not in files:
                files[date] = OrderedDict()

            if part_number is not None:
                part_number = int(part_number)
                if time not in files[date]:
                    files[date][time] = OrderedDict()
                files[date][time][part_number] = key
            else:
                files[date][time] = key

        return files
