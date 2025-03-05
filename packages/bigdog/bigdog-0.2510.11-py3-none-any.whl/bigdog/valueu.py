import os
# import sys
import inspect
# import traceback
import numpy as np
import datetime as dt
# import uuid

import astropy.units as u

from .toolclass_version import HeadVer
from .toolclass_pydocument import PyDocument

class ValueU:
    __fullname = 'Value tagged with Uncertainty'
    __lastupdate = dt.datetime.strptime('2025-03-04', '%Y-%m-%d')
    __version = HeadVer(0, __lastupdate, 12)
    __developer = {'name': 'DH.Koh', 'contact': 'donghyeok.koh.code@gmail.com'}
    __collaborators = [{'name': 'JH.Kim', 'contact': None}, {'name': 'KM.Heo', 'contact': None}]
    __contributors = [{'name': None, 'role': None}]
    __callsign = 'Value(+/-)'

    __versiondependency = {}

    __array_priority__ = 11000

    def __init__(self, central=np.nan, stddev=None, limit=None):
        # self.__id = uuid.uuid4()  # time.perf_counter_ns()

        assert stddev == None or limit == None, \
            f'Cannot provide both arguments \"stddev\" and \"limit\" in class {self.__class__}'

        if limit is None:
            limit = np.array([np.nan, np.nan])
        if stddev is None:
            stddev = np.nan

        ### initialize
        self.error_absolute = np.array([np.nan, np.nan])
        self.error_relative = np.array([np.nan, np.nan])

        self._set_central(central)

        ### recognize value
        if not np.all(np.isnan(limit)):
            self._set_error_absolute(limit)
        elif not np.all(np.isnan(stddev)):
            self._set_error_relative(stddev)

        self.set_digit(digit_round=5, digit_stringformat=8)

        return None

    def _set_central(self, centralvalue=None):
        """
        Protected Method
        Modify 'self.central' to input the central value
        usage :
        $ >>> v = ValueU()
        $ ... print(repr(v))
        $ ValueU(nan, (nan, nan))
        $ >>> v._set_central(10)
        $ ... print(repr(v))
        $ ValueU(10, (nan, nan))
        """
        if centralvalue is None:
            self.central = np.nan
        else:
            self.central = centralvalue

        # self.__baseshape = np.array(self.central).shape
        self._sync_from_absolute()

        return self

    def _sync_from_absolute(self):
        """
        Protected Method
        modify 'self.error_relative' based on 'self.error_absolute', for synchronization between instance variables
        usage of synchronize between self.error_relative and self.error_absolute
        """
        self.error_relative = self.error_absolute - self.central

        return self

    def _sync_from_relative(self):
        """
        Protected Method
        modify 'self.error_absolute' based on 'self.error_relative', for synchronization between instance variables
        usage of synchronize between 'self.error_absolute' and 'self.error_relative'
        """
        self.error_absolute = self.central + self.error_relative

        return self

    def __set_error_absolute(self, limits: np.ndarray):
        """
        Private Method
        replace the instance variable 'self.error_absolute' with the input parameter.
        available standard format of input variable must be: [-number, +number]
        """
        limits_isint = np.array([limits[0].is_integer(), limits[-1].is_integer()])

        if isinstance(self.central, int):
            if np.all(limits_isint):
                self.error_absolute = np.array(limits)
            else:
                self.error_absolute = np.array([float(limits[0]), float(limits[1])])
        else:
            if np.any(limits_isint):
                self._set_central(float(self.central))
                self.error_absolute = np.array([float(limits[0]), float(limits[1])])
            else:
                self.error_absolute = np.array(limits)

        return self

    def _set_error_absolute(self, limit: np.ndarray):
        """
        Protected Method
        categorize and process the input dispersion range
        impossible to handle an input variable that is not structured as a shape twice the size of the central value
        impossible to handle an input variable that cannot be processed as a numpy ndarray object
        transport processed dispersion range to 'self.__set_error_relative'
        usage :
        $ >>> v = ValueU(10)
        $ ... print(repr(v))
        $ ValueU(10, (nan, nan))
        $ >>> v._set_error_absolute([8, 11])
        $ ValueU(5, (-2, +1))
        """
        if np.array(limit).shape == (2,):
            ### Case (a) [-number, +number]
            self.__set_error_absolute(limits=np.array(limit))
        elif np.prod(np.array(limit).shape) / np.prod(np.array(self.central).shape) == 2.:
            ### Case (b) [[-number1, +number2, ...], [+number1, +number2, ...]]
            """[Describe] - self.central가 단일 값이 아닐 경우를 위한 부분. 현재는 사용처가 없지만 활용 가능성이 있기 때문에 존치."""
            if not np.array(limit).shape == ((2,) + np.array(self.central).shape):
                raise ValueError(f'Input argument \"limit\" shape not matched with two times repeated shape of the central value')
            self.__set_error_absolute(limits=np.array([np.array(limit)[0], np.array(limit)[1]]))
        else:
            raise IndexError(f'Input argument \"limit\" wrong - should be two times repeated shape of the central value')

        try:
            self._sync_from_absolute()
        except:
            raise

        return self

    def __set_error_relative(self, stddevs: np.ndarray):
        """
        Private Method
        replace the instance variable 'self.error_relative' with the input parameter.
        available standard format of input variable must be: [-number, +number]
        """
        stddevs_isint = np.array([stddevs[0].is_integer(), stddevs[-1].is_integer()])

        if isinstance(self.central, int):
            if np.all(stddevs_isint):
                self.error_relative = np.array(stddevs)
            else:
                self.error_relative = np.array([float(stddevs[0]), float(stddevs[1])])
        else:
            if np.any(stddevs_isint):
                self._set_central(float(self.central))
                self.error_relative = np.array([float(stddevs[0]), float(stddevs[1])])
            else:
                self.error_relative = np.array(stddevs)

        return self

    def _set_error_relative(self, stddev: np.ndarray):
        """
        Protected Method
        categorize and process the input standard deviation
        impossible to handle an input variable that is not structured as a shape twice the size of the central value
        impossible to handle an input variable that cannot be processed as a numpy ndarray object
        transport processed dispersion range to 'self.__set_error_relative'
        usage :
        $ >>> v = ValueU(10)
        $ ... print(repr(v))
        $ ValueU(10, (nan, nan))
        $ >>> v._set_error_relative([-1, 2])
        $ ValueU(5, (-1, +2))
        """
        if np.array(stddev).shape == (2,):
            ### Case (a) [-number, +number]
            self.__set_error_relative(stddevs=np.array(stddev))
        elif np.array(stddev).shape == (1,):
            ### Case (b) [number]
            self.__set_error_relative(stddevs=np.array([-stddev[0], stddev[0]]))
        elif np.array(stddev).shape == ():
            ### Case (c) number
            self.__set_error_relative(stddevs=np.array([-stddev, stddev]))
        elif np.prod(np.array(stddev).shape) / np.prod(np.array(self.central).shape) == 2.:
            ### Case (d) [[-number1, +number2, ...], [+number1, +number2, ...]]
            """[Describe] - self.central가 단일 값이 아닐 경우를 위한 부분. 현재는 사용처가 없지만 활용 가능성이 있기 때문에 존치."""
            if not np.array(stddev).shape == ((2,) + np.array(self.central).shape):
                raise ValueError(f'Input argument \"stddev\" shape not matched with two times repeated shape of the central value')
            self.__set_error_relative(stddevs = np.array([np.array(stddev)[0], np.array(stddev)[1]]))
        elif np.prod(np.array(stddev).shape) / np.prod(np.array(self.central).shape) == 1.:
            ### Case (e) [-number1, +number2, ...]
            """[Describe] - self.central가 단일 값이 아닐 경우를 위한 부분. 현재는 사용처가 없지만 활용 가능성이 있기 때문에 존치."""
            if not np.array(stddev).shape == np.array(self.central).shape:
                raise ValueError(f'Input argument \"stddev\" shape not matched with the central value')
            self.__set_error_relative(stddevs = np.array([-np.array(stddev), np.array(stddev)]))
        else:
            raise IndexError(f'Input argument \"stddev\" wrong - should be two times repeated or exactly same structure of the central value')

        try:
            self._sync_from_relative()
        except:
            raise

        return self

    def errorflip(self):
        copiedobject = self.__class__(central=self.central, limit=np.flip(self.error_absolute))
        copiedobject.set_digit(self._digit_round, self._digit_stringformat)

        return copiedobject

    def copy(self):
        copiedobject = self.__class__(central=self.central, limit=self.error_absolute)
        copiedobject.set_digit(self._digit_round, self._digit_stringformat)

        return copiedobject

    def compare_by(self, central:bool=False, conservative:bool=False, upper:bool=False, lower:bool=False):
        """
        [__*ToDo___] (25-01-24) - 단일문으로 작성시 어테이션 에러 발생할때 도무지 알 수 없는 이유로 스레드가 종료되지 않는 스레딩 에러 발생,
        python3.10/threading.py, line 1567, lock.acquire() \n KeyboardInterrupt:
        assert 열에서 하는 일을 바깥으로 빼내어 일단 안정적으로 작동, 임시방편인지 해결팩인지 확인 필요.
        """
        number_of_true_in_arguments: int = np.sum((central, conservative, upper, lower))
        error_message = f'Only one parameter can be \"True\" among {["central", "conservative", "upper", "lower"]} for this method {self.__class__.__name__}.{inspect.getframeinfo(inspect.currentframe()).function}.'
        # error_message = f'It is invalid to provide multiple parameters as \'True\' among {["central", "conservative", "upper", "lower"]} for the method {self.__class__.__name__}.{inspect.getframeinfo(inspect.currentframe()).function}.'
        assert number_of_true_in_arguments == 1, error_message

        copiedobject = self.copy()
        if central:
            copiedobject._comparison_criterion = 'central'
            copiedobject._comparison_information = np.array([copiedobject.central, copiedobject.central])
        elif conservative:
            copiedobject._comparison_criterion = 'conservative'
            copiedobject._comparison_information = copiedobject.error_absolute
        elif upper:
            copiedobject._comparison_criterion = 'upper'
            copiedobject._comparison_information = np.array([copiedobject.error_absolute[-1], copiedobject.error_absolute[-1]])
        elif lower:
            copiedobject._comparison_criterion = 'lower'
            copiedobject._comparison_information = np.array([copiedobject.error_absolute[0], copiedobject.error_absolute[0]])
        else:
            copiedobject._comparison_criterion = 'central'
            copiedobject._comparison_information = np.array([copiedobject.central, copiedobject.central])

        return copiedobject



    def __add__(self, other):  ## from self + other
        """
        [Describe] - 가산연산에서 other가 QuantityU의 인스턴스라면 other.__radd__를 호출하여 처리하고,
        이때 other가 Quantity의 인스턴스인 경우에는 other.unit이 astropy.units.dimensionless_unscaled이지 않으면 연산 불가능하다.
        이러한 경우를 별도로 예외처리하지 않고, 연산을 시도할 경우 기존 에러가 발생하도록 의도함.

        [__*ToDo___] (24-_-_) - QuantityU와 ValueU간의 상호작용이 있고, QuantityU에서도 ValueU 클래스를 사용하고 있다.
        따라서 순환참조가 되지 않도록 하려면 QuantityU를 이렇게 메소드 내에서 호출하여 사용하는 것이 맞는지 확인 필요.
        """
        from .quantityu import QuantityU
        if isinstance(other, QuantityU):  ### Case(c) ValueU + QuantityU
            result = other.__radd__(self)
        else:
            ### Operation Head: calculate the central value of the operation results.
            if isinstance(other, self.__class__):
                result = self.__class__(central=self.central + other.central)
            else:
                result = self.__class__(central=self.central + other)

            ### Operation Body(1): Determine the uncertainty signs of the results.
            if np.all(self.error_relative == 0):
                sign_self = np.array([-1, 1])
            else:
                sign_self = (self.error_relative / np.abs(self.error_relative)).round(0)

            ### Operation Body(2): Calculate the propagated uncertainty of the results.
            if isinstance(other, self.__class__):  ### Case(a) ValueU + ValueU
                """
                [***ToDo___] (24--) - 계산 기반인수의 의존성(오차부호) 처리방법이 결정되지 않아 임시로 반영하지 않(각 계산마다 독립변수 취급)도록 처리됨
                """
                # sign_other = (other.error_relative / np.abs(other.error_relative)).round(0)
                sign_other = sign_self.copy()

                result._set_error_relative(
                    np.sqrt(np.abs((self.error_relative) ** 2 * sign_self + (other.error_relative) ** 2 * sign_other))
                    *
                    sign_self
                )
            else:  ### Case(b) ValueU + Built-in Numeric
                result._set_error_relative(self.error_relative)

        return result

    def __radd__(self, other):  ## from other + self
        return self.__add__(other)

    """
    [Describe] - 비슷한 작동을 하는 __add__를 부호만 바꾸어 활용하는 방향으로 시도중, 안정성 및 설계상 이점 확인되면 삭제 예정
    """
    # def __sub__(self, other):
    #     """
    #     [___ToDo*__] (25-02-03) - 어차피 부호만 다르고 계산 접근방식이 같다면 별개 내용을 구현하기보단 __neg__와 __add__를 이용하도록 구현하는게 나을까?
    #     만약 그렇게 하기로 결정한다면, __add__에서 인수를 반드시 매번 독립변수로 취급되도록 설계되어야만 한다.
    #     어쨋든 현재 설계로는 __neg__와 __add__를 이용해 가감연산을 전적으로 __add__에 의지하는 것이 가능할 것으로 보이지만,
    #     이 제안이 좋은 구현인지, 논리적으로 정확한 구현인지 아닌지는 더 고민해봐야 하는 문제임.
    #     이러한 문제는 QuantityU.__sub__ 에서도 동일함
    #
    #     [Describe] - 가감연산에서 other가 QuantityU의 인스턴스라면 other.__radd__를 호출하여 처리하고,
    #     만약 other가 Quantity의 인스턴스일때는 other.unit이 astropy.units.dimensionless_unscaled이지 않으면 연산 불가능하다.
    #     이러한 경우를 별도로 예외처리하지 않고, 연산을 시도할 경우 기존 에러가 발생하도록 의도함.
    #     """
    #     from class_quantityu import QuantityU
    #     if isinstance(other, QuantityU):  ### Case(a) ValueU - QuantityU
    #         result = other.__neg__().__radd__(self)
    #     else:
    #         ### Operation Head: calculate the central value of the operation results.
    #         if isinstance(other, self.__class__):
    #             result = self.__class__(central=self.central - other.central)
    #         else:
    #             result = self.__class__(central=self.central - other)
    #
    #         ### Operation Body(1): Determine the uncertainty signs of the results.
    #         if np.all(self.error_relative == 0):
    #             sign_self = np.array([-1, 1])
    #         else:
    #             sign_self = (self.error_relative / np.abs(self.error_relative)).round(0)
    #
    #         ### Operation Body(2): Calculate the propagated uncertainty of the results.
    #         if isinstance(other, self.__class__):  ### Case(b) ValueU - ValueU
    #             """
    #             [***ToDo___] (24--) - 계산 기반인수의 의존성(오차부호) 처리방법이 결정되지 않아 임시로 반영하지 않(각 계산마다 독립변수 취급)도록 처리됨
    #             """
    #             # sign_other = (other.error_relative / np.abs(other.error_relative)).round(0)
    #             sign_other = sign_self.copy()
    #
    #             result._set_error_relative(
    #                 np.sqrt(np.abs((self.error_relative) ** 2 * sign_self + np.flip(-other.error_relative) ** 2 * sign_other))
    #                 *
    #                 sign_self
    #             )
    #         else:  ### Case(c) ValueU - Built-in Numeric
    #             result._set_error_relative(self.error_relative)
    #
    #     return result

    def __neg__(self):  ## from -self
        result = self.__class__(central=-self.central, limit=-self.error_absolute)
        result.set_digit(self._digit_round, self._digit_stringformat)
        return result

    def __sub__(self, other):  ## from self - other
        return self.__add__(other.__neg__())

    def __rsub__(self, other):  ## from other - self
        return self.__neg__().__add__(other)

    def __abs__(self):  ## from abs(self)
        if self.central < 0:
            return self.__neg__()
        else:
            return self.copy()

    def __mul__(self, other):  ## from self * other
        """
        [Describe] - 승법연산에서 other가 QuantityU의 인스턴스라면 other.__rmul__를 호출하여 처리하고,
        이때 other가 Quantity의 인스턴스인 경우에는 other.unit이 astropy.units.dimensionless_unscaled이지 않으면 연산 불가능하다.
        이러한 경우를 별도로 예외처리하지 않고, 연산을 시도할 경우 기존 에러가 발생하도록 의도함.

        [__*ToDo___] (24--) - QuantityU와 ValueU간의 상호작용이 있고, QuantityU에서도 ValueU 클래스를 사용하고 있다.
        따라서 순환참조가 되지 않도록 하려면 QuantityU를 이렇게 메소드 내에서 호출하여 사용하는 것이 맞는지 확인 필요.
        """
        from .quantityu import QuantityU
        if isinstance(other, QuantityU):  ### Case(c) ValueU * QuantityU
            result = other * self
        else:
            if isinstance(other, u.core.IrreducibleUnit) or isinstance(other, u.core.CompositeUnit) or isinstance(other, u.core.Unit):  ### Case(d) ValueU * Units
                ## [Describe] - 승법연산에서 other가 astropy.units에서 제공하는 인스턴스라면, QuantityU 객체로 반환한다.
                result = QuantityU(central=self.central * other, limit=self.error_absolute * other)
            else:
                ### Operation Head: Calculate the central value of the operation results.
                if isinstance(other, self.__class__):
                    result = self.__class__(central=self.central * other.central)
                else:
                    result = self.__class__(central=self.central * other)

                ### Operation Body(1): Determine the uncertainty signs of the results.
                if np.all(self.error_relative == 0):
                    sign_self = np.array([-1, 1])
                else:
                    sign_self = (self.error_relative / np.abs(self.error_relative)).round(0)

                ### Operation Body(2): Calculate the propagated uncertainty of the results.
                if isinstance(other, self.__class__):  ### Case(a) ValueU * ValueU
                    """
                    [***ToDo___] (24--) - 계산 기반인수의 의존성(오차부호) 처리방법이 결정되지 않아 임시로 반영하지 않(각 계산마다 독립변수 취급)도록 처리됨
                    """
                    # sign_other = (other.error_relative / np.abs(other.error_relative)).round(0)
                    sign_other = sign_self.copy()

                    if self.central == 0 or other.central == 0:
                        result._set_error_relative([np.nan, np.nan])
                    else:
                        result._set_error_relative(
                            np.sqrt(
                                np.abs(
                                    (self.error_relative / self.central) ** 2 * sign_self
                                    +
                                    (other.error_relative / other.central) ** 2 * sign_other
                                )
                            )
                            *
                            result.central
                            *
                            sign_self
                        )
                else:  ### Case(b) ValueU * Built-in Numeric ; Built-in Numeric / ValueU
                    result._set_error_relative(self.error_relative * other)

        return result

    def __rmul__(self, other):  ## from other * self
        return self.__mul__(other)

    """
    [Describe] - 비슷한 작동을 하는 __mull__를 지수만 바꾸어 활용하는 방향으로 시도중, 안정성 및 설계상 이점 확인되면 삭제 예정
    """
    # def __truediv__(self, other):
    #     from class_quantityu import QuantityU
    #     if isinstance(other, QuantityU):  ### Case(a) ValueU / QuantityU
    #         result = other * (self ** (-1))
    #     else:
    #         ### Operation Head: Calculate the central value of the operation results.
    #         if isinstance(other, self.__class__):
    #             result = self.__class__(central=self.central / other.central)
    #         else:
    #             result = self.__class__(central=self.central / other)
    #
    #         ### Operation Body(1): Determine the uncertainty signs of the results.
    #         if np.all(self.error_relative == 0):
    #             sign_self = np.array([-1, 1])
    #         else:
    #             sign_self = (self.error_relative / np.abs(self.error_relative)).round(0)
    #
    #         ### Operation Body(2): Calculate the propagated uncertainty of the results.
    #         if isinstance(other, self.__class__):  ### Case(b) ValueU / ValueU
    #             """
    #             [***ToDo___] (24--) - 계산 기반인수의 의존성(오차부호) 처리방법이 결정되지 않아 임시로 반영하지 않(각 계산마다 독립변수 취급)도록 처리됨
    #             """
    #             # sign_other = (other.error_relative / np.abs(other.error_relative)).round(0)
    #             sign_other = sign_self.copy()
    #
    #             if self.central == 0 or other.central == 0:
    #                 result._set_error_relative([np.nan, np.nan])
    #             else:
    #                 result._set_error_relative(
    #                     np.sqrt(
    #                         np.abs(
    #                             (self.error_relative / self.central) ** 2 * sign_self
    #                             +
    #                             (other.error_relative / other.central) ** 2 * sign_other
    #                         )
    #                     )
    #                     *
    #                     result.central
    #                     *
    #                     sign_self
    #                 )
    #         else:  ### Case(c) ValueU / Built-in Numeric
    #             """
    #             [___ToDo***] (25-02-04) - self.error_absolute의 upper/lower error 부호가 서로 다르면 계산을 하는게 맞는가?
    #             오차가 확률정규분포를 따른다면 확률밀도의 무작위성 분포에 따라 나눗셈을 할 때 확률분포 영역과 오차범위에 대한 개념적인 문제가 생기기 때문에 아마 예외처리를 해야 할 것 같음
    #             __mul__메소드에도 같은 문제 존재.
    #             [Describe] - other가 0일 때, numpy.ndarray([numpy.nan, numpy.nan])를 반환하고, 기존 경고 "divide by zero" RuntimeWarning을 출력하도록 의도함.
    #             """
    #             result._set_error_absolute(self.error_absolute / other)
    #
    #     return result

    def __truediv__(self, other):
        return self.__mul__(other.__pow__(-1))

    def __rtruediv__(self, other):
        return self.__pow__(-1).__mul__(other)

    def __pow__(self, other):  ## from self ** other
        """
        [Describe] - 지수연산에서 other는 단위가 없거나 단위가 dimensionless_unscaled 이어야 한다.
        other가 '지수연산이 불가능한 단위를 가진 객체'인 경우를 별도로 예외처리하지 않고, 연산을 시도할 경우 에러가 발생하도록 의도함.
        띠리서 other은 반드시 numeric하거나, 단위가 dimensionless_unscaled 이어야 한다.
        """
        from class_quantityu import QuantityU
        if isinstance(other, QuantityU):  ### Case(c) ValueU ** QuantityU
            result = other.__rpow__(self)
        else:
            ### Operation Head: Calculate the central value of the operation results.
            if isinstance(other, self.__class__):
                result = self.__class__(central=self.central ** other.central)
            else:
                result = self.__class__(central=self.central ** other)

            ### Operation Body(1): Determine the uncertainty signs of the results.
            if np.all(self.error_relative == 0):
                sign_self = np.array([-1, 1])
            else:
                sign_self = (self.error_relative / np.abs(self.error_relative)).round(0)

            ### Operation Body(2): Calculate the propagated uncertainty of the results.
            if isinstance(other, self.__class__):  ### Case(a) ValueU ** ValueU
                """
                [***ToDo___] (24--) - 계산 기반인수의 의존성(오차부호) 처리방법이 결정되지 않아 임시로 반영하지 않(각 계산마다 독립변수 취급)도록 처리됨
                """
                # sign_other = (other.error_relative / np.abs(other.error_relative)).round(0)
                sign_other = sign_self.copy()

                result._set_error_relative(
                    np.sqrt(
                        np.abs(
                            (other.central * (self.error_relative / self.central)) ** 2
                            +
                            (np.log(self.central) * other.error_relative) ** 2
                        )
                    ) * np.abs(result.central) * sign_self
                )

            else:  ### Case(b) ValueU ** Built-in Numeric
                result._set_error_relative((other * self.error_relative / self.central) * np.abs(result.central))

        return result

    def __rpow__(self, other):  ## from other ** self
        from class_quantityu import QuantityU
        """
        [Describe] - other가 QuantityU의 인스턴스일 경우, QuantityU ** ValueU 연산은 QuantityU.__pow__()에서 처리할 것이다.
        따라서 Value.__rpow__()에 해당 케이스를 처리하는 별도의 기능을 구현하지 않고, 부적절한 연산을 시도할 경우 에러가 발생하도록 의도.
        """
        ### Operation Head: Calculate the central value of the operation results.
        if isinstance(other, self.__class__):
            result = self.__class__(central=other.central ** self.central)
        else:
            result = self.__class__(central=other ** self.central)

        ### Operation Body(1): Determine the uncertainty signs of the results.
        if np.all(self.error_relative == 0):
            sign_self = np.array([-1, 1])
        else:
            sign_self = (self.error_relative / np.abs(self.error_relative)).round(0)

        ### Operation Body(2): Calculate the propagated uncertainty of the results.
        if isinstance(other, self.__class__):  ### Case(a) ValueU ** ValueU
            """
            [***ToDo___] (24--) - 계산 기반인수의 의존성(오차부호) 처리방법이 결정되지 않아 임시로 반영하지 않(각 계산마다 독립변수 취급)도록 처리됨
            """
            # sign_other = (other.error_relative / np.abs(other.error_relative)).round(0)
            sign_other = sign_self.copy()

            result._set_error_relative(
                np.sqrt(
                    np.abs(
                        (self.central * (other.error_relative / other.central)) ** 2
                        +
                        (np.log(other.central) * self.error_relative) ** 2
                    )
                ) * np.abs(result.central) * sign_other
            )

        else:  ### Case(b) Built-in Numeric ** ValueU
            """
            [___ToDo***] (24--) - 이게 맞을거라고 생각하지만 검증되지 않음, 확인 필요.
            """
            result._set_error_relative((np.log(other) * self.error_relative) * np.abs(result.central))

        return result



    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.central == other.central and np.all(self.error_absolute == other.error_absolute)
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            comparison = self._comparison_information[1] < other._comparison_information[0]
        else:
            comparison = self._comparison_information[1] < other
            """
            [***ToDo___] (25-02-11) - 해당 예외를 일으킬만한 상황이 있는가? 삭제해도 문제가 없는지 검토중
            """
            # raise TypeError(f'Not valid type {type(other)} of {other} for operation method \"{__name__}\"')

        return comparison

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            comparison = self._comparison_information[0] >= other._comparison_information[1]
        else:
            comparison = self._comparison_information[0] >= other
            """
            [***ToDo___] (25-02-11) - 해당 예외를 일으킬만한 상황이 있는가? 삭제해도 문제가 없는지 검토중
            """
            # raise TypeError(f'Not valid type {type(other)} of {other} for operation method \"{__name__}\"')

        return comparison

    def __le__(self, other):
        if isinstance(other, self.__class__):
            comparison = self._comparison_information[1] <= other._comparison_information[0]
        else:
            comparison = self._comparison_information[1] <= other
            """
            [***ToDo___] (25-02-11) - 해당 예외를 일으킬만한 상황이 있는가? 삭제해도 문제가 없는지 검토중
            """
            # raise TypeError(f'Not valid type {type(other)} of {other} for operation method \"{__name__}\"')

        return comparison

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            comparison = self._comparison_information[0] >= other._comparison_information[1]
        else:
            comparison = self._comparison_information[0] >= other
            """
            [***ToDo___] (25-02-11) - 해당 예외를 일으킬만한 상황이 있는가? 삭제해도 문제가 없는지 검토중
            """
            # raise TypeError(f'Not valid type {type(other)} of {other} for operation method \"{__name__}\"')

        return comparison



    def __int__(self):
        return int(self.central)

    def __round__(self, rounddigit: int):
        """
        $ >>> v = ValueU(3.141592653589793, 0.5)
        $ ... print(repr(round(v, 3)))
        $ ValueU(3.142, (-0.5, +0.5))
        """
        result = self.__class__(central=np.round(self.central, rounddigit), limit=np.round(self.error_absolute, rounddigit))
        result.set_digit(self._digit_round, self._digit_stringformat)

        return result



    def set_digit(self, digit_round=5, digit_stringformat=10):
        if isinstance(digit_round, int):
            self._digit_round = digit_round
        else:
            raise TypeError(f'Input argument \'digit_round\' for \"{__name__}\" type wrong - must be instance of {int}')
        if isinstance(digit_stringformat, int):
            self._digit_stringformat = digit_stringformat
        else:
            raise TypeError(f'Input argument \'digit_stringformat\' for \"{__name__}\" type wrong - must be instance of {int}')

        return self

    def get_notation(self, digit_round=None):
        if digit_round == None:
            digit_round = self._digit_round

        notation_central = f'{np.round(self.central, digit_round)}'

        notations_error = []
        for notation_error in self.error_relative.copy():
            if not np.isnan(notation_error):
                notation = np.round(notation_error, digit_round)
                if notation >= 0:
                    sign = '+'
                else:
                    sign = '-'
                notations_error.append(f'{sign}{np.abs(notation)}')
            else:
                notations_error.append(f'{np.nan}')  # to-do : how to show in the error is nan

        return notation_central, notations_error

    def help(self):
        pydoc = PyDocument()
        print(f'\n{"#" * 120}\n')

        print(
            f'\033[1m\033[3m\033[4m\033[7m{self.__class__.__name__}\033[0m\033[4m: \033[1m{self.__fullname} (Class) '
            f''.ljust(120 + 4 * 7 - len(str(self.__class__.__version))) + str(self.__class__.__version) + '\033[0m')
        print(f'last updated at {self.__lastupdate.strftime("%Y-%m-%d")}'.rjust(120))

        print(f'\n\033[1m\033[4m{"Introduction:".ljust(25)}\033[0m')
        print(pydoc.f(
            f' {self.__class__.__name__} is a Python class designed for managing variables with asymmetric uncertainty.'
            f' It provides versatile functions for manipulating, calculating, and representing values with asymmetric errors.'
            f' This package processes results under the assumption of independent variables (zero covariance between uncertainties).'
            f' The required dependencies include \'NumPy\', \'Astropy\', and standard Python libraries (e.g., \'os\', \'sys\', \'inspect\', \'datetime\').'
            f' Testing and inspection were performed using \033[1mPython 3.10.14\033[0m, \033[1mNumPy 1.26.4\033[0m, and \033[1mAstropy 6.1.3\033[0m.'
            f' While performance was as expected in this specific environment, results may vary in other settings.'
            f' Additional testing is required to ensure consistent behavior across different configurations.'
        ))
        print('\n        \u2013 How to Import from This File to Start (*For alpha tester) :')
        print(
            f'            $ >>> import sys, os\n            $ ... sys.path.append(r\'{os.path.dirname(__file__)}\')\n            $ ... # Now you are able to import this package'
            f'\n            $ >>> from {os.path.basename(__file__).split(".")[0]} import {self.__class__.__name__}\n            $ >>> my_first_uncertain_value = {self.__class__.__name__}(15, 3)\n')
        print(pydoc.f(
            f' The \'__init__()\' method accepts \'central\', \'stddev\', and \'limit\' as input parameters.'
            f' The \'stddev\' can accept array-like objects (lists, tuples, numpy.ndarrays) to represent asymmetric errors.'
            f' A single standard deviation value can be provided if the lower and upper errors are symmetric.'
            f' On the other hand, \'limit\' should accept an array-like input value.'
            f' Note that \'stddev\' and \'limit\' cannot be used simultaneously.'
        ))
        print(' The full set of parameters is:\n')
        print(f'    \u2013 \033[1mCentral\033[0m [float]: \033[4mMean\033[0m value (or representative/\033[4mcentral\033[0m value) the representing probabilistic center')
        print(f'    \u2013 \033[1mStddev\033[0m [float/float-arr]: \033[4mStandard deviation\033[0m(s) representing relative uncertainty(s) from the central value')
        print(f'    \u2013 \033[1mLimit\033[0m [float-arr]: \033[4mAbsolute range\033[0m(array-like) of uncertainty (lower and upper limits)')
        print('')
        print(pydoc.f(
            f'If no keywords are specified, the first parameter is regarded as the central value and the second as the standard deviation.'
            f' \033[4mWe recommend that users avoid using protected methods\033[0m.'
            f' Although we do not restrict users from accessing protected methods like \'_set_central()\' and modifying object contents, \033[4mthese methods are not designed for user access\033[0m.'
        ))

        print(f'\n\033[1m\033[4m{"Application:".ljust(25)}\033[0m')
        print(f'\033[1m\u2022\033[0mMathematical Operation\033[0m')
        print(pydoc.f(
            f' {self.__class__.__name__} propagates uncertainty by assuming that each side of the uncertainty follows half of a normal distributions, represented by a single uncertainty value for a side.'
            f' It currently supports uncertainty propagation for addition, subtraction, multiplication, division, and exponentiation.'
            f' Future development will expand support to include more functions and operations.'
        , tab=1))
        print('\n            \u2013 Example 1 of Application : Addition of Symmetric Uncertainty')
        v1, v2 = self.__class__(72, 3), self.__class__(83, 4)
        print(f'                $ >>> v1, v2 = {repr(v1)}, {repr(v2)}\n                $ >>> print(\'v1 + v2  = \', str(v1 + v2), \' = \', repr(v1 + v2))\n                $ v1 + v2  =  {str(v1 + v2)}  =  {repr(v1 + v2)}')
        print('\n            \u2013 Example 2 of Application : Addition of Asymmetric Uncertainty')
        v1, v2 = self.__class__(72, (-3, +5)), self.__class__(83, (-4, +12))
        print(f'                $ >>> v1, v2 = {repr(v1)}, {repr(v2)}\n                $ >>> print(\'v1 + v2  = \', str(v1 + v2), \' = \', repr(v1 + v2))\n                $ v1 + v2  =  {str(v1 + v2)}  =  {repr(v1 + v2)}\n')
        print('\033[1m\u2022\033[0mPromotion\033[0m')
        from .quantityu import QuantityU
        print(pydoc.f(
            f' {self.__class__.__name__} objects are designed to be compatible with {" ".join([word[0].upper() + word[1:] for word in str(u.__name__).split(".")])}.'
            f' Multiplying a {self.__class__.__name__} object by an \'{u.__name__}\' object will promote it to a {QuantityU.__name__} object, which provides additional features for working with units.'
            f' See the {QuantityU.__name__} documentation for a complete description of its capabilities.'
        , tab=1))
        print('\n            \u2013 Example 3 of Application : Multiply with Unit Object')
        q = v1 * u.m  # It is now promoted as QuantityU, not ValueU anymore.
        print(
            f'                $ >>> q = v1 * u.m  # It is now promoted as QuantityU, not {self.__class__.__name__} anymore.\n                $ >>> print(\'q  = \', str(q), \' = \', repr(q))\n                $ q  =  {str(q)}  =  {repr(q)}\n'
            f'                $ >>> print(type(q))\n                $ {QuantityU}\n')
        print('\033[1m\u2022\033[0mComparison\033[0m')
        print(pydoc.f(
            f' To use comparison operators (<, >, <=, >=) for evaluating for {self.__class__.__name__} objects, you must first establish the comparison criteria by calling the \'{self.compare_by.__name__}()\' method.'
            f' This method accepts four keyword arguments: \'central\', \'conservative\', \'upper\', and \'lower\', which are boolean objects.'
            f' Set the corresponding keyword argument to True to enable a specific comparison criterion.'
            f' Once activated, the selected criterion will govern subsequent comparison operations.'
        , tab=1))
        print('    *\033[1mNote\033[0m: \033[4mThis current approach is under review, and future discussions may lead to major changes in its method.\033[0m')
        print('     Each keyword argument specifies the comparison criteria as follows:\n')
        print(f'        \u2013 \033[1mCentral\033[0m [bool]: Compares the \033[4mcentral\033[0m values of each {self.__class__.__name__} objects. This is often the default behavior')
        print(f'        \u2013 \033[1mConservative\033[0m [bool]: Compares in a \033[4mworst-case\033[0m manner. Returns True only when one value is clearly larger/smal-\n                               ler; otherwise, False. \'{self.__lt__.__name__}()\' being False does not guarantee \'{self.__gt__.__name__}()\' is True.')
        print(f'        \u2013 \033[1mUpper\033[0m [bool]: Compares the \033[4mupper\033[0m bounds of the uncertainty ranges of each {self.__class__.__name__} objects')
        print(f'        \u2013 \033[1mLower\033[0m [bool]: Compares the \033[4mlower\033[0m bounds of the uncertainty ranges of each {self.__class__.__name__} objects')
        print('\n            \u2013 Example 4 of Application : Comparison in Various Approaches')
        v3, v4 = self.__class__(90, 50), self.__class__(100, 10)
        print(
            f'                $ >>> v3, v4 = {repr(v3)}, {repr(v4)}\n'
            f'\n                $ >>> if v3.{v3.compare_by.__name__}(central=True) < v4.{v4.compare_by.__name__}(central=True):  # by central value\n                $ ...     print(\'v3 < v4 by central value\')'
            f'\n                $ ... elif v3.{v3.compare_by.__name__}(central=True) > v4.{v4.compare_by.__name__}(central=True):\n                $ ...     print(\'v3 > v4 by central value\')'
            f'\n                $ ... else:\n                $ ...     print(\'unable to compare by central value\')')
        print('                $ ' + ('v3 < v4 by central value' if v3.compare_by(central=True) < v4.compare_by(central=True) else 'v3 > v4 by central value' if v3.compare_by(central=True) > v4.compare_by(central=True) else 'unable to compare by central value') + '\n')
        print(
            f'                $ >>> if v3.{v3.compare_by.__name__}(conservative=True) < v4.{v4.compare_by.__name__}(conservative=True):  # conservative approach\n                $ ...     print(\'v3 < v4 in conservative approach\')'
            f'\n                $ ... elif v3.{v3.compare_by.__name__}(conservative=True) > v4.{v4.compare_by.__name__}(conservative=True):\n                $ ...     print(\'v3 > v4 in conservative approach\')'
            f'\n                $ ... else:\n                $ ...     print(\'unable to compare in conservative approach\')')
        print('                $ ' + ('v3 < v4 in conservative approach' if v3.compare_by(conservative=True) < v4.compare_by(conservative=True) else 'v3 > v4 in conservative approach' if v3.compare_by(conservative=True) > v4.compare_by(conservative=True) else 'unable to compare in conservative approach') + '\n')
        print(
            f'                $ >>> if v3.{v3.compare_by.__name__}(upper=True) < v4.{v4.compare_by.__name__}(upper=True):  # by upper error\n                $ ...     print(\'v3 < v4 by upper limit\')'
            f'\n                $ ... elif v3.{v3.compare_by.__name__}(upper=True) > v4.{v4.compare_by.__name__}(upper=True):\n                $ ...     print(\'v3 > v4 by upper limit\')'
            f'\n                $ ... else:\n                $ ...     print(\'unable to compare by central value\')')
        print('                $ ' + ('v3 < v4 by upper limit' if v3.compare_by(upper=True) < v4.compare_by(upper=True) else 'v3 > v4 by upper limit' if v3.compare_by(upper=True) > v4.compare_by(upper=True) else 'unable to compare by central value') + '\n')
        print(pydoc.f(
            f' In contrast to the previously described comparison methods, \033[4mthe == operator performs a strict equality check.\033[0m'
            f' It returns True only when both the center and uncertainty values are identical.'
        , tab=1))
        print('')
        print('\033[1m\u2022\033[0mAdditional Functions\033[0m')
        print(pydoc.f(
            f' The \'{self.copy.__name__}()\' method creates a new {self.__class__.__name__} object replicating the original.'
            f' The copied object retains the same central value and uncertainty information as the original.'
            f' This enables you to work with a copy without affecting the original object.'
        , tab=1))
        print(pydoc.f(
            f' The \'{self.errorflip.__name__}()\' method returns a new {self.__class__.__name__} object where the upper and lower limits (or errors) have been swapped.'
            f' This effectively reverses the asymmetry of the uncertainty.'
            f' The central value remains unchanged.'
            f' This can be useful for certain types of analysis or for exploring the effects of error asymmetry.'
        , tab=1))
        print('\n            \u2013 Example 5 of Application : Equal-to Operator')
        v5 = self.__class__(1897, (-1, 10))
        print(f'                $ >>> v5 = {repr(v5)}\n                $ >>> print(repr(v5.{v5.copy.__name__}()), \'==\' if v5.{v5.copy.__name__}() == v5.{v5.errorflip.__name__}() else \'!=\', repr(v5.{v5.errorflip.__name__}()))')
        print(f'                $ {repr(v5.copy())} {"=" if v5.copy() == v5.errorflip() else "!="} {repr(v5.errorflip())}\n')
        print('\033[1m\u2022\033[0mFormatting\033[0m')
        print(pydoc.f(
            f' The \'{self.set_digit.__name__}\' method allows you to customize how the object is displayed.'
            f' A first parameter, \'digit_round\', controls the number of decimal places for rounding (default: 5 digit), and \'digit_stringformat\' sets the total output width (default: 8 spaces).'
            f' For example, \".{self.set_digit.__name__}(digit_round=3, digit_stringformat=10)\" would round to 3 decimal places and use a width of 10 characters.'
            f' Users can access the formatted representation via \'{self.get_notation.__name__}\'.'
            f' However, the \'{self.__str__.__name__}()\' and \'{self.__repr__.__name__}()\' functions already use these settings.'
            f' Therefore, users rarely need to call \'get_notation()\' directly.'
        , tab=1))
        print('\n            \u2013 Example 6 of Application : Output Formatting')
        print(f'                $ >>> import numpy as np\n                $ >>> v6 = {self.__class__.__name__}(np.pi, (-np.pi * 0.011, np.pi * 0.013))')
        v6 = self.__class__(np.pi, (-np.pi * 0.011, np.pi * 0.013))
        print(f'                $ >>> print(\'formatted v6   : \', v6.{self.set_digit.__name__}(7, 13))\n                $ ... print(\'ex-formatted v6: \', v6.{self.set_digit.__name__}(10, 13))\n                $ formatted v6   : {str(v6.set_digit(7, 13))}\n                $ ex-formatted v6: {str(v6.set_digit(10, 13))}')

        print(f'\n\033[1m\033[4m{"Warning:".ljust(25)}\033[0m')
        print(pydoc.f(
            ' This class assumes that all operations involve \033[1mIndependent Variables\033[0m.'
            ' If your data contains correlated variables (i.e., non-zero covariance), the results of this class\'s operations may be unreliable.'
            ' \033[1m\033[4mDo not use this class with correlated value without thoroughly validating the results.\033[0m\n\n'
            ' The operations in this package are designed to propagate errors based on normal distribution theory, treating errors in each variable independently.'
            ' However, due to the complexities of error propagation, some operations may not be mathematically or logically sound.'
            ' We are actively working to identify and address these potential issues through ongoing testing and review.\n\n'
            ' While some NumPy methods, such as \'sum()\', \'diff()\', \'prod()\', and interactions with `numpy.ndarray`, \033[4mappear to function, they have \033[1mnot been fully validated\033[0m.'
            ' \033[1m\033[4mExercise extreme caution\033[0m when using these methods, and do not rely on their output without careful verification.'
            ' Full support for \'numpy.ndarray\' is planned for future development.\n\n'
            ' We are dedicated to improving the accuracy and reliability of this package.'
            ' If you encounter results that differ from other packages, or if you suspect an incorrect or inappropriate operation, please submit a detailed bug report to the primary developer.'
            ' Your feedback is crucial for identifying and resolving any remaining issues.'
            ' We appreciate your collaboration in making this package more robust.'
        ))

        print(f'\n\033[1m\033[4m{"Credit:".ljust(25)}\033[0m')
        print('\033[1m\u2022\033[0mDevelopers\033[0m')
        developers = [f'    {"Main Developer ".ljust(50, "-")}: {self.__developer["name"]} ({self.__developer["contact"]})']
        for collaborator in self.__collaborators:
            if collaborator["contact"] is None:
                developers.append(f'    {"Collaborate Developer ".ljust(50, "-")}: {collaborator["name"]}')
            else:
                developers.append(f'    {"Collaborate Developer ".ljust(50, "-")}: {collaborator["name"]} ({collaborator["contact"]})')
        for contributor in self.__contributors:
            developers.append(f'    {"Contributor ".ljust(50, "-")}: {contributor["name"]} ({contributor["role"]})')
        print('\n'.join(developers) + '\n')
        print('\033[1m\u2022\033[0mHistory\033[0m')
        histories = [
            {'contents': 'First Development of Varu', 'period': '2349'},
            {'contents': 'First Separated Design of ValueU / QuantityU', 'period': '2406'},
            {'contents': 'Test for Operator Magic Method', 'period': '2412'},
            {'contents': 'Code Commenting', 'period': '2412'},
            {'contents': 'Operator Magic Method Restructuring', 'period': '2507'},
            {'contents': 'Help Message Implements', 'period': '2508'},
            {'contents': 'Minor hotfix (__rtruediv__ error)', 'period': '2509'},
            {'contents': 'Minor hotfix (__rper__ error)', 'period': '2509'},
            {'contents': 'Minor hotfix (system path error in help message)', 'period': '2509'},
            {'contents': 'Minor hotfix (__array_priority__)', 'period': '2510'},
        ]
        for history_part in histories:
            print(f'    {(history_part["contents"] + " ").ljust(50, "-")}: {history_part["period"]}')

        print(f'\n{"#" * 120}\n{f"Now, you can start {self.__class__.__name__}".rjust(120)}')

        return True

    def __str__(self, connection=''):
        notation_central, notations_error = self.get_notation()

        if notations_error[0][1:] == notations_error[-1][1:]:
            notation_error = f' ± {notations_error[0][1:].ljust(self._digit_stringformat)}'
        else:
            notation_error = f' {notations_error[0].ljust(self._digit_stringformat)}, {notations_error[-1].ljust(self._digit_stringformat)}'

        notation_final = (
            f'{notation_central.ljust(self._digit_stringformat)}'
            f' '
            f'({notation_error})'
        )

        return notation_final

    def __repr__(self):
        notation_central, notations_error = self.get_notation()

        if notations_error[0][1:] == notations_error[-1][1:]:
            if np.all(np.isnan(self.error_relative)):
                notation_error = 'np.nan'
            else:
                notation_error = f'{notations_error[0][1:]}'
        else:
            notation_error = f'({notations_error[0]}, {notations_error[-1]})'

        notation_final = (
            f'{self.__class__.__name__}({notation_central},'
            f' '
            f'{notation_error})')

        return notation_final



if __name__ == '__main__':
    ValueU().help()
