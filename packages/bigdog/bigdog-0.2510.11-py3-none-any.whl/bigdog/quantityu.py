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
from .valueu import ValueU
# from class_identity import Identity

class QuantityU:
    __fullname = 'Quantity tagged with Uncertainty'
    __lastupdate = dt.datetime.strptime('2025-03-04', '%Y-%m-%d')
    __version = HeadVer(0, __lastupdate, 8)
    __developer = {'name': 'DH.Koh', 'contact': 'donghyeok.koh.code@gmail.com'}
    __collaborators = [{'name': 'JH.Kim', 'contact': None}, {'name': 'KM.Heo', 'contact': None}]
    __contributors = [{'name': None, 'role': 'alpha tester'}]
    __callsign = 'Quantity(+/-)'

    __versiondependency = {}

    __array_priority__ = 12000

    def __init__(self, central=np.nan, stddev=None, limit=None):
        # self.__id = uuid.uuid4()  # time.perf_counter_ns()

        assert stddev == None or limit == None,\
            f'Cannot provide both arguments \"stddev\" and \"limit\" in class {self.__class__}'

        if limit is None:
            limit = np.array([np.nan, np.nan])
        if stddev is None:
            stddev = np.nan

        ### initialize
        self.unit = None
        self.error_absolute = np.array([np.nan, np.nan]) * u.dimensionless_unscaled
        self.error_relative = np.array([np.nan, np.nan]) * u.dimensionless_unscaled
        self.value = ValueU(central=np.nan)

        self._set_central(central)

        ### recognize value
        if not np.all(np.isnan(limit)):
            self._set_error_absolute(limit)
        elif not np.all(np.isnan(stddev)):
            self._set_error_relative(stddev)

        self.set_digit(digit_round=5, digit_stringformat=8)

        return None

    def _set_central(self, central=None):
        """
        Protected Method
        modify 'self.central' to input the central value, including unit processing
        treat its unit as a dimensionless unit, if the central value is not a quantity defined in 'astropy.units'
        'self.unit' is determined by the unit of the central value
        usage :
        $ >>> q = QuantityU()
        $ ... print(repr(q))
        $ QuantityU(nan, (nan, nan))
        $ >>> q._set_central(10 * u.m)
        $ ... print(repr(q))
        $ QuantityU(10 * u.m, (nan, nan))
        """
        if central is None:
            self.unit = u.dimensionless_unscaled
            self.central = np.nan * u.dimensionless_unscaled
        else:
            if isinstance(central, u.quantity.Quantity):
                self.unit = central.unit
                self.central = central
            else:
                self.unit = u.dimensionless_unscaled
                self.central = central * u.dimensionless_unscaled

        ### unit synchronizing
        if isinstance(self.error_absolute, u.quantity.Quantity):
            if self.error_absolute.unit == u.dimensionless_unscaled:
                self.error_absolute = self.error_absolute.value * self.unit  ### dimensionlessless quantity
            else:
                self.error_absolute = self.error_absolute.to(self.unit)  ### compatible unit
        else:
            self.error_absolute = np.array([np.nan, np.nan]) * self.unit  ### unitless ndarray

        ### value synchronizing
        self.value._set_central(centralvalue=self.central.value)

        # self.__baseshape = np.array(self.central).shape
        self._sync_from_absolute()

        return self

    def _sync_from_absolute(self):
        """
        Protected Method
        modify 'self.error_relative' based on 'self.error_absolute', for synchronization between instance variables
        usage of synchronize between self.error_relative and self.error_absolute
        attention that the error if the physical type of central value is not compatible to 'self.error_absolute'
        """
        self.error_relative = self.error_absolute - self.central  ### self synchronizing
        self.value._set_error_absolute(self.error_absolute.value)  ### value synchronizing

        return self

    def _sync_from_relative(self):
        """
        Protected Method
        modify 'self.error_absolute' based on 'self.error_relative', for synchronization between instance variables
        usage of synchronize between 'self.error_absolute' and 'self.error_relative'
        attention that the error if the physical type of central value is not compatible to 'self.error_relative'
        """
        self.error_absolute = self.central + self.error_relative  ### self synchronizing
        self.value._set_error_relative(self.error_relative.value)  ### value synchronizing

        return self

    def __set_error_absolute(self, limits):
        """
        Private Method
        replace the instance variable 'self.error_absolute' with the input parameter.
        available standard format of input variable must be: [-number, +number] * astropy.unit
        """
        self.error_absolute = np.array([limits[0].to(self.unit).value, limits[1].to(self.unit).value]) * self.unit

        return self

    def _set_error_absolute(self, limit: np.ndarray):
        """
        Protected Method
        categorize and process the input dispersion range
        impossible to handle an input variable that is not structured as a shape twice the size of the central value
        impossible to handle an input variable that cannot be processed as a numpy ndarray object
        transport processed dispersion range to 'self.__set_error_relative'
        usage :
        $ >>> q = QuantityU(10 * u.m)
        $ ... print(repr(q))
        $ QuantityU(10.0 * u.m, (nan, nan))
        $ >>> q._set_error_absolute([8, 11])
        $ QuantityU(10.0 * u.m, (-2.0, +1.0))
        """
        if np.array(limit).shape == (2,):
            if isinstance(limit, u.quantity.Quantity):
                ### Case (a) [-number, +number] * unit
                self.__set_error_absolute(limits=limit)
            else:
                ### Case (b) [-number, +number]
                self.__set_error_absolute(limits=[element if isinstance(element, u.quantity.Quantity) else element * self.unit for element in limit])
        elif np.prod(np.array(limit).shape) / np.prod(np.array(self.central).shape) == 2.:
            ### Case (c) [[-number1, +number2, ...], [+number1, +number2, ...]] * unit
            """[Describe] - self.central가 단일 값이 아닐 경우를 위한 부분. 현재는 사용처가 없지만 활용 가능성이 있기 때문에 존치."""
            if not np.array(limit).shape == ((2,) + np.array(self.central).shape):
                raise ValueError(f'Input argument \"limit\" shape not matched with two times repeated shape of the central value')
            if isinstance(limit, u.quantity.Quantity):
                self.__set_error_absolute(limits=limit)
            else:
                raise NotImplementedError("Currently not supporting ndarray quantity with error")
        else:
            raise IndexError(f'Input argument \"limit\" wrong - should be two times repeated shape of the central value')

        try:
            self._sync_from_absolute()
        except:
            raise

        return self

    def __set_error_relative(self, stddevs):
        """
        Private Method
        replace the instance variable 'self.error_relative' with the input parameter.
        available standard format of input variable must be: [-number, +number] * astropy.unit
        """
        self.error_relative = np.array([stddevs[0].to(self.unit).value, stddevs[1].to(self.unit).value]) * self.unit

        return self

    def _set_error_relative(self, stddev):
        """
        Protected Method
        categorize and process the input standard deviation
        impossible to handle an input variable that is not structured as a shape twice the size of the central value
        impossible to handle an input variable that cannot be processed as a numpy ndarray object
        transport processed dispersion range to 'self.__set_error_relative'
        usage :
        $ >>> q = QuantityU(10 * u.m)
        $ ... print(repr(q))
        $ QuantityU(10.0 * u.m, (nan, nan))
        $ >>> q._set_error_relative([-1, 2])
        $ QuantityU(10.0 * u.m, (-1.0, +2.0))
        """
        if np.array(stddev).shape == (2,):
            if isinstance(stddev, u.quantity.Quantity):
                ### Case (a) [-number, +number] * unit
                self.__set_error_relative(stddevs=stddev)
            else:
                ### Case (b) [-number, +number]
                self.__set_error_relative(stddevs=[element if isinstance(element, u.quantity.Quantity) else element * self.unit for element in stddev])
        elif np.array(stddev).shape == (1,):
            if isinstance(stddev[0], u.quantity.Quantity):
                ### Case (c) [number] * unit
                self.__set_error_relative(stddevs=[-stddev[0], stddev[0]])
            else:
                ### Case (d) [number]
                self.__set_error_relative(stddevs=[-stddev[0] * self.unit, stddev[0] * self.unit])
        elif np.array(stddev).shape == ():
            if isinstance(stddev, u.quantity.Quantity):
                ### Case (e) number * unit
                self.__set_error_relative(stddevs=[-stddev, stddev])
            else:
                ### Case (f) number
                self.__set_error_relative(stddevs=[-stddev * self.unit, stddev * self.unit])
        elif np.prod(np.array(stddev).shape) / np.prod(np.array(self.central).shape) == 2.:
            """[Describe] - self.central가 단일 값이 아닐 경우를 위한 부분. 현재는 사용처가 없지만 활용 가능성이 있기 때문에 존치."""
            ### Case (g) [[-number1, +number2, ...], [+number1, +number2, ...]] * unit
            if not np.array(stddev).shape == ((2,) + np.array(self.central).shape):
                raise ValueError(f'Input argument \"stddev\" shape not matched with two times repeated shape of the central value')
            if isinstance(stddev, u.quantity.Quantity):
                self.__set_error_relative(stddevs=np.array([stddev.to(self.unit).value[0], stddev.to(self.unit).value[1]]) * self.unit)
            else:
                raise NotImplementedError("Currently not supporting ndarray value with error")
        elif np.prod(np.array(stddev).shape) / np.prod(np.array(self.central).shape) == 1.:
            """[Describe] - self.central가 단일 값이 아닐 경우를 위한 부분. 현재는 사용처가 없지만 활용 가능성이 있기 때문에 존치."""
            ### Case (h) [number1, number2, ...] * unit
            if not np.array(stddev).shape == np.array(self.central).shape:
                raise ValueError(f'Input argument \"stddev\" shape not matched with the central value')
            if isinstance(stddev, u.quantity.Quantity):
                self.__set_error_relative(stddevs=np.array([-np.array(stddev.to(self.unit).value), np.array(stddev.to(self.unit).value)]) * self.unit)
            else:
                raise NotImplementedError("Currently not supporting ndarray quantity with error")
        else:
            raise IndexError(f'Input argument \"stddev\" wrong - should be two times repeated or exactly same structure of the central value')

        try:
            self._sync_from_relative()
        except:
            raise

        return self

    def to(self, unit=None):
        """
        Method for unit decomposition
        calculate instance variables by decomposing their unit into its irreducible parts.
        to support users control the object, by same purpose and manner with 'astropy.units.quantity.Quantity.decompose()'
        usage (exactly same with astropy.units.quantity.Quantity.decompose()):
        $ >>> q = QuantityU(3.26 * u.lyr, 0.5)
        $ ... print(repr(q))
        $ QuantityU(3.26 * u.lyr, (-0.5, +0.5))
        $ >>> print(repr(q.to(u.pc)))
        $ QuantityU(0.99952 * u.pc, (-0.1533, +0.1533))
        """
        if isinstance(unit, u.UnitBase) and unit is not None:
            result = self.__class__(central=self.central.to(unit), limit=self.error_absolute.to(unit))
            result.set_digit(self._digit_round, self._digit_stringformat)
            return result
        else:
            raise u.core.UnitsError(f'Input argument \"{unit}\" is not identified as type {u.UnitBase}')

    def decompose(self):
        """
        Method for unit decomposition
        calculate instance variables by decomposing their unit into its irreducible parts.
        to support users control the object, by same purpose and manner with 'astropy.units.quantity.Quantity.decompose()'
        usage (exactly same with astropy.units.quantity.Quantity.decompose()):
        $ >>> q = QuantityU(1e-10 * u.lyr / (25 * u.km / u.second))
        $ ... print(repr(q))
        $ QuantityU(0.0 * u.lyr * u.s / u.km, (nan, nan))
        $ >>> print(repr(q.decompose()))
        $ QuantityU(37.84292 * u.s, (nan, nan))
        """
        result = self.__class__(central=self.central.decompose(), limit=self.error_absolute.decompose())
        result.set_digit(self._digit_round, self._digit_stringformat)

        return result

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
            copiedobject._comparison_information = np.array([copiedobject.central.value, copiedobject.central.value]) * copiedobject.unit
        elif conservative:
            copiedobject._comparison_criterion = 'conservative'
            copiedobject._comparison_information = copiedobject.error_absolute
        elif upper:
            copiedobject._comparison_criterion = 'upper'
            copiedobject._comparison_information = np.array([copiedobject.error_absolute[-1].value, copiedobject.error_absolute[-1].value]) * copiedobject.unit
        elif lower:
            copiedobject._comparison_criterion = 'lower'
            copiedobject._comparison_information = np.array([copiedobject.error_absolute[0].value, copiedobject.error_absolute[0].value]) * copiedobject.unit
        else:
            copiedobject._comparison_criterion = 'central'
            copiedobject._comparison_information = np.array([copiedobject.central.value, copiedobject.central.value]) * copiedobject.unit

        return copiedobject



    def __add__(self, other):  ## from self + other

        """
        [Describe] - 가산연산에서 self.unit과 other.unit의 physical type이 다르면 연산 불가능하다.
        self.unit과 other.unit이 상호 호환되지 않는 physical type인 경우를 별도로 예외처리하지 않고, 연산을 시도할 경우 기존 에러가 발생하도록 의도함.
        """
        ### Operation Head: calculate the central value of the operation results.
        if isinstance(other, self.__class__):
            result = self.__class__(central=self.central + other.central.to(self.unit))
        elif isinstance(other, ValueU):
            result = self.__class__(central=self.central + other.central)
        elif isinstance(other, u.quantity.Quantity):
            result = self.__class__(central=self.central + other.to(self.unit))
        else:
            result = self.__class__(central=self.central + other)

        ### Operation Body(1): Determine the uncertainty signs of the results.
        if np.all(self.error_relative == 0):
            sign_self = np.array([-1, 1])
        else:
            sign_self = (self.error_relative / np.abs(self.error_relative)).value.round(0)

        ### Operation Body(2): Calculate the propagated uncertainty of the results.
        if isinstance(other, self.__class__):  ### Case(a) QuantityU + QuantityU
            """
            [***ToDo___] (24--) - 계산 기반인수의 의존성(오차부호) 처리방법이 결정되지 않아 임시로 반영하지 않(각 계산마다 독립변수 취급)도록 처리됨
            """
            # sign_other = (self.error_relative / np.abs(self.error_relative)).value.round(0)
            sign_other = sign_self.copy()

            result._set_error_relative(
                np.sqrt(np.abs(self.error_relative ** 2 * sign_self + other.error_relative.to(self.unit) ** 2 * sign_other))
                *
                sign_self
            )
        elif isinstance(other, ValueU):  ### Case(b) QuantityU + ValueU
            """
            [***ToDo___] (24--) - 계산 기반인수의 의존성(오차부호) 처리방법이 결정되지 않아 임시로 반영하지 않(각 계산마다 독립변수 취급)도록 처리됨
            """
            # sign_other = (other.error_relative / np.abs(other.error_relative)).round(0)
            sign_other = sign_self.copy()

            result._set_error_relative(
                np.sqrt(np.abs(self.error_relative ** 2 * sign_self + (other.error_relative * u.dimensionless_unscaled) ** 2 * sign_other))
                *
                sign_self
            )
        else:
            if isinstance(other.error_relative, u.quantity.Quantity):  ### Case(c) QuantityU + Built-in Numeric
                result._set_error_relative(self.error_relative)
            else:
                result._set_error_relative(self.error_relative)

        return result

    def __radd__(self, other):  ## from other + self
        return self.__add__(other)

    """
    [Describe] - 비슷한 작동을 하는 __add__를 부호만 바꾸어 활용하는 방향으로 시도중, 안정성 및 설계상 이점 확인되면 삭제 예정
    """
    # def __sub__(self, other):  ## from self - other
    #     """
    #     [___ToDo*__] (25-02-03) - 어차피 부호만 다르고 계산 접근방식이 같다면 별개 내용을 구현하기보단 __neg__와 __add__를 이용하도록 구현하는게 나을까?
    #     만약 그렇게 하기로 결정한다면, __add__에서 인수를 반드시 매번 독립변수로 취급되도록 설계되어야만 한다.
    #     어쨋든 현재 설계로는 __neg__와 __add__를 이용해 가감연산을 전적으로 __add__에 의지하는 것이 가능할 것으로 보이지만,
    #     이 제안이 좋은 구현인지, 논리적으로 정확한 구현인지 아닌지는 더 고민해봐야 하는 문제임.
    #     이러한 문제는 ValueU.__sub__ 에서도 동일함
    #
    #     [Describe] - 가감연산에서 self.unit과 other.unit의 physical type이 다르면 연산 불가능하다.
    #     self.unit과 other.unit이 상호 호환되지 않는 physical type인 경우를 별도로 예외처리하지 않고, 연산을 시도할 경우 기존 에러가 발생하도록 의도함.
    #     """
    #     ### Operation Head: Calculate the central value of the operation results.
    #     if isinstance(other, self.__class__):
    #         result = self.__class__(central=self.central - other.central.to(self.unit))
    #     elif isinstance(other, ValueU):
    #         result = self.__class__(central=self.central - other.central)
    #     elif isinstance(other, u.quantity.Quantity):
    #         result = self.__class__(central=self.central - other.to(self.unit))
    #     else:
    #         result = self.__class__(central=self.central - other)
    #
    #     ### Operation Body(1): Determine the uncertainty signs of the results.
    #     if np.all(self.error_relative == 0):
    #         sign_self = np.array([-1, 1])
    #     else:
    #         sign_self = (self.error_relative / np.abs(self.error_relative)).value.round(0)
    #
    #     ### Operation Body(2): Calculate the propagated uncertainty of the results.
    #     if isinstance(other, self.__class__):  ### Case(a) QuantityU - QuantityU
    #         """
    #         [***ToDo___] (24--) - 계산 기반인수의 의존성(오차부호) 처리방법이 결정되지 않아 임시로 반영하지 않(각 계산마다 독립변수 취급)도록 처리됨
    #         """
    #         # sign_other = (self.error_relative / np.abs(self.error_relative)).value.round(0)
    #         sign_other = sign_self.copy()
    #
    #         result._set_error_relative(
    #             np.sqrt(np.abs(self.error_relative ** 2 * sign_self + (np.flip(-other.error_relative).to(self.unit)) ** 2 * sign_other))
    #             *
    #             sign_self
    #         )
    #     elif isinstance(other, ValueU):  ### Case(b) QuantityU - ValueU
    #         """
    #         [***ToDo___] (24--) - 계산 기반인수의 의존성(오차부호) 처리방법이 결정되지 않아 임시로 반영하지 않(각 계산마다 독립변수 취급)도록 처리됨
    #         """
    #         # sign_other = (other.error_relative / np.abs(other.error_relative)).round(0)
    #         sign_other = sign_self.copy()
    #
    #         result._set_error_relative(
    #             np.sqrt(np.abs(self.error_relative ** 2 * sign_self + (np.flip(-other.error_relative) * u.dimensionless_unscaled) ** 2 * sign_other))
    #             *
    #             sign_self
    #         )
    #     else:
    #         if isinstance(other.error_relative, u.quantity.Quantity):  ### Case(c) QuantityU - Built-in Numeric
    #             result._set_error_relative(self.error_relative)
    #         else:
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

    def __mul__(self, other):  ## from other * self
        ### Operation Head: Calculate the central value of the operation results.
        if isinstance(other, self.__class__) or isinstance(other, ValueU):
            result = self.__class__(central=self.central * other.central)
        else:
            result = self.__class__(central=self.central * other)

        ### Operation Body(1): Determine the uncertainty signs of the results.
        if np.all(self.error_relative == 0):
            sign_self = np.array([-1, 1])
        else:
            sign_self = (self.error_relative / np.abs(self.error_relative)).value.round(0)

        ### Operation Body(2): Calculate the propagated uncertainty of the results.
        if isinstance(other, ValueU):  ### Case(a) QuantityU * ValueU
            """
            [***ToDo___] (24--) - 계산 기반인수의 의존성(오차부호) 처리방법이 결정되지 않아 임시로 반영하지 않(각 계산마다 독립변수 취급)도록 처리됨
            """
            # sign_other = (other.error_relative / np.abs(other.error_relative)).value.round(0)
            sign_other = sign_self.copy()

            if self.central.value == 0 or other.central == 0:
                result._set_error_relative([np.nan, np.nan])
            else:
                result._set_error_relative(
                    np.sqrt(
                        np.abs(
                            (self.error_relative / self.central) ** 2 * sign_self
                            +
                            (other.error_relative / other.central) ** 2 * sign_other
                        )
                    ).decompose()
                    *
                    result.central
                    *
                    sign_self
                )

        elif isinstance(other, self.__class__):  ### Case(b) QuantityU * QuantityU
            """
            [***ToDo___] (24--) - 계산 기반인수의 의존성(오차부호) 처리방법이 결정되지 않아 임시로 반영하지 않(각 계산마다 독립변수 취급)도록 처리됨
            """
            # sign_other = (other.error_relative / np.abs(other.error_relative)).value.round(0)
            sign_other = sign_self.copy()

            if self.central.value == 0 or other.central.value == 0:
                result._set_error_relative([np.nan, np.nan])
            else:
                result._set_error_relative(
                    np.sqrt(
                        np.abs(
                            (self.error_relative / self.central) ** 2 * sign_self
                            +
                            (other.error_relative / other.central) ** 2 * sign_other
                        )
                    ).decompose()
                    *
                    result.central
                    *
                    sign_self
                )
        else:  ### Case(c) QuantityU * Built-in Numeric ; Built-in Numeric / QuantityU
            result._set_error_absolute(np.abs(self.error_absolute) * other)

        return result

    def __rmul__(self, other):
        return self * other

    """
    [Describe] - 비슷한 작동을 하는 __mull__를 지수만 바꾸어 활용하는 방향으로 시도중, 안정성 및 설계상 이점 확인되면 삭제 예정
    """
    # def __truediv__(self, other):
    #     if isinstance(other, self.__class__) or isinstance(other, ValueU):
    #         result = self.__class__(central=self.central / other.central)
    #     else:
    #         result = self.__class__(central=self.central / other)
    #
    #     if np.all(self.error_relative == 0):
    #         sign_self = np.array([-1, 1])
    #     else:
    #         sign_self = (self.error_relative / np.abs(self.error_relative)).value.round(0)
    #
    #
    #     if isinstance(other, ValueU):
    #         """
    #         [***ToDo___] (24--) - 계산 기반인수의 의존성(오차부호) 처리방법이 결정되지 않아 임시로 반영하지 않(각 계산마다 독립변수 취급)도록 처리됨
    #         """
    #         # sign_other = (other.error_relative / np.abs(other.error_relative)).value.round(0)
    #         sign_other = sign_self.copy()
    #
    #         if self.central.value == 0 or other.central == 0:
    #             result._set_error_relative([np.nan, np.nan])
    #         else:
    #             result._set_error_relative(
    #                 np.sqrt(
    #                     np.abs(
    #                         (self.error_relative / self.central) ** 2 * sign_self
    #                         +
    #                         (other.error_relative / other.central) ** 2 * sign_other
    #                     )
    #                 ).decompose()
    #                 *
    #                 result.central
    #                 *
    #                 sign_self
    #             )
    #
    #     elif isinstance(other, self.__class__):
    #         """
    #         [***ToDo___] (24--) - 계산 기반인수의 의존성(오차부호) 처리방법이 결정되지 않아 임시로 반영하지 않(각 계산마다 독립변수 취급)도록 처리됨
    #         """
    #         # sign_other = (other.error_relative / np.abs(other.error_relative)).value.round(0)
    #         sign_other = sign_self.copy()
    #
    #         if self.central.value == 0 or other.central.value == 0:
    #             result._set_error_relative([np.nan, np.nan])
    #         else:
    #             result._set_error_relative(
    #                 np.sqrt(
    #                     np.abs(
    #                         (self.error_relative / self.central) ** 2 * sign_self
    #                         +
    #                         (other.error_relative / other.central) ** 2 * sign_other
    #                     )
    #                 ).decompose()
    #                 *
    #                 result.central
    #                 *
    #                 sign_self
    #             )
    #     else:
    #         result._set_error_absolute(np.abs(self.error_absolute) / other)
    #
    #     return result
    #
    #     return result

    def __truediv__(self, other):
        return self.__mul__(other.__pow__(-1))

    def __rtruediv__(self, other):
        return self.__pow__(-1).__mul__(other)

    def __pow__(self, other):
        """
        [Describe] - 지수연산에서 other는 단위가 없거나 단위가 dimensionless_unscaled 이어야 한다.
        other가 '지수연산이 불가능한 단위를 가진 객체'인 경우를 별도로 예외처리하지 않고, 연산을 시도할 경우 에러가 발생하도록 의도함.
        띠리서 other은 반드시 numeric하거나, 단위가 dimensionless_unscaled 이어야 한다.
        """
        ### Operation Head: Calculate the central value of the operation results.
        if isinstance(other, self.__class__):
            result = self.__class__(central=self.central ** other.central.decompose())
        elif isinstance(other, ValueU):
            result = self.__class__(central=self.central ** other.central)
        else:
            result = self.__class__(central=self.central ** other)

        ### Operation Body(1): Determine the uncertainty signs of the results.
        if np.all(self.error_relative == 0):
            sign_self = np.array([-1, 1])
        else:
            sign_self = (self.error_relative / np.abs(self.error_relative)).round(0)

        ### Operation Body(2): Calculate the propagated uncertainty of the results.
        if isinstance(other, ValueU) or isinstance(other, self.__class__):  ### Case(a) QuantityU ** ValueU / QuantityU ** QuantityU
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
                ).decompose()
                *
                np.abs(result.central)
                *
                sign_self
            )

        else:  ### Case(b) QuantityU ** Built-in Numeric
            result._set_error_relative((other * self.error_relative / self.central) * np.abs(result.central))

        return result

    def __rpow__(self, other):  ## from other ** self
        """
        [Describe] - 역지수연산에서 self는 단위가 dimensionless인 units.quantity.Quantity의 인스턴스여야 한다.
        따라서 Value.__rpow__()에 해당 케이스를 처리하는 별도의 기능을 구현하지 않고, 부적절한 연산을 시도할 경우 에러가 발생하도록 의도.
        """
        ### Operation Head: Calculate the central value of the operation results.
        if isinstance(other, self.__class__):
            result = self.__class__(central=other.central ** self.central.decompose())
        elif isinstance(other, ValueU):
            result = self.__class__(central=other.central ** self.central)
        else:
            result = self.__class__(central=other ** self.central)

        ### Operation Body(1): Determine the uncertainty signs of the results.
        if np.all(self.error_relative == 0):
            sign_self = np.array([-1, 1])
        else:
            sign_self = (self.error_relative / np.abs(self.error_relative)).round(0)

        ### Operation Body(2): Calculate the propagated uncertainty of the results.
        if isinstance(other, ValueU):  ### Case(b) ValueU ** QuantityU / QuantityU ** QuantityU
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

        else:  ### Case(b) Built-in Numeric ** QuantityU
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
        return int(self.central.value)

    def __round__(self, rounddigit: int):
        """
        $ >>> q = QuantityU(3.141592653589793 * u.lyr, 0.5)
        $ ... print(repr(round(q, 3)))
        $ QuantityU(3.142 * u.lyr, (-0.5, +0.5))
        """
        result = self.__class__(central=np.round(self.central, rounddigit), limit=np.round(self.error_absolute, rounddigit))
        result.set_digit(self._digit_round, self._digit_stringformat)

        return result



    def set_digit(self, digit_round=3, digit_stringformat=5):
        if isinstance(digit_round, int):
            self._digit_round = digit_round
        else:
            raise TypeError(f'Input argument \'digit_round\' for \"{__name__}\" type wrong - have not to be {int}')
        if isinstance(digit_stringformat, int):
            self._digit_stringformat = digit_stringformat
        else:
            raise TypeError(f'Input argument \'digit_stringformat\' for \"{__name__}\" type wrong - have not to be {int}')

        self.value.set_digit(digit_round=digit_round, digit_stringformat=digit_stringformat)

        return self

    def help(self):
        pydoc = PyDocument()
        print(f'\n{"#" * 120}\n')

        print(
            f'\033[1m\033[3m\033[4m\033[7m{self.__class__.__name__}\033[0m\033[4m: \033[1m{self.__fullname} (Class) '
            f''.ljust(120 + 4 * 7 - len(str(self.__class__.__version))) + str(self.__class__.__version) + '\033[0m')
        print(f'last updated at {self.__lastupdate.strftime("%Y-%m-%d")}'.rjust(120))

        print(f'\n\033[1m\033[4m{"Introduction:".ljust(25)}\033[0m')
        print(pydoc.f(
            f' {self.__class__.__name__} is a Python class designed to manage variables with asymmetric uncertainty and physical units.'
            f' It provides versatile functions for manipulating, calculating, and representing values with asymmetric errors.'
            f' {self.__class__.__name__} is an upper-compatible extension of {ValueU.__name__}, adding unit control and representation.'
            f' This package processes results under the assumption of independent variables (zero covariance between uncertainties).'
            f' Dependencies include \'NumPy\', \'Astropy\', and standard Python libraries (e.g., \'os\', \'sys\', \'inspect\', \'datetime\').'
            f' Testing and inspection were performed using \033[1mPython 3.10.14\033[0m, \033[1mNumPy 1.26.4\033[0m, and \033[1mAstropy 6.1.3\033[0m.'
            f' While performance was as anticipated in this environment, results may differ in other settings.'
            f' Additional testing is required to ensure consistent behavior across different configurations.'
        ))
        print('\n        \u2013 How to Import from This File to Start (*For alpha tester) :')
        print(
            f'            $ >>> import sys, os\n            $ ... sys.path.append(r\'{os.path.dirname(__file__)}\')\n            $ ... # Now you are able to import this package'
            f'\n            $ >>> from {os.path.basename(__file__).split(".")[0]} import {self.__class__.__name__}\n            $ >>> my_first_uncertain_quantity = {self.__class__.__name__}(15, 3)\n')
        print(pydoc.f(
            f' The \'__init__()\' method accepts \'central\', \'stddev\', and \'limit\' as input parameters.'
            f' The \'stddev\' can accept array-like objects (lists, tuples, numpy.ndarrays) to represent asymmetric errors.'
            f' A single standard deviation value can be provided if the lower and upper errors are symmetric.'
            f' On the other hand, \'limit\' should accept an array-like input value.'
            f' Note that \'stddev\' and \'limit\' cannot be used simultaneously.'
        ))
        print(' The full set of parameters is:\n')
        print(f'    \u2013 \033[1mCentral\033[0m [float]: \033[4mMean\033[0m value (or representative/\033[4mcentral\033[0m value) with associated unit, serving as the base unit for\n                       other properties.')
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
        q1, q2 = self.__class__(72 * u.m, 3), self.__class__(800 * u.cm, 400)
        print(f'                $ >>> q1, q2 = {repr(q1)}, {repr(q2)}\n'
              f'                $ >>> print(\'q1 + q2  = \', str(q1 + q2), \' = \', repr(q1 + q2))\n'
              f'                $ q1 + q2  =  {str(q1 + q2)}  =  {repr(q1 + q2)}\n')
        print('\n            \u2013 Example 2 of Application : Addition of Asymmetric Uncertainty')
        q1, q2 = self.__class__(72 * u.m, (-3, +12)), self.__class__(800 * u.cm, (-400, +500))
        print(f'                $ >>> q1, q2 = {repr(q1)}, {repr(q2)}\n'
              f'                $ >>> print(\'q1 + q2  = \', str(q1 + q2), \' = \', repr(q1 + q2))\n'
              f'                $ q1 + q2  =  {str(q1 + q2)}  =  {repr(q1 + q2)}\n')
        print(f'\033[1m\u2022\033[0mUnit Conversion\033[0m')
        print('    ***writing...***')
        print('\n            \u2013 Example 3 of Application : Unit Conversion')
        q1 = self.__class__(274 * u.mm, (-3, +5))
        print(f'                $ >>> q1 = {repr(q1)}\n                $ >>> print(\'q1 in meter  = \', str(q1.to(u.m)))\n                $ q1 in meter  =  {str(q1.to(u.m))}\n')
        print('\n            \u2013 Example 3 of Application : Unit Decomposition')
        import astropy.constants as const
        q3 = self.__class__(4582 * u.km, 10)
        print(f'                $ >>> import astropy.constants as const\n                $ >>> q3 = {repr(q3)}\n                $ >>> print(\'q3 in frequancy      = \', str((const.c / q3).decompose()))\n                $ q3 in frequancy  =  {str((const.c / q3).decompose())}\n')
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
        q3, q4 = self.__class__(90 * u.cm, 50), self.__class__(100 * u.cm, 10)
        print(
            f'                $ >>> q3, q4 = {repr(q3)}, {repr(q4)}\n'
            f'\n                $ >>> if q3.{q3.compare_by.__name__}(central=True) < q4.{q4.compare_by.__name__}(central=True):  # by central value\n                $ ...     print(\'q3 < q4 by central value\')'
            f'\n                $ ... elif q3.{q3.compare_by.__name__}(central=True) > q4.{q4.compare_by.__name__}(central=True):\n                $ ...     print(\'q3 > q4 by central value\')'
            f'\n                $ ... else:\n                $ ...     print(\'unable to compare by central value\')')
        print('                $ ' + ('q3 < q4 by central value' if q3.compare_by(central=True) < q4.compare_by(central=True) else 'q3 > q4 by central value' if q3.compare_by(central=True) > q4.compare_by(central=True) else 'unable to compare by central value') + '\n')
        print(
            f'                $ >>> if q3.{q3.compare_by.__name__}(conservative=True) < q4.{q4.compare_by.__name__}(conservative=True):  # conservative approach\n                $ ...     print(\'q3 < q4 in conservative approach\')'
            f'\n                $ ... elif q3.{q3.compare_by.__name__}(conservative=True) > q4.{q4.compare_by.__name__}(conservative=True):\n                $ ...     print(\'q3 > q4 in conservative approach\')'
            f'\n                $ ... else:\n                $ ...     print(\'unable to compare in conservative approach\')')
        print('                $ ' + ('q3 < q4 in conservative approach' if q3.compare_by(conservative=True) < q4.compare_by(conservative=True) else 'q3 > q4 in conservative approach' if q3.compare_by(conservative=True) > q4.compare_by(conservative=True) else 'unable to compare in conservative approach') + '\n')
        print(
            f'                $ >>> if q3.{q3.compare_by.__name__}(upper=True) < q4.{q4.compare_by.__name__}(upper=True):  # by upper error\n                $ ...     print(\'q3 < q4 by upper limit\')'
            f'\n                $ ... elif q3.{q3.compare_by.__name__}(upper=True) > q4.{q4.compare_by.__name__}(upper=True):\n                $ ...     print(\'q3 > q4 by upper limit\')'
            f'\n                $ ... else:\n                $ ...     print(\'unable to compare by central value\')')
        print('                $ ' + ('q3 < q4 by upper limit' if q3.compare_by(upper=True) < q4.compare_by(upper=True) else 'q3 > q4 by upper limit' if q3.compare_by(upper=True) > q4.compare_by(upper=True) else 'unable to compare by central value') + '\n')
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
        q5 = self.__class__(1897 * u.yr, (-1, 10))
        print(f'                $ >>> q5 = {repr(q5)}\n                $ >>> print(repr(q5.{q5.copy.__name__}()), \'==\' if q5.{q5.copy.__name__}() == q5.{q5.errorflip.__name__}() else \'!=\', repr(q5.{q5.errorflip.__name__}()))')
        print(f'                $ {repr(q5.copy())} {"=" if q5.copy() == q5.errorflip() else "!="} {repr(q5.errorflip())}')
        print('')
        print('\033[1m\u2022\033[0mFormatting\033[0m')
        print(pydoc.f(
            f' The \'{self.set_digit.__name__}\' method allows you to customize how the object is displayed.'
            f' A first parameter, \'digit_round\', controls the number of decimal places for rounding (default: 5 digit), and \'digit_stringformat\' sets the total output width (default: 8 spaces).'
            f' For example, \".{self.set_digit.__name__}(digit_round=3, digit_stringformat=10)\" would round to 3 decimal places and use a width of 10 characters.'
        , tab=1))
        print('\n            \u2013 Example 6 of Application : Output Formatting')
        print(f'                $ >>> import numpy as np\n                $ ... import astropy.units as u\n                $ >>> q6 = {self.__class__.__name__}(np.pi * u.hour, (-np.pi * 0.011, np.pi * 0.013))')
        q6 = self.__class__(np.pi * u.hour, (-np.pi * 0.011, np.pi * 0.013))
        print(f'                $ >>> print(\'formatted q6   : \', q6.{self.set_digit.__name__}(7, 13))\n                $ ... print(\'ex-formatted q6: \', q6.{self.set_digit.__name__}(10, 13))\n                $ formatted q6   : {str(q6.set_digit(7, 13))}\n                $ ex-formatted q6: {str(q6.set_digit(10, 13))}')

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
            {'contents': 'Minor hotfix (__rtruediv__ error)', 'period': '2509'},
            {'contents': 'Minor hotfix (system path error in help message)', 'period': '2509'},
            {'contents': 'Help Message Implements', 'period': '2509'},
            {'contents': 'Minor hotfix (__array_priority__)', 'period': '2510'}
        ]
        for history_part in histories:
            print(f'    {(history_part["contents"] + " ").ljust(50, "-")}: {history_part["period"]}')

        print(f'\n{"#" * 120}\n{f"Now, you can start {self.__class__.__name__}".rjust(120)}')

        return True

    def __str__(self, connection=''):
        notation_central, notations_error = self.value.get_notation()

        if notations_error[0][1:] == notations_error[1][1:]:
            if np.all(np.isnan(self.error_relative)):
                notation_error = 'np.nan'
            else:
                notation_error = f' ± {notations_error[0][1:].ljust(self._digit_stringformat)}'
        else:
            notation_error = f' {notations_error[0].ljust(self._digit_stringformat)}, {notations_error[-1].ljust(self._digit_stringformat)}'

        if self.unit is u.dimensionless_unscaled:
            notation_unit = ''
        else:
            notation_unit = f' [{self.unit}]'

        notation_final = (
            f'{notation_central.ljust(self._digit_stringformat)}'
            f' '
            f'({notation_error})'
            f'{notation_unit}'
        )

        return notation_final

    def __repr__(self):
        notation_central, notations_error = self.value.get_notation()

        if notations_error[0][1:] == notations_error[-1][1:]:
            if np.all(np.isnan(self.error_relative)):
                notation_error = 'np.nan'
            else:
                notation_error = f'{notations_error[0][1:]}'
        else:
            notation_error = f'({notations_error[0]}, {notations_error[-1]})'

        if self.unit is u.dimensionless_unscaled:
            notation_unit = ''
        else:
            notation_unit_elements = []
            for operator, part in zip(('*', '/'), self.unit.to_string().split(' / ')):
                if part[0] == '(' and part[-1] == ')':
                    part = part[1:-1]
                for unitelement in part.split(' '):
                    if unitelement != '1':

                        unitelement_powerbase = unitelement
                        unitelement_powerexponent = '1'

                        indices_notnum = [index for index, char in enumerate(unitelement) if not char.isnumeric()]
                        if unitelement[-1].isnumeric():
                            unitelement_powerbase = unitelement[:indices_notnum[-1] + 1]
                            unitelement_powerexponent = unitelement[indices_notnum[-1] + 1:]

                        if '(' in unitelement and ')' in unitelement:
                            unitelement_powerexponent_expected = unitelement[unitelement.find('(') + 1:unitelement.find(')')]
                            splitedcomp = unitelement_powerexponent_expected.split('/')
                            if len(splitedcomp) == 2 and splitedcomp[0].isnumeric() and splitedcomp[1].isnumeric():
                                unitelement_powerbase = unitelement[:unitelement.find('(')]
                                unitelement_powerexponent = f'({unitelement_powerexponent_expected})'

                        if unitelement_powerexponent == '1':
                            notation_unit_elements.append(f' {operator} u.{unitelement_powerbase}')
                        else:
                            notation_unit_elements.append(f' {operator} u.{unitelement_powerbase} ** {unitelement_powerexponent}')

            notation_unit = ''.join(notation_unit_elements)

        notation_final = (
            f'{self.__class__.__name__}({notation_central}{notation_unit},'
            f' '
            f'{notation_error})')

        return notation_final



if __name__ == '__main__':
    QuantityU().help()
