"""
HTML XBlock tests
"""

from __future__ import print_function

import unittest

from xblock.field_data import DictFieldData
from xblock.test.tools import TestRuntime

import completable_html_xblock


class TestHTMLXBlock(unittest.TestCase):
    """
    Unit tests for `completable_html_xblock`
    """

    def setUp(self):
        self.runtime = TestRuntime()

    def test_render_with_completion(self):
        """
        Test a basic rendering with custom completion enabled.
        Expects that `HTML5CompletionXBlock` JS function was initialized and `tracker` is present in the resources.
        """
        field_data = DictFieldData(
            {
                'data': '<p>Safe <b>html</b><script>alert(\'javascript\');</script></p>',
            }
        )
        block = completable_html_xblock.CompletableHTML5XBlock(self.runtime, field_data, None)
        self.assertEqual(block.has_custom_completion, True)
        fragment = block.student_view()
        self.assertIn('<p>Safe <b>html</b><script>alert(\'javascript\');</script></p>', fragment.content)
        self.assertIn('HTML5CompletionXBlock', fragment.js_init_fn)
        self.assertIn('var handlerUrl', fragment.foot_html())
