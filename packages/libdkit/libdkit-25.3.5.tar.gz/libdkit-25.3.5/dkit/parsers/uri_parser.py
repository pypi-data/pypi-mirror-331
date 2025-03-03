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

import re
from urllib.parse import urlparse, parse_qs

from .. import messages
from ..exceptions import DKitParseException


COMPRESSION_FORMATS = ['bz2', 'zip', 'gz', 'xz', 'lz4']
ENCRYPTION_FORMATS = ['aes']
RE_COMRESSION_FORMATS = "|".join(COMPRESSION_FORMATS)
RE_ENCRYPTION_FORMATS = "|".join(ENCRYPTION_FORMATS)
FILE_DIALECTS = [
    'csv', 'jsonl', 'json', 'tsv', 'xlsx', 'xls', 'xml', 'bxr',
    'pkl', 'mpak', 'pke', 'avro', 'parquet'
]
SHARED_MEMORY_DIALECTS = ["shm"]
FILE_SQL_DIALECTS = ["sqlite", "duckdb"]
FILE_DB_DIALECTS = ["hdf5"] + FILE_SQL_DIALECTS


"""
SQL_DRIVERS = {
    # "sybase": "sqlalchemy_sqlany",
    # "firebird": "firebird+fdb",
    "hdf5": "hdf5",
    "impala": "impala",
    "mssql": "mssql+pymssql",
    "mysql+mysqldb": "mysql+mysqldb",
    "oracle": "oracle+cx_oracle",
    "postgresql": "postgresql",
    "sqlite": "sqlite",
    "awsathena+rest": "awsathena+rest",
    "duckdb": "duckdb",
    "mssql+pyodbc": "mssql+pyodbc",
}
NETWORK_DIALECTS = list(SQL_DRIVERS.keys())
"""
NETWORK_DIALECTS = [
    "hdf5", "impala", "mssql", "mysql+mysqldb", "oracle+cx_oracle",
    "postgresql", "sqlite", "awsathena+rest", "duckdb", "mssql+pyodbc"
]


