#
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

# =========== =============== =================================================
# 16 Feb 2015 Cobus Nel       initial version
# 26 Apr 2018 Cobus Nel       updated for iterators
# 29 Oct 2018 Cobus Nel       updated with support for TDigest to calculate
#                             quantiles
# =========== =============== =================================================

"""
Statistical utilities

"""
import sys
import cython
from dkit.algorithms import tdigest
import math
from boltons.statsutils import Stats
from decimal import Decimal
from ..utilities.cmd_helper import LazyLoad

numpy = LazyLoad("numpy")


def quantile_bins(values, n_quantiles=10, strict=False):
    """compute n quantile bins

    args:
        * values: iterator of numeric values
        * n_quantiles: how many bins
        * strict: generate ValueError if too many similar values for bins

    returns:
        list of values: [(left, right, count), ...]

    """
    stats = Stats(values)
    step = Decimal(1)/Decimal(n_quantiles)
    q_list = []
    q = step
    last = None
    for i in range(n_quantiles):
        this = stats.get_quantile(q)
        if this == last:
            if strict:
                raise ValueError("Too many similar value for bins")
            else:
                if q_list[-1][1] == this:
                    prev = q_list.pop()
                    last = prev[0]
        else:
            q_list.append((last, this, q))
            last = this
        q += step
    q_list[-1] = (q_list[-1][0], None, q_list[-1][2])
    return q_list


class AbstractAccumulator(object):
    """base class for accumulators"""

    def as_map(self):
        """
        statistics as dictionary

        The following keys:
            * observations
            * min
            * max
            * mean
            * median
            * stdev
            * variance
            * iq

        """
        _attrs = ["observations", "min", "max", "mean", "median", "stdev",
                  "variance", "iqr"]
        return {k: getattr(self, k) for k in _attrs}

    def consume(self, values):
        """
        consume an iterable

        Example usage as below:

        >>> a = Accumulator()
        >>> a.consume([i for i in range(10)])
        >>> print(a.stdev)
        3.02765

        """
        for value in values:
            self.push(value)

    def __call__(self, values):
        """
        consume values in iterable and yield back
        """
        for value in values:
            self.push(value)
            yield value

    def __str__(self):
        """
        String values of information including observations, min, max, mean
        std deviation and variance.

        :returns: str
        """
        s = ""
        s += f"Observations:       {self.observations:d}\n"
        s += f"Minimum:            {self.min:f}\n"
        s += f"Maxmimum:           {self.max:f}\n"
        s += f"Mean:               {self.mean:f}\n"
        s += f"Median:             {self.median:f}\n"
        s += f"Standard deviation: {self.stdev:f}\n"
        s += f"Variance:           {self.variance:f}\n"
        s += f"IQR:                {self.iqr:f}\n"
        return s


class BufferAccumulator(AbstractAccumulator):

    def __init__(self, values=None, precision: int = 5):
        self.buffer_ = values if values else []
        self.precision = precision

    @property
    def mean(self):
        """
        sample mean
        """
        return round(numpy.mean(self.buffer_), self.precision)

    def quantile(self, q):
        """
        quantile at value
        """
        return round(
            numpy.quantile(self.buffer_, q),
            self.precision
        )

    @property
    def iqr(self):
        """inter-quartile range"""
        return round(
            self.quantile(0.75) - self.quantile(0.25),
            self.precision
        )

    @property
    def max(self):
        """
        maximum value
        """
        return max(self.buffer_)

    @property
    def median(self):
        """estimated median value"""
        return self.quantile(0.5)

    @property
    def min(self):
        """
        minimum value
        """
        return min(self.buffer_)

    @property
    def observations(self):
        """
        number of observations
        """
        return len(self.buffer_)

    @property
    def sum(self):
        """sum of values"""
        return sum(self.buffer_)

    @property
    def stdev(self):
        """
        sample standard deviation
        """
        return round(
            numpy.std(self.buffer_),
            self.precision
        )

    @property
    def variance(self):
        """
        sample variance
        """
        return round(
            numpy.var(self.buffer_),
            self.precision
        )

    def push(self, value):
        """
        Feed a value to the Collector.

        :param value: add value added to counters.
        :type value: float/int
        """
        self.buffer_.append(value)

    def merge(self, other):
        self.buffer.extend(other)
        return self


