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
import argparse
import json

from . import module, options
from dkit import exceptions
from dkit.data import manipulate as mp, containers, aggregation as agg
from dkit.etl.extensions import ext_sql_alchemy
from dkit.etl.extensions.ext_sql_alchemy import SQLAlchemyTemplateSource
from dkit.parsers.parameter_parser import parameter_dict
from dkit.utilities.cmd_helper import build_kw_dict
from dkit.utilities.jinja2 import render_strict, find_variables
from dkit.data.json_utils import make_simple_encoder


class GroupByAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if hasattr(namespace, "group_by_operations"):
            operations = getattr(namespace, "group_by_operations")
        else:
            operations = []
            setattr(namespace, "group_by_operations", operations)
        aggregator_class = agg.MAP_NON_PARAMETRIC_FUNCTIONS[self.dest]
        if ":" in values:
            v = values.split(":")
            aggregator = aggregator_class(v[0])
            aggregator.alias(v[1])
        else:
            aggregator = aggregator_class(values)
        operations.append(aggregator)


class PivotFunctionAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        # Set function
        setattr(
            namespace,
            "function", mp.PIVOT_FUNCTIONS[self.dest]
        )

        # Set aggregation field
        setattr(
            namespace,
            "value_field",
            values
        )


class RunModule(module.MultiCommandModule):

    def do_agg(self):
        """group-by with aggregation"""

        def get_aggregator():
            """build dkit.data.aggregator.Aggregate object from options"""
            aggregator = agg.Aggregate()

            # Check that at least one operation has been specified
            if not hasattr(self.args, "group_by_operations"):
                raise exceptions.DKitApplicationException("No group by operation specified")

            # set group by keys
            aggregator = aggregator + agg.GroupBy(*self.args.group_by)

            for operation in self.args.group_by_operations:
                aggregator = aggregator + operation

            return aggregator

        aggr = get_aggregator()
        field_list = aggr.groupby_keys + [i.target for i in aggr.aggregations]
        self.args.fields = field_list
        if self.args.table is True:
            a = list(aggr(self.input_stream(
                    self.args.input, fields=aggr.required_fields)
                ))
            self.tabulate(a)
        else:
            self.push_to_uri(
                self.args.output,
                aggr(self.input_stream(
                    self.args.input,
                    fields=aggr.required_fields
                ))
            )

    def do_etl(self):
        """run etl process"""
        self.push_to_uri(
            self.args.output,
            self.input_stream(self.args.input)
        )

    def do_exec(self):
        """execute driver level query"""
        srv = self.load_services(ext_sql_alchemy.SQLServices)

        # Get source connection
        if self.args.connection is None:
            raise exceptions.DKitApplicationException("Connection required")

        # get SQL query
        if self.args.query is not None:
            str_query = srv.model.queries[self.args.query]()
        elif self.args.query_file is not None:
            with open(self.args.query_file, "r") as infile:
                str_query = infile.read()
        else:
            str_query = self.args.query_string
        accessor = srv.get_sql_accessor(self.args.connection)
        json = make_simple_encoder()
        for result in accessor.execute(str_query):
            self.print(json.dumps(result))

    def do_query(self):
        """execute SQL query"""
        from dkit.etl import model
        srv = self.load_services(ext_sql_alchemy.SQLServices)

        # Get source connection
        if self.args.connection is not None:
            connection = srv.model.get_connection(self.args.connection)
        elif self.args.database_uri is not None and len(self.args.database_uri) > 0:
            connection = model.Connection.from_uri(self.args.database_uri)
        else:
            raise exceptions.DKitApplicationException("Connection or Input URI required")

        # get SQL query
        if self.args.query is not None:
            str_query = srv.model.queries[self.args.query]()
        elif self.args.query_file is not None:
            with open(self.args.query_file, "r") as infile:
                str_query = infile.read()
        else:
            str_query = self.args.query_string

        # variables
        variables = parameter_dict(self.args.parameter)

        # show only
        if self.args.show_sql:
            s = SQLAlchemyTemplateSource(None, str_query, variables)
            self.print(s.get_rendered_sql())
            return

        if self.args.show_params:
            s = SQLAlchemyTemplateSource(None, str_query, variables)
            for param in s.discover_parameters():
                self.print(param)
            return

        if self.args.table:
            # only retrieve first 100 rows
            data = []
            i = srv.run_template_query(
                    connection,
                    str_query,
                    variables=variables
                )
            for i, row in enumerate(i):
                data.append(row)
                if i > 100:
                    break
            self.tabulate(data)
        else:
            self.push_to_uri(
                self.args.output,
                srv.run_template_query(
                    connection,
                    str_query,
                    variables=variables
                )
            )

    def do_template(self):
        """
        apply data sets specified to jinja2 template
        """
        with open(self.args.template, "rt") as infile:
            template = infile.read()

        # print undeclared variables and exit
        if self.args.list_variables:
            var_map = {
                k: f'__{k}__' for k in find_variables(template)
            }
            self.print(json.dumps(var_map, indent=2))
            return

        # read variables
        if self.args.json:
            data_dict = json.loads(self.args.json.read())
        else:
            data_dict = build_kw_dict(*self.args.data_dict)

        self.args.output.write(
            # self.services.render_template(
            #     self.args.template,
            #    data_dict
            # )
            render_strict(
                template,
                **data_dict
            )
        )

    def do_join(self):
        """
        join two datasets
        """
        left = self.input_stream([self.args.left])
        right = self.input_stream([self.args.right])

        if self.args.backend:
            backend = containers.FlexShelve(self.args.backend)
        else:
            backend = None

        m = mp.merge(
            left,
            right,
            self.args.const_cols,
            self.args.ref_cols,
            self.args.all_left,
            backend=backend
        )
        self.push_to_uri(self.args.output, m)

        if backend is not None:
            backend.close()

    def do_melt(self):
        """transpose a pivot table back to key:value pairs"""
        self.push_to_uri(
            self.args.output,
            mp.melt(
                self.input_stream(self.args.input),
                self.args.id_fields,
                self.args.variable_name,
                self.args.value_name
            )
        )

    def do_pivot(self):
        """create pivot"""
        p = mp.Pivot(
            self.input_stream(self.args.input),
            self.args.group_by,
            self.args.pivot,
            self.args.value_field,
            self.args.function,
        )
        if self.args.table:
            self.tabulate(list(p))
        else:
            self.push_to_uri(
                self.args.output,
                p
            )

    def do_report(self):
        """run report"""
        from dkit.doc import builder
        b = builder.ReportBuilder.from_file(self.args.report)
        b.run()

    def init_parser(self):
        """initialize argparse parser"""
        self.init_sub_parser()

        # agg
        parser_agg = self.sub_parser.add_parser("agg", help=self.do_agg.__doc__)
        options.add_option_defaults(parser_agg)
        options.add_options_inputs(parser_agg)
        options.add_option_output_uri(parser_agg)
        parser_agg.add_argument("-g", "--group_by", dest="group_by", action="append",
                                default=[], help="add group_by field")
        for name, class_obj in agg.MAP_NON_PARAMETRIC_FUNCTIONS.items():
            parser_agg.add_argument(
                f"--{name}",
                dest=name,
                action=GroupByAction
            )
        options.add_option_tabulate(parser_agg)

        # etl
        parser_etl = self.sub_parser.add_parser("etl", help=self.do_etl.__doc__)
        options.add_option_defaults(parser_etl)
        options.add_options_inputs(parser_etl)
        options.add_option_n(parser_etl)
        options.add_option_output_uri(parser_etl)

        # join
        parser_join = self.sub_parser.add_parser("join", help=self.do_join.__doc__)
        options.add_option_defaults(parser_join)
        options.add_options_extension(parser_join)
        options.add_option_backend_map(parser_join)
        options.add_options_join(parser_join)
        options.add_option_output_uri(parser_join)

        # melt
        parser_melt = self.sub_parser.add_parser("melt", help=self.do_melt.__doc__)
        options.add_option_defaults(parser_melt)
        options.add_options_inputs(parser_melt)
        options.add_option_n(parser_melt)
        options.add_option_output_uri(parser_melt)
        parser_melt.add_argument(
            "-i", "--id_field", dest="id_fields", action="append",
            default=[], help="add identifier field"
        )
        parser_melt.add_argument(
            "-K", "--var", dest="variable_name", default="variable",
            help="name of variable field (default is 'variable')"
        )
        parser_melt.add_argument(
            "-V", "--val", dest="value_name", default="value",
            help="name of value field (default is 'value')"
        )

        # pivot
        parser_pivot = self.sub_parser.add_parser("pivot", help=self.do_pivot.__doc__)
        options.add_option_defaults(parser_pivot)
        options.add_options_inputs(parser_pivot)
        options.add_option_output_uri(parser_pivot)
        parser_pivot.add_argument("-g", "--group_by", dest="group_by", action="append",
                                  default=[], help="add group_by field")
        parser_pivot.add_argument("-p", "--pivot", required=True, help="pivot field")
        for name, class_obj in mp.PIVOT_FUNCTIONS.items():
            parser_pivot.add_argument(
                f"--{name}",
                dest=name,
                action=PivotFunctionAction
            )
        options.add_option_tabulate(parser_pivot)

        # execute
        parser_execute = self.sub_parser.add_parser(
            "exec", help=self.do_exec.__doc__
        )
        group_io = parser_execute.add_argument_group("connection")
        options.add_option_connection_name_opt(parser_execute)
        options.add_option_defaults(parser_execute)
        group_query = parser_execute.add_argument_group("sql source")
        options.add_query_group(group_query)

        # query
        parser_query = self.sub_parser.add_parser("query", help=self.do_query.__doc__)
        group_io = parser_query.add_argument_group("connection")
        options.add_option_connection_name_opt(group_io)
        options.add_option_input_db_uri_optional(group_io)
        options.add_option_defaults(parser_query)
        group_query = parser_query.add_argument_group("sql source")
        options.add_query_group(group_query)
        options.add_option_output_uri(parser_query)
        options.add_option_tabulate(parser_query)
        parser_query.add_argument(
            '-p', '-param', action='append', dest='parameter',
            default=[],
            help='define query parameters (can be added multiple times)'
        )
        parser_query.add_argument(
            "--show-sql", dest="show_sql", action="store_true",
            default=False,
            help="show query without executing"
        )
        parser_query.add_argument(
            "--show-params", dest="show_params", action="store_true",
            default=False,
            help="show parameters in sql statement without executing"
        )

        # report
        parser_report = self.sub_parser.add_parser("report", help=self.do_report.__doc__)
        options.add_option_model(parser_report)
        parser_report.add_argument(
            "-r", "--report", required=True, help="report.yml file"
        )
        options.add_option_logging(parser_report)

        # template
        parser_template = self.sub_parser.add_parser(
            "template", help=self.do_template.__doc__
        )
        # options.add_option_model(parser_template)
        # options.add_options_extension(parser_template)
        options.add_option_kw_data(parser_template)
        options.add_option_template(parser_template)
        parser_template.add_argument(
            "--json", default=None,
            type=argparse.FileType('r'),
            help="read input variables from json file"
        )
        options.add_option_output(parser_template)
        parser_template.add_argument(
            "--list-variables", dest="list_variables", action="store_true",
            default=False,
            help="show variables in template without rendering"
        )

        super().parse_args()