class URIStruct:
    """
    Helper class that ensure parsed dictionary contains the correct
    fields.
    """
    def __init__(self, driver=None, dialect=None, database=None,
                 username=None, password=None, host=None, port=None,
                 compression=None, parameters=None, entity=None):
        # encryption=None:
        self.dialect = dialect
        self.driver = driver
        self.database = database
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.compression = compression
        self.parameters = parameters
        self.entity = entity

    @classmethod
    def from_uri(cls, uri):
        """parse from uri"""
        return cls(**parse(uri))

    def as_dict(self):
        """return as dict"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("__")}

    def __str__(self):
        """string representation"""
        return str(self.as_dict())

    def __eq__(self, other):
        """equality test"""
        return self.__dict__ == other.__dict__


def parse(uri):
    """
    parse uri into dictionary.

    Arguments:
        uri: uri string (e.g 'jsonl://filename.db')

    Returns:
        dictionary (see URIStruct)

    Raises
       `dkit.exceptions.CkitParseException`
    """
    if ":///" in uri:
        # this is a file based driver
        retval = _parse_file_driver(uri)
    elif "//" in uri:
        # this is a network based database
        retval = _parse_network_db(uri)
    else:
        # this is a file
        retval = _parse_file_name(uri)
    if retval is not None:
        return retval
    else:
        raise DKitParseException(
            messages.MSG_0012.format(uri)
        )


def _parse_file_driver(uri: str):
    """parse file with specified driver"""
    rx = r"({}):\/\/\/(.+)$".format("|".join(
        FILE_DIALECTS + FILE_DB_DIALECTS + SHARED_MEMORY_DIALECTS
    ))
    m = re.match(rx, uri)
    if m is not None:
        dialect = m.group(1)
        if dialect in FILE_DB_DIALECTS:
            # Its a database
            endpoint = _parse_file_db_endpoint(m.group(2))
            if endpoint is not None:
                if dialect in FILE_SQL_DIALECTS:
                    endpoint["driver"] = "sql"
                else:
                    endpoint["driver"] = dialect
                endpoint["dialect"] = dialect
                return URIStruct(**endpoint).as_dict()
            else:
                return None
        elif dialect in SHARED_MEMORY_DIALECTS:
            # It is a shared memory file
            return URIStruct(
                database=f"/{m.group(2)}",
                dialect=_parse_dialect_from_filename(m.group(2)),
                driver="shm",
                compression=_parse_compression_from_filename(m.group(2)),
                # encryption=_parse_encryption_from_filename(m.group(2))
            ).as_dict()
        elif dialect in FILE_DIALECTS:
            return URIStruct(
                database=m.group(2),
                dialect=m.group(1),
                driver="file",
                compression=_parse_compression_from_filename(m.group(2)),
                # encryption=_parse_encryption_from_filename(m.group(2))
            ).as_dict()
        else:
            raise DKitParseException(messages.MSG_0014.format(dialect))
    else:
        return None


def _parse_file_db_endpoint(host_string):
    """parse host details including port etc."""
    # user:password@hostname:port/database::entity[filter]
    rx = (
        r"(?P<database>[a-zA-Z0-9_./:]+)"                 # file
        r"(?:\#(?P<entity>[a-zA-Z0-9/_-]+))?"             # entity
        # r"(?:#\[(?P<filter>.+)\])?)?"                  # filter
        r"$"                                             # end of rx
    )
    m = re.match(rx, host_string)
    if m is not None:
        return m.groupdict()
    else:
        return None


def _parse_uri_parameters(inner_text):
    """parse uri parameters"""
    if not inner_text:
        return None
    rv = {}
    inner = r"(\?|\&)([^=]+)\=([^&]+)"
    for i in re.findall(inner, inner_text):
        rv[i[1]] = i[2]
    return rv


def _parse_netloc(netloc):
    """used by _parse_network_db to parse the network location"""
    ur = r"[A-Za-z0-9_-]"
    # _pr = r"[A-Za-z0-9!@#$%^&*()_+-=[]{}'\"\\|,.<>/?]"
    pr = r"[^@:]"
    hn = r"[A-Za-z0-9_\-.]"
    pattern = fr'(?P<un>{ur}+)?:?(?P<pw>{pr}+)?@(?P<h>{hn}+):?(?P<p>\d+)?'
    match = re.match(pattern, netloc)

    return {
        "username": match.group('un'),
        "password": match.group('pw'),
        "host": match.group('h'),
        "port": match.group('p'),
    }


def _parse_network_db(host_string):
    """
        driver
        username=None
        password=None
        host=None
        port=None,
        database=None
        parameters=None
    """
    result = urlparse(host_string)
    params = parse_qs(result.query)

    if result.scheme not in NETWORK_DIALECTS:
        raise DKitParseException(
            f"invalid dialect: {result.scheme}"
        )
    database = result.path[1:] if result.path else None

    rv = {
        "driver": "sql",
        "dialect": result.scheme,
        "database": database,
        "parameters": {k: v[0] for k, v in params.items()}
    }
    rv.update(_parse_netloc(result.netloc))
    return rv


def _parse_file_name(uri):
    """parse filename to uri"""
    return URIStruct(
        database=uri,
        compression=_parse_compression_from_filename(uri),
        # encryption=_parse_encryption_from_filename(uri),
        driver="file",
        dialect=_parse_dialect_from_filename(uri)
    ).as_dict()


def _parse_dialect_from_filename(file_name):
    """
    determine encoding from filename
    """
    p = re.compile(r".+\.({})(?:\..+$)?".format("|".join(FILE_DIALECTS)))
    r = p.search(file_name)
    if r is None:
        raise DKitParseException(messages.MSG_0013.format(file_name))
    else:
        return r.group(1)


def _parse_compression_from_filename(file_name):
    """
    determine compression from filename
    """
    p = re.compile(r".+\.({})(?:\..+$)*$".format(RE_COMRESSION_FORMATS))
    r = p.search(file_name)
    if r is None:
        return None
    else:
        return r.group(1)


# def _parse_encryption_from_filename(file_name):
#    """
#    determine encryption from filename
#    """
#    p = re.compile(r".+\.({})$".format(RE_ENCRYPTION_FORMATS))
#    r = p.search(file_name)
#    if r is None:
#        return None
#    else:
#        return r.group(1)
