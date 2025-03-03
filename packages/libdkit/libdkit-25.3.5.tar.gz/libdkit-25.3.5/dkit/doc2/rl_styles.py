# Copyright (c) 2025 Cobus Nel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
Reportlab Style repository
"""
from datetime import datetime
from importlib.resources import open_binary, open_text

import yaml
from reportlab.lib import colors, pagesizes
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from pydantic import BaseModel
from . import fontsize_map, document as doc
from .rl_helper import PdfImage


class DefaultStyler(object):
    """default rl_renderer styler

    Used by rl_render to generate pdf documents
    this class can be inherited to implement new styles
    for different document standards
    """

    def __init__(self, document: doc.Document, local_style: dict = None):
        if local_style:
            self.local_style = local_style
        else:
            self.local_style = self.load_local_style(
                "dkit.resources", "rl_stylesheet.yaml"
            )
        self.doc = document
        self.style = getSampleStyleSheet()
        self.unit = cm
        self.register_fonts()
        self.update_styles()

    def __getitem__(self, key):
        return self.style[key]

    def load_local_style(self, location, filename):
        """
        load default style update

        arguments:
            - location: module name
            - filename: yaml file name
        """
        with open_text(location, filename) as infile:
            return yaml.safe_load(infile)

    @property
    def title_date(self):
        fmt = self.local_style["page"]["title_date_format"]
        _date = self.doc.date if self.doc.date else datetime.now()
        return fmt.format(_date)

    @property
    def left_margin(self):
        return self.local_style["page"]["left"] / 10 * self.unit

    @property
    def right_margin(self):
        return self.local_style["page"]["right"] / 10 * self.unit

    @property
    def top_margin(self):
        return self.local_style["page"]["top"] / 10 * self.unit

    @property
    def bottom_margin(self):
        return self.local_style["page"]["bottom"] / 10 * self.unit

    @property
    def page_size(self):
        size_map = {
            "A4": pagesizes.A4,
            "A5": pagesizes.A5,
            "LETTER": pagesizes.LETTER
        }
        return size_map[self.local_style["page"]["size"].upper()]

    @property
    def page_width(self):
        return self.page_size[0]

    @property
    def page_height(self):
        return self.page_size[1]

    @property
    def title_font_name(self):
        return self["Heading1"].fontName

    @property
    def author_font_name(self):
        return self["Heading3"].fontName

    @property
    def text_color(self):
        """primary text color"""
        return self.style["Normal"].textColor

    def register_fonts(self):
        """load additional fonts"""
        def register_font(font_name, file_name):
            """load font from resources and register"""
            with open_binary("dkit.resources", file_name) as infile:
                pdfmetrics.registerFont(TTFont(font_name, infile))

        register_font("SourceSansPro", "SourceSansPro-Regular.ttf")
        register_font("SourceSansPro-Bold", "SourceSansPro-Bold.ttf")
        register_font("SourceSansPro-Italic", "SourceSansPro-Italic.ttf")
        register_font("SourceSansPro-Ital", "SourceSansPro-Italic.ttf")
        register_font("SourceSansPro-BoldItalic", "SourceSansPro-BoldItalic.ttf")
        pdfmetrics.registerFontFamily(
            "SourceSansPro", "SourceSansPro", "SourceSansPro-Bold",
            "SourceSansPro-Ital", "SourceSansPro-BoldItalic"
        )

    def __print_style(self, style):
        """helper to print style info"""
        for k, v in sorted(style.__dict__.items(), key=lambda x: x[0]):
            print(k, v)

    def update_styles(self):

        # Create Verbatim style
        self.style.byName['Verbatim'] = ParagraphStyle(
            'Verbatim',
            parent=self.style['Normal'],
            firstLineIndent=20,
            leftIndent=20,
            fontName="Times-Roman",
            fontSize=8,
            leading=8,
            spaceAfter=5,
            spaceBefore=5,
        )
        # self.__print_style(self.style.byName["Verbatim"])

        # BlockQuote
        self.style.byName['BlockQuote'] = ParagraphStyle(
            'BlockQuote',
            parent=self.style['Normal'],
            firstLineIndent=10,
            leftIndent=10,
        )

        # Update Code style
        code = self.style.byName["Code"]
        code.spaceBefore = 5
        code.spaceAfter = 5
        code.leftIndent = 10

        # Bodytext
        bt = self.style.byName["BodyText"]
        bt.spaceBefore = 5
        bt.spaceAfter = 5

        # Update List styles
        for style in ["OrderedList", "UnorderedList"]:
            ol = self.style.byName[style]
            ol.spaceBefore = 0
            ol.spaceAfter = 0
            ol.leftIndent = 10
            ol.bulletFontSize = self.style["BodyText"].fontSize
            ol.bulletColor = self.style["BodyText"].textColor

        # Update style / provided local stylesheet
        for style, updates in self.local_style["reportlab"]["styles"].items():
            this = self.style.byName[style]
            for k, v in updates.items():
                if "Color" in k:
                    setattr(this, k, colors.HexColor(v))
                elif k == "fontSize":
                    setattr(this, k, fontsize_map[v])
                else:
                    setattr(this, k,  v)

        # Update List styles
        for style in ["OrderedList", "UnorderedList"]:
            ol = self.style.byName[style]
            ol.spaceBefore = 0
            ol.spaceAfter = 0
            ol.leftIndent = 10
            ol.bulletFontSize = self.style["BodyText"].fontSize
            ol.bulletColor = self.style["BodyText"].textColor
            # self.__print_style(self.style.byName[style])

    @property
    def contact_email(self):
        rv = self.doc.contact if self.doc.contact else ""
        if self.doc.email:
            if self.doc.contact:
                rv += f" / {self.doc.email}"
            else:
                rv = str(self.doc.email)
        return rv

    def first_page(self, canvas: Canvas, style_sheet):
        """default function for first pages"""
        class FirstPageConf(BaseModel):
            package: str
            image: str
            text_color: str
            title_color: str
            title_xy: tuple[int, int]
            title_font_size: int
            subtitle_xy: tuple[int, int]
            subtitle_font_size: int
            author_xy: tuple[int, int]
            author_font_size: int
            contact_xy: tuple[int, int]
            contact_font_size: int
            date_font_size: int
            date_xy: tuple[int, int]

        canvas.saveState()
        # canvas.setFont('Times-Bold', 16)
        conf = FirstPageConf(**self.local_style["reportlab"]["front_page"])

        # image
        with open_binary(conf.package, conf.image) as infile:
            pdf = PdfImage(infile, self.page_width, self.page_height)
            pdf.drawOn(canvas, 0, 0)

        # color
        canvas.setFillColor(conf.title_color)

        # title
        x, y = conf.title_xy
        canvas.setFont(self.title_font_name, conf.title_font_size)
        canvas.drawString(x, y, self.doc.title)

        # main color
        canvas.setFillColor(conf.text_color)

        # subtitle
        x, y = conf.subtitle_xy
        canvas.setFont(self.title_font_name, conf.subtitle_font_size)
        canvas.drawString(x, y, self.doc.sub_title)

        # author
        x, y = conf.author_xy
        canvas.setFont(self.author_font_name, conf.author_font_size)
        canvas.drawString(x, y, self.doc.author)

        # email
        x, y = conf.contact_xy
        canvas.setFont(self.author_font_name, conf.contact_font_size)
        canvas.drawString(x, y, self.doc.contact)

        # date
        x, y = conf.date_xy
        canvas.setFont(self.author_font_name, conf.date_font_size)
        canvas.drawString(x, y,  self.title_date)
        canvas.restoreState()

    def later_pages(self, canvas: Canvas, style_sheet):
        class LaterPage(BaseModel):
            top_line: bool
            bottom_line: bool
            add_title: bool = True
            add_sub_title: bool = True
            add_date: bool = True

        conf = LaterPage(**self.local_style["reportlab"]["later_pages"])
        canvas.saveState()
        ty = self.page_height - self.top_margin
        tl = self.left_margin
        tr = self.page_width - self.right_margin
        by = self.bottom_margin

        # lines
        canvas.setStrokeColor(self.text_color)
        canvas.setFillColor(self.text_color)
        canvas.setLineWidth(0.1)
        if conf.top_line:
            canvas.line(tl, ty, tr, ty)
        if conf.bottom_line:
            canvas.line(tl, by, tr, by)   # bottom line

        # title
        if conf.add_title:
            canvas.setFont(self.title_font_name, 8)
            canvas.drawString(tl, ty + 12, self.doc.title)

        # subtitle
        if conf.add_sub_title:
            canvas.setFont(self.author_font_name, 8)
            canvas.drawString(tl, ty + 2, self.doc.sub_title)

        # date
        if conf.add_date:
            canvas.setFont(self.author_font_name, 8)
            tw = stringWidth(self.title_date, self.author_font_name, 8)
            canvas.drawString(tr - tw, ty + 6, self.title_date)

        # author
        canvas.drawString(tl, by - 10, self.doc.author)
        tw = stringWidth(self.title_date, self.author_font_name, 8)

        # page number
        n = canvas.getPageNumber()
        page_num = str(f"Page: {n}")
        tw = stringWidth(page_num, self.author_font_name, 8)
        canvas.drawString(tr - tw, by - 10, page_num)

        canvas.restoreState()
