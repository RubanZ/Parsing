import csv
import io
from xml.sax.saxutils import XMLGenerator

import sys

import six
from scrapy.exporters import BaseItemExporter
from scrapy.utils.serialize import ScrapyJSONEncoder
from scrapy.utils.python import to_bytes, is_listlike, to_native_str
from scrapy.conf import settings

class CsvItemExporter(BaseItemExporter):

    def __init__(self, file, include_headers_line=True, join_multivalued=',', **kwargs):
        self._configure(kwargs, dont_fail=True)
        if not self.encoding:
            self.encoding = 'utf-8'
        self.include_headers_line = include_headers_line
        self.stream = io.TextIOWrapper(
            file,
            line_buffering=False,
            write_through=True,
            encoding=self.encoding
        ) if six.PY3 else file
        self.csv_writer = csv.writer(self.stream, lineterminator='\n', quotechar='"', quoting=csv.QUOTE_ALL)
        self._headers_not_written = True
        self._join_multivalued = join_multivalued

    def serialize_field(self, field, name, value):
        serializer = field.get('serializer', self._join_if_needed)
        return serializer(value)

    def _join_if_needed(self, value):
        if isinstance(value, (list, tuple)):
            try:
                return self._join_multivalued.join(value)
            except TypeError:  # list in value may not contain strings
                pass
        return value

    def export_item(self, item):
        if self._headers_not_written:
            self._headers_not_written = False
            self._write_headers_and_set_fields_to_export(item)

        fields = self._get_serialized_fields(item, default_value='',
                                             include_empty=True)
        values = list(self._build_row(x for _, x in fields))
        # values = [i.replace("\r","").replace("\n","") for i in values]
        # print values
        self.csv_writer.writerow(values)

    def _build_row(self, values):
        for s in values:
            try:
                yield to_native_str(s, self.encoding)
            except TypeError:
                yield s

    def _write_headers_and_set_fields_to_export(self, item):
        if self.include_headers_line:
            if not self.fields_to_export:
                if isinstance(item, dict):
                    # for dicts try using fields of the first item
                    self.fields_to_export = list(item.keys())
                else:
                    # use fields declared in Item
                    self.fields_to_export = list(item.fields.keys())
            row = list(self._build_row(self.fields_to_export))
            self.csv_writer.writerow(row)


class UniversalXmlItemExporter(BaseItemExporter):

    def __init__(self, file, **kwargs):

        self._configure(kwargs)
        if not self.encoding:
            self.encoding = 'utf-8'
        self.encoding = self.encoding.upper()

        self.indent = settings.get('UXML_INDENT', 0)

        self.item_element = settings.get("UXML_ITEM", "item")
        self.root_element = settings.get("UXML_ROOT", "items")

        self.xg = XMLGenerator(file, encoding=self.encoding)

    def _beautify_newline(self, new_item=False):
        if self.indent is not None and (self.indent > 0 or new_item):
            self._xg_characters('\n')

    def _beautify_indent(self, depth=1):
        if self.indent:
            self._xg_characters(' ' * self.indent * depth)

    def start_exporting(self):
        self.xg.startDocument()
        self.xg.startElement(self.root_element, {})
        self._beautify_newline(new_item=True)

    def export_item(self, item):
        self._beautify_indent(depth=1)
        _attrs = {}
        for key in item.keys():
            if key.startswith("_"):
                _attrs[key[1:]] = item[key]
        _tag = self.item_element
        if "tag" in _attrs:
            _tag = _attrs.pop("tag")
        self.xg.startElement(_tag, _attrs)
        self._beautify_newline()
        for name, value in self._get_serialized_fields(item, default_value=''):
            if name.startswith("_"):
                continue
            _sub_attrs = {}
            if hasattr(value, 'items'):
                for key in value.keys():
                    if key.startswith("_"):
                        _sub_attrs[key[1:]] = value[key]
            _sub_tag = name
            if "tag" in _sub_attrs:
                _sub_tag = _sub_attrs.pop("tag")
            _out_value = None
            if "value" in _sub_attrs:
                _out_value = _sub_attrs.pop("value")

            self._export_xml_field(_sub_tag, value, depth=2, attrs=_sub_attrs, out_value=_out_value)
        self._beautify_indent(depth=1)
        self.xg.endElement(self.item_element)
        self._beautify_newline(new_item=True)

    def finish_exporting(self):
        self.xg.endElement(self.root_element)
        self.xg.endDocument()

    def _export_xml_field(self, name, serialized_value, depth, attrs=None, out_value=None):
        self._beautify_indent(depth=depth)

        if attrs is None:
            attrs = {}
        if out_value is not None:
            serialized_value = out_value

        if serialized_value is None:
            self.xg.ignorableWhitespace("<%s/>" % name)
            self._beautify_newline()
            return

        self.xg.startElement(name, attrs)
        if hasattr(serialized_value, 'items'):
            self._beautify_newline()
            for subname, value in serialized_value.items():
                if subname.startswith("_"):
                    continue
                _attrs = {}

                if hasattr(value, 'items'):
                    for key in value.keys():
                        if key.startswith("_"):
                            _attrs[key[1:]] = value[key]

                _tag = subname
                if "tag" in _attrs:
                    _tag = _attrs.pop("tag")

                _out_value = None
                if "value" in _attrs:
                    _out_value = _attrs.pop("value")

                self._export_xml_field(_tag, value, depth=depth + 1, attrs=_attrs, out_value=_out_value)
            self._beautify_indent(depth=depth)
        elif is_listlike(serialized_value):
            self._beautify_newline()
            _is_dict_inside = True
            for value in serialized_value:
                if not hasattr(value, 'items'):
                    _is_dict_inside = False
                    break
            if _is_dict_inside:
                for value in serialized_value:
                    _sub_attrs = {}
                    for key in value.keys():
                        if key.startswith("_"):
                            _sub_attrs[key[1:]] = value[key]
                    _sub_tag = 'value'
                    if "tag" in _sub_attrs:
                        _sub_tag = _sub_attrs.pop("tag")

                    _sub_out_value = None
                    if "value" in _sub_attrs:
                        _sub_out_value = _sub_attrs.pop("value")

                    self._export_xml_field(_sub_tag, value, depth=depth + 1, out_value=_sub_out_value)
            else:
                for value in serialized_value:
                    self._export_xml_field('value', value, depth=depth + 1)
            self._beautify_indent(depth=depth)
        elif isinstance(serialized_value, six.text_type):
            self._xg_characters(serialized_value)
        else:
            self._xg_characters(str(serialized_value))
        self.xg.endElement(name)
        self._beautify_newline()

    # Workaround for https://bugs.python.org/issue17606
    # Before Python 2.7.4 xml.sax.saxutils required bytes;
    # since 2.7.4 it requires unicode. The bug is likely to be
    # fixed in 2.7.6, but 2.7.6 will still support unicode,
    # and Python 3.x will require unicode, so ">= 2.7.4" should be fine.
    if sys.version_info[:3] >= (2, 7, 4):
        def _xg_characters(self, serialized_value):
            if not isinstance(serialized_value, six.text_type):
                serialized_value = serialized_value.decode(self.encoding)
            return self.xg.characters(serialized_value)
    else:  # pragma: no cover
        def _xg_characters(self, serialized_value):
            return self.xg.characters(serialized_value)
