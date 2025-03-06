"""Tests for translatable_xblocks/util.py"""

from unittest import TestCase
from unittest.mock import patch

from lxml import etree

from translatable_xblocks.utils import (
    convert_html_to_xml,
    reinsert_base64_images,
    replace_img_base64_with_placeholder,
)


class TestHtmlXmlConversion(TestCase):
    """Tests for AiTranslationService."""

    @patch("translatable_xblocks.utils.get_platform_etree_lib")
    def test_convert_html_to_xml(self, mock_platform_etree):
        # edx-platform enforces its own import of etree for safety...
        # but for testing, we can just use etree
        mock_platform_etree.return_value = etree

        # Given an HTML response from the Google Translate API
        original_xml = '<option correct="False">Attributes should be quoted</option>'
        html_wrapped_xml = "<html><body><option correct=False>Attributes should be quoted</option></body></html>"

        # When I try to convert it to XML
        xml_output = convert_html_to_xml(html_wrapped_xml)

        # Then I get the expected output
        self.assertEqual(original_xml, xml_output)


class TestBase64ImageReplacement(TestCase):
    """Tests for replacing base64 images with placeholders."""

    def test_base64_image_replace(self):
        text = (
            "<p>Here is an image:</p>"
            '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA" alt="Example">'
            "<p>Another paragraph.</p>"
            '<img src="data:image/jpg;base64,iBlahBlahBlah" alt="Example2">'
        )

        expected_text = (
            '<p>Here is an image:</p><img src="BASE64_IMG_PLACEHOLDER_0" alt="Example">'
            '<p>Another paragraph.</p><img src="BASE64_IMG_PLACEHOLDER_1" alt="Example2">'
        )

        replaced_text, base64_images = replace_img_base64_with_placeholder(text)

        self.assertEqual(expected_text, replaced_text)
        self.assertEqual(len(base64_images), 2)

        actual_text = reinsert_base64_images(replaced_text, base64_images)
        self.assertEqual(actual_text, text)
