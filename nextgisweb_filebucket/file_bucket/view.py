# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

from nextgisweb.dynmenu import DynItem, Label, Link
from nextgisweb.resource import Resource, Widget

from .model import FileBucket
from .util import _


class Widget(Widget):
    resource = FileBucket
    operation = ('create', 'update')
    amdmod = 'ngw-file-bucket/Widget'


class FileBucketMenu(DynItem):
    def build(self, args):
        yield Label('file_bucket', _('File bucket'))

        if isinstance(args.obj, FileBucket):
            yield Link(
                'resource/export', _('Export'),
                lambda args: args.request.route_url('resource.export', id=args.obj.id),
            )


def setup_pyramid(comp, config):
    Resource.__dynmenu__.add(FileBucketMenu())

    Resource.__psection__.register(
        key='file_bucket', priority=20, title=_("File bucket"),
        is_applicable=lambda obj: isinstance(obj, FileBucket),
        template='nextgisweb_filebucket:file_bucket/template/section.mako')
