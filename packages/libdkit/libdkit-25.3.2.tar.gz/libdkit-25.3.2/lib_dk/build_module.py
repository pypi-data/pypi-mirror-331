# Copyright (c) 2017 Cobus Nel
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
Execute ETL jobs
"""
from . import module, options
from dkit.etl.model import DOC_SECTION


def value_by_priority(*values, default=None):
    """get a value from prioritised choices

    a choice will be skipped if the value is None
    """
    for value in values:
        if value is not None:
            return value
    return default


class BuildModule(module.MultiCommandModule):

    @property
    def doc_author(self):
        """Author as per priority for choices"""
        return value_by_priority(
            self.args.author,
            self.config.get(DOC_SECTION, "author", fallback=None),
            default="Author Name"
        )

    @property
    def doc_email(self):
        """Author as per priority for choices"""
        return value_by_priority(
            self.args.email,
            self.config.get(DOC_SECTION, "email", fallback=None),
            default=""
        )

    @property
    def doc_contact(self):
        """Author as per priority for choices"""
        return value_by_priority(
            self.args.contact,
            self.config.get(DOC_SECTION, "contact", fallback=None),
            default=""
        )

    def do_template(self):
        """
        apply data sets specified to jinja2 template
        """
        self.args.output.write(
            self.services.render_template(
                self.args.template,
                self.args.data_dict
            )
        )

    def do_doc(self):
        """create pdf document from markdown file(s)"""
        from dkit.doc import builder
        b = builder.SimpleDocRenderer(
            author=self.doc_author,
            title=self.args.title,
            sub_title=self.args.sub_title,
            email=self.doc_email,
            contact=self.doc_contact
        )
        b.build_from_files(
            self.args.output,
            *self.args.files
        )

    def do_report(self):
        """run report"""
        from dkit.doc import builder
        b = builder.ReportBuilder.from_file(self.args.report)
        b.run()

    def init_parser(self):
        """initialize argparse parser"""
        self.init_sub_parser()

        # doc
        parser_doc = self.sub_parser.add_parser("doc", help=self.do_doc.__doc__)
        options.add_option_defaults(parser_doc)
        parser_doc.add_argument("-o", "--output", help="pdf output filename", required=True)
        parser_doc.add_argument("-t", "--title", required=True, help="title")
        parser_doc.add_argument("-s", "--sub-title", dest="sub_title", help="title",
                                default="")
        parser_doc.add_argument("-a", "--author", default=None, help="author")
        parser_doc.add_argument("-e", "--email", help="email", default=None)
        parser_doc.add_argument("-c", "--contact", help="contact", default=None)

        parser_doc.add_argument("files", nargs="+")

        # report
        parser_report = self.sub_parser.add_parser("report", help=self.do_report.__doc__)
        options.add_option_model(parser_report)
        parser_report.add_argument(
            "-r", "--report", required=True, help="report.yml file"
        )
        options.add_option_logging(parser_report)

        # template
        parser_template = self.sub_parser.add_parser("template", help=self.do_template.__doc__)
        options.add_option_model(parser_template)
        options.add_options_extension(parser_template)
        options.add_option_kw_data(parser_template)
        options.add_option_template(parser_template)
        options.add_option_output_uri(parser_template)

        super().parse_args()
