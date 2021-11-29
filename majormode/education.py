# Copyright (C) 2021 Majormode.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import annotations

import json
import os
import traceback


class InvalidCountryEducationLevelsFileDataError(Exception):
    """
    Indicate that an education level file related to a country has invalid
    data.
    """


class UndefinedEducationLevel(Exception):
    """
    Indicate that no education level corresponds to the specified criteria.
    """


class UnsupportedCountryEducationLevelsError(Exception):
    """
    Indicate that this library has no education level data for the
    specified country.
    """


class EducationLevel:
    """
    Educational stages are subdivisions of formal learning, typically
    covering early childhood education, primary education, secondary
    education and tertiary education.

    Education during childhood and early adulthood is typically provided
    through either a two- or three-stage system of childhood school,
    followed by additional stages of higher education or vocational
    education for those who continue their formal education:

    - Early childhood education at preschool, nursery school, or
      kindergarten (outside the U.S. and Canada)
    - Primary education at primary school or elementary school, and
      sometimes in the early years of middle school
    - Secondary education at secondary school or high school, and sometimes
      in the latter years of middle school
    - Higher education or vocational education

    The following table introduces the main concepts, although terms and
    ages may vary in different places:

    +=====+===========================+================+================+=======+
    | Age |     Educational stage     | 2-stage system | 3-stage system | ISCED |
    +=====+===========================+================+================+=======+
    |  4  |                           | 	           |                |       |
    +-----+ Early childhood education |   Preschool    |   Preschool    |   0   |
    |  5  |                           |                |                |       |
    +-----+---------------------------+----------------+----------------+-------+
    |  6  |                           |                |                |       |
    +-----+                           |                |                |       |
    |  7  |                           |                |                |   1   |
    +-----+                           |                |                |       |
    |  8  |                           |                |   Elementary   |       |
    +-----+                           |                |     school     +-------+
    |  9  |     Primary education     | Primary school |                |       |
    +-----+                           |                |                |       |
    | 10  |                           |                |                |       |
    +-----+                           |                +----------------|       |
    | 11  |                           |                |                |       |
    +-----+                           |                |                |       |
    | 12  |                           |                |                |       |
    +-----+---------------------------+----------------+                |   2   |
    | 13  |                           |                |                |       |
    +-----+                           |                | Middle school  |       |
    | 14  |                           |                |                |       |
    +-----+                           |                |                |       |
    | 15  |                           |                |                |       |
    +-----+                           |                |                |       |
    | 16  |   Secondary education     |   Secondary    |                |       |
    +-----+                           |    School      +----------------+-------+
    | 17  |                           |                |                |       |
    +-----+                           |                |                |       |
    | 18  |                           |                |  High school   |   3   |
    +-----+                           |                |                |       |
    | 19  |                           |                |                |       |
    +-----+---------------------------+----------------+----------------+-------+

    @note: The International Standard Classification of Education (ISCED)
        is a statistical framework for organizing information on education
        maintained by the United Nations Educational, Scientific and
        Cultural Organization (UNESCO).
    """
    __COUNTRIES_EDUCATION_LEVELS = {}

    __JSON_FIELD_END_AGE = 'end_age'
    __JSON_FIELD_GRADE_LEVEL = 'grade_level'
    __JSON_FIELD_GRADE_NAME = 'grade_name'
    __JSON_FIELD_GRADE_SHORT_NAME = 'grade_short_name'
    __JSON_FIELD_START_AGE = 'start_age'

    @staticmethod
    def __build_instance(
            country_code: str,
            grade_level: int,
            grade_name: str,
            start_age: int,
            end_age: int,
            grade_short_name: str = None):
        """

        :param country_code:
        :param grade_level:
        :param grade_name:
        :param start_age:
        :param end_age:
        :param grade_short_name:
        :return:
        """
        class __EducationGradeImpl(EducationLevel):
            """
            Private implementation of the class {@link EducationLevel`.

            This hack allow to implement the factory method pattern in Python
            using a private class and a static method.
            """
            def __init__(
                    self,
                    country_code: str,
                    grade_level: int,
                    grade_name: str,
                    start_age: int,
                    end_age: int,
                    grade_short_name: str = None):
                super().__init__(
                    country_code,
                    grade_level,
                    grade_name,
                    start_age,
                    end_age,
                    grade_short_name=grade_short_name)

        return __EducationGradeImpl(
                    country_code,
                    grade_level,
                    grade_name,
                    start_age,
                    end_age,
                    grade_short_name=grade_short_name)

    def __init__(
            self,
            country_code: str,
            grade_level: int,
            grade_name: str,
            start_age: int,
            end_age: int,
            grade_short_name: str = None):
        """

        :param country_code: A ISO 3166-1 alpha-2 code representing the
            country this education stage corresponds to.

        :param grade_level: The number of the year a pupil has reached in this
            given educational stage for this grade.

        :param grade_name:
        :param start_age:
        :param end_age:
        :param grade_short_name:
        """
        if self.__class__.__name__ == EducationLevel.__name__:
            raise Exception(f"the class {self.__class__.__name__} MUST be instantiated with a factory method")

        self._country_code = country_code
        self._grade_level = grade_level
        self._grade_name = grade_name
        self._start_age = start_age
        self._end_age = end_age
        self._grade_short_name = grade_short_name

    @classmethod
    def __load_country_education_levels(cls, country_code: str) -> list[EducationLevel]:
        """
        Load the education levels of a specified country.


        :param country_code: A ISO 3166-1 alpha-2 code representing the
            country to load the education levels.


        :return: A list of {@link EducationLevel} instances in whatever order.
        """
        country_file_path_name = os.path.join(os.path.abspath(
                os.path.dirname(__file__)), '..', 'data', f'{country_code}.json')

        print(country_file_path_name)

        try:
            with open(country_file_path_name) as fd:
                data = json.loads(fd.read())

            country_education_levels = [
                cls.__build_instance(
                    country_code,
                    item[cls.__JSON_FIELD_GRADE_LEVEL],
                    item[cls.__JSON_FIELD_GRADE_NAME],
                    item[cls.__JSON_FIELD_START_AGE],
                    item[cls.__JSON_FIELD_END_AGE],
                    grade_short_name=item[cls.__JSON_FIELD_GRADE_SHORT_NAME] or None,
                )
                for item in data
            ]

            return country_education_levels

        except OSError:
            raise UnsupportedCountryEducationLevelsError(f"Unsupported country {country_code}")
        except KeyError:
            traceback.print_exc()
            raise InvalidCountryEducationLevelsFileDataError(
                f'The country file {country_file_path_name} contains error; '
                'please contact the maintainer of this library')

    @property
    def country_code(self) -> str:
        """
        A ISO 3166-1 alpha-2 code representing the country this education
        stage corresponds to.


        :return: A ISO 3166-1 alpha-2 code representing the country this
            education stage corresponds to.
        """
        return self._country_code

    @property
    def end_age(self) -> int:
        """
        Return the age at which pupils usually complete this grade.


        :return: The age at which pupils usually complete this grade.
        """
        return self._end_age

    @property
    def grade_level(self) -> int:
        """
        Return the number of the year a pupil has reached in this given
        educational stage for this grade.


        :return: The number of the year a pupil has reached in this given
            educational stage for this grade.
        """
        return self._grade_level

    @property
    def grade_name(self) -> str:
        """
        Return the name given to this grade.


        :return: The name given to this grade.
        """
        return self._grade_name

    @property
    def grade_short_name(self) -> str | None:
        """
        Return the short name given to this grade.


        :return: The short name given to this grade, or `None` if no short
            name at been given to this grade.
        """
        return self._grade_short_name

    @property
    def start_age(self) -> int:
        """
        Return the age at which pupils usually begin this grade.


        :return: The age at which pupils usually begin this grade.
        """
        return self._start_age

    @classmethod
    def find_by_grade_level(cls, country_code: str, grade_level: int) -> EducationLevel:
        """
        Find the education level of a country providing its grade level.


        :param country_code: A ISO 3166-1 alpha-2 code representing a country
            to return the list of education levels.

        :param grade_level: The number of the year a pupil has reached in this
            given educational stage for this grade.


        :return: An instance {@link EducationLevel} corresponding to the
            specified grade level for the given country.


        :raise UndefinedEducationLevel: If no education level corresponds to
            the specified grade level for the given country.
        """
        country_education_levels = cls.get_country_education_levels(country_code)

        education_level = next((
            education_level
            for education_level in country_education_levels
            if education_level.grade_level == grade_level),
            None)

        if not education_level:
            raise UndefinedEducationLevel(
                f"The education level for grade level {grade_level} "
                f"is not defined for country {country_code}")

        return education_level

    @classmethod
    def find_by_grade_name(cls, country_code: str, grade_name: str) -> EducationLevel:
        """
        Find the education level of a country providing its grade name.


        :param country_code: A ISO 3166-1 alpha-2 code representing a country
            to return the list of education levels.

        :param grade_name: The name given to the grade to return.


        :return: An instance {@link EducationLevel} corresponding to the
            specified grade name for the given country.


        :raise UndefinedEducationLevel: If no education level corresponds to
            the specified grade name for the given country.
        """
        _grade_name_ = grade_name.strip().lower()
        country_education_levels = cls.get_country_education_levels(country_code)

        education_level = next((
            education_level
            for education_level in country_education_levels
            if education_level.grade_name.lower() == _grade_name_),
            None)

        if not education_level:
            raise UndefinedEducationLevel(
                f"The education level for grade name {grade_name.strip()} "
                f"is not defined for country {country_code}")

        return education_level

    @classmethod
    def find_by_grade_short_name(cls, country_code: str, grade_short_name: str) -> EducationLevel:
        """
        Find the education level of a country providing its grade short name.


        :param country_code: A ISO 3166-1 alpha-2 code representing a country
            to return the list of education levels.

        :param grade_short_name: The short name given to the grade to return.


        :return: An instance {@link EducationLevel} corresponding to the
            specified grade short name for the given country.


        :raise UndefinedEducationLevel: If no education level corresponds to
            the specified grade short name for the given country.
        """
        _grade_short_name_ = grade_short_name.strip().lower()
        country_education_levels = cls.get_country_education_levels(country_code)

        education_level = next((
            education_level
            for education_level in country_education_levels
            if education_level.grade_short_name.lower() == _grade_short_name_),
            None)

        if not education_level:
            raise UndefinedEducationLevel(
                f"The education level for grade name {grade_short_name.strip()} "
                f"is not defined for country {country_code}")

        return education_level

    @classmethod
    def get_country_education_levels(cls, country_code: str) -> list[EducationLevel]:
        """
        Return the list of education grades for the specified country.


        :param country_code: A ISO 3166-1 alpha-2 code representing a country
            to return the list of education levels.


        :return: A list of {@link EducateLevel} instances.
        """
        country_code = country_code.strip().upper()

        country_education_levels = cls.__COUNTRIES_EDUCATION_LEVELS.get(country_code)
        if not country_education_levels:
            country_education_levels = cls.__load_country_education_levels(country_code)
            cls.__COUNTRIES_EDUCATION_LEVELS[country_code] = country_education_levels

        return country_education_levels
