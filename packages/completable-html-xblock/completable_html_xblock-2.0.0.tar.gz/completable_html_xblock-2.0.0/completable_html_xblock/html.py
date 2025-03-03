"""This XBlock help creating a secure and easy-to-use HTML blocks in edx-platform."""

from __future__ import absolute_import

import logging

import pkg_resources
from html_xblock import HTML5XBlock
from html_xblock.utils import _
from xblock.completable import CompletableXBlockMixin
from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.utils.resources import ResourceLoader

log = logging.getLogger(__name__)
xblock_loader = ResourceLoader(__name__)


class CompletableHTML5XBlock(CompletableXBlockMixin, HTML5XBlock):
    """
    This XBlock will disable completion and add provide and  an HTML WYSIWYG interface in Studio to be rendered in LMS.
    """

    display_name = String(
        display_name=_('Display Name'),
        help=_('The display name for this component.'),
        scope=Scope.settings,
        default=_('Completable'),
    )
    allow_javascript = True
    editor = String(
        help=_(
            'Select Visual to enter content and have the editor automatically create the HTML. Select Raw to edit '
            'HTML directly. If you change this setting, you must save the component and then re-open it for editing.'
        ),
        display_name=_('Editor'),
        default='raw',
        values=[{'display_name': _('Visual'), 'value': 'visual'}, {'display_name': _('Raw'), 'value': 'raw'}],
        scope=Scope.settings,
    )
    has_custom_completion = True
    editable_fields = ('display_name', 'editor')

    @staticmethod
    def completable_resource_string(path):
        """We need to subclass this, because we don't want to override its usages in superclass methods."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode('utf8')

    @XBlock.supports('multi_device')
    def student_view(self, context=None):
        """
        Return a fragment that contains the html for the student view. Add #complete element.
        """
        frag = super().student_view()
        frag.add_javascript(self.completable_resource_string('static/js/html_completion.js'))
        frag.initialize_js('HTML5CompletionXBlock')

        return frag

    @XBlock.json_handler
    def complete(self, _data, _suffix=''):
        """
        Use new completion API for marking the block as completed.
        """
        self.emit_completion(1.0)