class Accumulator(AbstractAccumulator):
    """
    Statistics collector.

    This class will  maintain statistics about the data
    fed to it.

    In addtion the date can be collected and consumed again
    by using the __call__ function:

    >>> a = Accumulator()
    >>> s = a([i for i in range(10)])
    >>> print(sum(s))
    45
    >>> print(a.stdev)
    3.02765

    The information can be printed to the console:

    >>> a = Accumulator()
    >>> a.consume([i for i in range(10)])
    >>> print(a)
    Observations:       10
    Minimum:            0.000000
    Maxmimum:           9.000000
    Mean:               4.500000
    Median:             4.500000
    Standard deviation: 3.027650
    Variance:           9.166670
    IQR:                5.000000
    <BLANKLINE>

    Refer to additional examples, below

    """
    def __init__(self, values=[], precision: int = 5):
        """
        Constructor
        """
        self.precision: int = precision
        self._min: float = sys.float_info.max
        self._max: float = -sys.float_info.max
        self._observations: cython.long = 0
        self._mean: float = None
        self._std: float = None
        self._tdigest = tdigest.TDigest()
        self.consume(values)

    def __add__(self, o):
        """merge two instances"""
        a1 = self.from_dict(self.as_dict())

        n1 = self.observations
        n2 = o.observations

        if n1 == 0 and n2 == 0:
            return a1
        if n1 == 0:
            return o.from_dict(o.as_dict())
        if n2 == 0:
            return a1

        a1._mean = (self._observations * self._mean + o._observations * o.mean) / \
            (n1 + n2)
        a1._std = math.sqrt((((n1-1)*(a1._std ** 2)) + ((n2-1)*(o._std ** 2)))/(n1+n2-2))
        a1._min = min(self._min, o._min)
        a1._max = max(self._max, o._max)
        a1._observations = n1 + n2
        a1._tdigest.merge(o._tdigest)
        return a1

    def as_dict(self):
        """dict representation for serialisation

        the t_digest cannot be pickled
        """
        rv = dict(self.__dict__)
        rv["digest"] = rv.pop("_tdigest").as_dict()
        return rv

    @classmethod
    def from_dict(cls, data):
        rv = cls(precision=data["precision"])
        rv._min = data["_min"]
        rv._max = data["_max"]
        rv._observations = data["_observations"]
        rv._mean = data["_mean"]
        rv._std = data["_std"]
        rv._tdigest = tdigest.TDigest.from_dict(data["digest"])
        return rv

    @property
    def mean(self):
        """
        sample mean
        """
        if self._observations > 0:
            return round(self._mean, self.precision)
        else:
            return 0.0

    def quantile(self, value):
        """
        quantile at value
        """
        return round(
            self._tdigest.quantile(value),
            self.precision
        )

    @property
    def iqr(self):
        """inter-quartile range"""
        return round(
            self._tdigest.quantile(0.75) - self._tdigest.quantile(0.25),
            self.precision
        )

    @property
    def max(self):
        """
        maximum value
        """
        return self._max

    @property
    def median(self):
        """estimated median value"""
        return self._tdigest.quantile(0.5)

    @property
    def min(self):
        """
        minimum value
        """
        return self._min

    @property
    def observations(self):
        """
        number of observations
        """
        return self._observations

    @property
    def sum(self):
        """sum of values"""
        return round(self._mean * self.observations, self.precision)

    @property
    def stdev(self):
        """
        sample standard deviation
        """
        return round(math.sqrt(self.variance), self.precision)

    @property
    def variance(self):
        """
        sample variance
        """
        if self._observations > 1:
            return round(self._std / (self._observations - 1), self.precision)
        else:
            return 0

    def push(self, value, strict=False):
        """
        Feed a value to the Collector.

        Args:
            - value: add value added to counters
            - strict: ignore None values if not strict

        Refer to:
            * https://www.johndcook.com/blog/standard_deviation/
            * Donald M Knuth, The art of Computer Programming Vol II, 3rd Ed,  P232
        """
        try:
            _value = float(value)
        except TypeError as e:
            if value is None:
                return
            else:
                raise e
        if _value < self._min:
            self._min = _value
        if _value > self._max:
            self._max = _value
        self._observations += 1

        # Variance
        if self._mean is not None:
            new_mean = self._mean + (_value-self._mean) / float(self._observations)
            self._std = self._std + (_value-self._mean)*(_value-new_mean)
            self._mean = new_mean
        else:
            self._mean = _value
            self._std = 0.0
        self._tdigest.insert(_value)
