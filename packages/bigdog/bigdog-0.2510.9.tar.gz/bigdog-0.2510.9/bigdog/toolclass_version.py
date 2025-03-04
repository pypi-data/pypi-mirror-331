import os
import datetime as dt

class SemVer:
    __fullname = 'Semantic Versioning'
    __lastupdate = dt.datetime.strptime('2025-02-11', '%Y-%m-%d')
    __version = None
    __developer = {'name': 'DH.Koh'}
    __collaborators = None
    __contributors = None
    __callsign = 'semver'

    __dependency = {}

    def __init__(self, major=0, minor=0, patch=0, prerelease=None, hotfix=None):

        self.__major = None
        self.__minor = None
        self.__patch = None

        self.__prerelease = None
        self.__hotfix = None

        self.set_version(major, minor, patch)
        self.set_subversion(prerelease, hotfix)

        return None

    def set_version(self, major: int, minor: int, patch: int):

        if major < 0:
            raise ValueError(f'Cannot provide negative integer for \'major\' version number in class {self.__class__}')
        if minor < 0:
            raise ValueError(f'Cannot provide negative integer for \'minor\' version number in class {self.__class__}')
        if patch < 0:
            raise ValueError(f'Cannot provide negative integer for \'patch\' version number in class {self.__class__}')

        self.__major, self.__minor, self.__patch = major, minor, patch

        return self

    def set_subversion(self, prerelease=None, hotfix=None):

        assert (prerelease is None and hotfix is None) or ((not prerelease is None) and hotfix is None) or ((not prerelease is None) and (not hotfix is None)), \
            f'Cannot provide \"hotfix\" without \"prerelease\" in class {self.__class__}'

        if prerelease is not None:
            if not isinstance(prerelease, str):
                raise TypeError(f'Invalid type for "prerelease" in class {self.__class__}')
            if len(prerelease) != 1:
                raise ValueError(f'Invalid length for "prerelease" in class {self.__class__}')

        if hotfix is not None and not isinstance(hotfix, int):
            raise TypeError(f'Invalid type for "hotfix" in class {self.__class__}')

        self.__prerelease, self.__hotfix = prerelease, hotfix

        return self

    def is_standardversion(self):
        return self.__prerelease is None and self.__hotfix is None

        return self

    def _islaterthan_superordinate(self, other):
        if self.__major == other.__major:
            if self.__minor == other.__minor:
                if self.__patch == other.__patch:
                    return None
                else:
                    return self.__patch > other.__patch
            else:
                return self.__minor > other.__minor
        else:
            return self.__major > other.__major

        return self

    def _islaterthan_subordinate(self, other):
        if self.__prerelease == None:
            if other.__prerelease == None:
                return None
            else:
                return False
        elif other.__prerelease == None:
            return True

        if self.__prerelease == other.__prerelease:
            if self.__hotfix == other.__hotfix:
                return None
            else:
                return self.__hotfix > other.__hotfix
        else:
            return self.__prerelease > other.__prerelease


    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'\'>\' not supported between instances of \'{self.__class__.__name__}\' and \'{other.__class__.__name__}\'')

        selfislater_superordinate = self._islaterthan_superordinate(other)

        if selfislater_superordinate is None:
            return self._islaterthan_subordinate(other) is True
        else:
            return selfislater_superordinate is True

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'\'<\' not supported between instances of \'{self.__class__.__name__}\' and \'{other.__class__.__name__}\'')

        selfislater_superordinate = self._islaterthan_superordinate(other)

        if selfislater_superordinate is None:
            return self._islaterthan_subordinate(other) is False
        else:
            return selfislater_superordinate is False

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'\'=\' not supported between instances of \'{self.__class__.__name__}\' and \'{other.__class__.__name__}\'')

        selfislater_superordinate = self._islaterthan_superordinate(other)

        if selfislater_superordinate is None:
            return self._islaterthan_subordinate(other) is None
        else:
            return False

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'\'>=\' not supported between instances of \'{self.__class__.__name__}\' and \'{other.__class__.__name__}\'')

        selfislater_superordinate = self._islaterthan_superordinate(other)

        if selfislater_superordinate is None:
            return self._islaterthan_subordinate(other) is not False
        else:
            return selfislater_superordinate is True

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'\'<=\' not supported between instances of \'{self.__class__.__name__}\' and \'{other.__class__.__name__}\'')

        selfislater_superordinate = self._islaterthan_superordinate(other)

        if selfislater_superordinate is None:
            return self._islaterthan_subordinate(other) is not True
        else:
            return selfislater_superordinate is False

    def __str__(self):
        supercomponent = '.'.join([str(self.__major), str(self.__minor), str(self.__patch)])

        if self.is_standardversion():
            subcomponent = None
        else:
            if self.__hotfix is None:
                subcomponent = f'{self.__prerelease}'
            else:
                subcomponent = f'{self.__prerelease}{str(self.__hotfix)}'

        version = f'{supercomponent}' if subcomponent is None else f'{supercomponent}-{subcomponent}'

        return f'v{version}'

    def __repr__(self):
        if self.is_standardversion():
            return f'{self.__class__.__name__}({self.__major}, {self.__minor}, {self.__patch})'
        else:
            if self.__hotfix is None:
                return f'{self.__class__.__name__}({self.__major}, {self.__minor}, {self.__patch}, prerelease = \'{self.__prerelease}\')  # \033[7mWIP\033[0m'
            else:
                return f'{self.__class__.__name__}({self.__major}, {self.__minor}, {self.__patch}, prerelease = \'{self.__prerelease}\', hotfix = {self.__hotfix})  # \033[7mWIP\033[0m'


    @staticmethod
    def dformat(string, ncolumn=120, remove_nlinespace=False):
        string_blocks = string.split('\n')
        string_blocks_result = [''] * len(string_blocks)
        for index, string_block in enumerate(string_blocks):
            while len(string_block) >= ncolumn:
                if string_block[ncolumn] == ' ':  # 'aaaa| bbbb'
                    string_blocks_result[index] += string_block[:ncolumn] + '\n'
                    string_block = string_block[ncolumn + 1:]
                elif string_block[ncolumn - 1] == ' ':  # 'aaaa |bbbb'
                    string_blocks_result[index] += string_block[:ncolumn - 1] + '\n'
                    string_block = string_block[ncolumn:]
                elif string_block[ncolumn - 2] == ' ':  # 'aaaa b|bbb'
                    string_blocks_result[index] += string_block[:ncolumn - 2] + '\n'
                    string_block = string_block[ncolumn - 1:]
                elif string_block[ncolumn - 3] == ' ' and string_block[ncolumn - 2] in ['\'', '\"', '(', '{', '[', '<', '/']:  # 'aaaa (b|bbb'
                    string_blocks_result[index] += string_block[:ncolumn - 3] + '\n'
                    string_block = string_block[ncolumn - 2:]
                elif string_block[ncolumn - 1] == '-':  # 'aaaa-|bbbb'
                    string_blocks_result[index] += string_block[:ncolumn] + '\n'
                    string_block = string_block[ncolumn:]
                elif string_block[ncolumn - 2] == '-':  # 'aaaa-b|bbb'
                    string_blocks_result[index] += string_block[:ncolumn - 1] + '\n'
                    string_block = string_block[ncolumn - 1:]
                else:  # 'aaaa|aaaa'
                    string_blocks_result[index] += string_block[:ncolumn - 1] + '-\n'
                    string_block = string_block[ncolumn - 1:]

                if remove_nlinespace:
                    string_block = string_block[[index for index, char in enumerate(list(string_block[121:])) if char != ' '][0]:]

            string_blocks_result[index] += string_block

        return '\n'.join(string_blocks_result)

    def help(self):
        print(f'\n{"#" * 120}\n')
        print(f'\033[1m\033[3m\033[4m\033[7m{self.__class__.__name__}\033[0m\033[4m(Class) : \033[1m{self.__fullname}'.ljust(120 + 4 * 7) + '\033[0m')
        print(f'last updated at {self.__lastupdate.strftime("%Y-%m-%d")}'.rjust(120))
        print('')
        print(f'\033[1m\033[4m{"Introduction:".ljust(25)}\033[0m')
        print(self.dformat(f' {self.__class__.__name__} is a Python class tailored to handle and compare version numbers for customized Python projects, aligning seamlessly with the widely adopted Semantic Versioning Specification\u2014https://semver.org in software development. This specification provides a clear and standardized way of versioning software, allowing developers to communicate changes effectively using three numbers joined with dots (MAJOR.MINOR.PATCH). The first number in the expression is the MAJOR version, increased for incompatible API changes. The second number is the MINOR version for backward-compatible functionality additions. And the third number is the PATCH version for backward-compatible bug fixes.'))
        print('')
        print(f'\033[1m\033[4m{"Application:".ljust(25)}\033[0m')
        print(self.dformat(f' To describe the version of code by using the SemVer class, instantiate an object with up to five parameters representing the version. The first three parameters\u2014MAJOR, MINOR, and PATCH\u2014are essential for proper functionality, each serving a specific purpose:\n'))
        print(f'    \u2013 \033[1mMAJOR\033[0m [int]: Represents \033[4mmajor\033[0m version changes, indicating significant, potentially incompatible modifications.')
        print(f'    \u2013 \033[1mMINOR\033[0m [int]: Denotes \033[4mminor\033[0m version changes for relatively compatible modifications.')
        print(f'    \u2013 \033[1mPATCH\033[0m [int]: Specifies the \033[4mpatch\033[0m version number for simple bug fixes.')
        print(self.dformat(f'\nHere is a usage example for creating a general version:'))
        version_standard = SemVer(5, 1, 12)
        print(f'\n    \u2013 Create a general version:\n        $ >>> version_standard = {repr(version_standard)}\n        $ ... print(\'Version notation for general release: \', str(version_standard))\n        $ Version notation for general release: {str(version_standard)}')
        print(self.dformat(f'\n The other two optional arguments—PRERELEASE and HOTFIX—are available to further describe the version:\n'))
        print(f'    \u2013 \033[1mPRERELEASE\033[0m [str, optional]: A single alphabet character representing pre-release versions.')
        print(f'    \u2013 \033[1mHOTFIX\033[0m [int, optional]: A number representing emergency hotfix versions.')
        print(self.dformat(f'\nDevelopers can use these additional factors to express work-in-progress (WIP) or emergency hotfix versions. These two arguments allow developers to articulate that the target code does not guarantee stable functionality or has applied temporary countermeasures to unexpected bugs. If separate values are not specified for those, {self.__class__.__name__} implies that the target code is released as a general version, functions as intended by the developer, and is not expected to result in known bugs, even when used by the general user. Usage of HOTFIX without setting a PRERELEASE is not allowed. In the case of a WIP version, the string representation\u2014returned by repr()\u2014of an object will include the marker "WIP" with a background, providing a clear visual indication of the ongoing development status.'))
        version_wip = SemVer(5, 1, 14, prerelease='a', hotfix=1)
        print(f'\n    \u2013 Create a version with additional parameters, pre-release, and hotfix to express WIP:\n        $ >>> version_wip = {repr(version_wip)[:-15]}\n        $ ... print(\'Version notation for WIP: \', str(version_wip))\n        $ Version notation for WIP: {str(version_wip)}')
        print(self.dformat(f'\n As {self.__class__.__name__} supports comparison magic methods, you can use comparison operators to determine the relationship between different versions. For example:'))
        version_latest = repr(version_standard) if version_standard > version_wip else repr(version_wip) if version_standard < version_wip else "They are Equal"
        print(f'\n    \u2013 Compare versions\n        $ >>> print(\'Which is the later version? : \', end=\'\')\n        $ ... if version_wip > version_standard:\n        $ ...     print(repr(version_wip))\n        $ ... elif version_wip < version_standard:\n        $ ...     print(repr(version_standard))\n        $ ... else:\n        $ ...     print(\'They are Equal\')\n        $ Which is the later version? : {version_latest}')
        print(self.dformat(f'\nThis allows you to easily check whether the target code matches a specific version or if it was released later.'))
        print('')
        print(f'\033[1m\033[4m{"Versioning Guidance:".ljust(25)}\033[0m')
        print(self.dformat(f' The standard Semantic Versioning Specification essentially supports a three-numbering system. However, the {self.__class__.__name__} class introduces an enhancement by providing two additional identifiers after an extra hyphen, allowing for the manifestation of sub-component versions indicating pre-release and hotfix versions.\n When defining a sub-component version, a pre-release version should be represented by a single alphabet character, and a hotfix version must be expressed as a single number (MAJOR.MINOR.PATCH-PRERELEASE.HOTFIX). The hotfix version must not be designated without a pre-release version. If the user omits setting the pre-release and hotfix, the version is considered a normal version, expected to operate reliably in common usage. It\'s crucial to designate a pre-release version if the function cannot be guaranteed to work as intended. A recommended version increasing guideline is as follows:\n\n    PATCH \u2013 bugfix\n    MINOR \u2013 function addition\n    MAJOR \u2013 function elimination\n\n    HOTFIX \u2013 emergency hotfix\n    PRERELEASE \u2013 any other upcoming pre-release versions\n\nThis explicit versioning regulation maintains consistency and effectively communicates the nature of changes. Developers can make informed decisions about version updates based on the specific type of modifications introduced.'))
        print('')
        print(f'\n{"#" * 120}\n{f"Now, you can start {self.__class__.__name__}".rjust(120)}')

class HeadVer:
    __fullname = 'HeadVer Versioning Specification'
    __lastupdate = dt.datetime.strptime('2025-02-19', '%Y-%m-%d')
    __version = SemVer(0, 0, 2, prerelease='a')
    __developer = {'name': 'DH.Koh', 'contact': 'donghyeok.koh.code@gmail.com'}
    __collaborators = None
    __contributors = None
    __callsign = 'headver'

    __dependency = {}

    def __init__(self, head=0, yearweek=None, build=0):

        self.__head = None
        self.__yearweek = None
        self.__build = None

        if yearweek is None:
            self.set_version(head, None, build)
        elif isinstance(yearweek, dt.datetime):
            self.set_version(head, yearweek.strftime('%y%V'), build)
        else:
            self.set_version(head, str(yearweek), build)

        return None

    def set_version(self, head: int, yearweek: str, build: int):

        if head < 0:
            raise ValueError(f'Cannot provide negative integer for \'major\' version number in class {self.__class__}')
        if yearweek is not None:
            try:
                if '.' in yearweek:
                    if len(yearweek.split('-')[0]) == 4:
                        dt.datetime.strptime(f'{yearweek}Mon', '%G.%V%a')
                    else:
                        dt.datetime.strptime(f'20{yearweek}Mon', '%G.%V%a')
                elif '-' in yearweek:
                    if len(yearweek.split('-')[0]) == 4:
                        dt.datetime.strptime(f'{yearweek}Mon', '%G-%V%a')
                    else:
                        dt.datetime.strptime(f'20{yearweek}Mon', '%G-%V%a')
                elif '/' in yearweek:
                    if len(yearweek.split('/')[0]) == 4:
                        dt.datetime.strptime(f'{yearweek}Mon', '%G/%V%a')
                    else:
                        dt.datetime.strptime(f'20{yearweek}Mon', '%G/%V%a')
                else:
                    if len(yearweek) > 4:
                        dt.datetime.strptime(f'{yearweek}Mon', '%G%V%a')
                    else:
                        dt.datetime.strptime(f'20{yearweek}Mon', '%G%V%a')
            except:
                raise ValueError(f'String format of \'minor\' not satisfying YYWW in class {self.__class__}')
        if build < 0:
            raise ValueError(f'Cannot provide negative integer for \'patch\' version number in class {self.__class__}')

        self.__head, self.__yearweek, self.__build = head, yearweek, build

        return self

    def set_version_veryfirst(self):
        self.set_version(head=0, yearweek=dt.datetime.now().strftime('%y%V'), build=0)

        return self

    def set_version_after(self, other):

        today_dt = dt.datetime.now()
        today_str = today_dt.strftime('%y%V')

        if isinstance(other, self.__class__):
            if today_str == other.__yearweek:
                self.set_version(head=other.__head, yearweek=today_str, build=other.__build+1)
            elif today_str > other.__yearweek:
                self.set_version(head=other.__head, yearweek=today_str, build=0)
            else:
                raise ValueError(f'Identified yearweek of reference ({other.__yearweek}) is later than today')
        elif isinstance(other, SemVer):
            self.set_version(head=other.__major + 1, yearweek=today_str, build=0)
        else:
            raise TypeError(f'Not supported version type as reference in class {self.__class__}')

        return self

    def _islaterthan(self, other):
        if self.__head == other.__head:
            if self.__yearweek == other.__yearweek:
                if self.__build == other.__build:
                    return None
                else:
                    return self.__build > other.__build
            else:
                return self.__yearweek > other.__yearweek
        else:
            return self.__head > other.__head


    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'\'>\' not supported between instances of \'{self.__class__.__name__}\' and \'{other.__class__.__name__}\'')

        selfislater = self._islaterthan(other)

        return selfislater is True

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'\'<\' not supported between instances of \'{self.__class__.__name__}\' and \'{other.__class__.__name__}\'')

        selfislater = self._islaterthan(other)

        return selfislater is False

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'\'=\' not supported between instances of \'{self.__class__.__name__}\' and \'{other.__class__.__name__}\'')

        selfislater = self._islaterthan(other)

        return selfislater is None

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'\'>=\' not supported between instances of \'{self.__class__.__name__}\' and \'{other.__class__.__name__}\'')

        selfislater = self._islaterthan(other)

        return selfislater is None or selfislater is True

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f'\'<=\' not supported between instances of \'{self.__class__.__name__}\' and \'{other.__class__.__name__}\'')

        selfislater = self._islaterthan(other)

        return selfislater is None or selfislater is False

    def _stringizing(self):
        return '.'.join([str(self.__head), str(self.__yearweek), str(self.__build)])

    def __str__(self):
        return f'v{".".join([str(self.__head), str(self.__yearweek), str(self.__build)])}'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__head}, {self.__yearweek}, {self.__build})'


    @staticmethod
    def dformat(string, ncolumn=120, remove_nlinespace=False):
        string_blocks = string.split('\n')
        string_blocks_result = [''] * len(string_blocks)
        for index, string_block in enumerate(string_blocks):
            while len(string_block) >= ncolumn:
                if string_block[ncolumn] == ' ':  # 'aaaa| bbbb'
                    string_blocks_result[index] += string_block[:ncolumn] + '\n'
                    string_block = string_block[ncolumn + 1:]
                elif string_block[ncolumn - 1] == ' ':  # 'aaaa |bbbb'
                    string_blocks_result[index] += string_block[:ncolumn - 1] + '\n'
                    string_block = string_block[ncolumn:]
                elif string_block[ncolumn - 2] == ' ':  # 'aaaa b|bbb'
                    string_blocks_result[index] += string_block[:ncolumn - 2] + '\n'
                    string_block = string_block[ncolumn - 1:]
                elif string_block[ncolumn - 3] == ' ' and string_block[ncolumn - 2] in ['\'', '\"', '(', '{', '[', '<', '/']:  # 'aaaa (b|bbb'
                    string_blocks_result[index] += string_block[:ncolumn - 3] + '\n'
                    string_block = string_block[ncolumn - 2:]
                elif string_block[ncolumn - 1] == '-':  # 'aaaa-|bbbb'
                    string_blocks_result[index] += string_block[:ncolumn] + '\n'
                    string_block = string_block[ncolumn:]
                elif string_block[ncolumn - 2] == '-':  # 'aaaa-b|bbb'
                    string_blocks_result[index] += string_block[:ncolumn - 1] + '\n'
                    string_block = string_block[ncolumn - 1:]
                else:  # 'aaaa|aaaa'
                    string_blocks_result[index] += string_block[:ncolumn - 1] + '-\n'
                    string_block = string_block[ncolumn - 1:]

                if remove_nlinespace:
                    string_block = string_block[[index for index, char in enumerate(list(string_block[121:])) if char != ' '][0]:]

            string_blocks_result[index] += string_block

        return '\n'.join(string_blocks_result)

    def help(self):
        print(f'\n{"#" * 120}\n')
        print(f'\033[1m\033[3m\033[4m\033[7m{self.__class__.__name__}\033[0m\033[4m(Class) : \033[1m{self.__fullname}'.ljust(120 + 4 * 7) + '\033[0m')
        print(f'last updated at {self.__lastupdate.strftime("%Y-%m-%d")}'.rjust(120))
        print('')
        print(f'\033[1m\033[4m{"Introduction:".ljust(25)}\033[0m')
        print(self.dformat(f' {self.__class__.__name__} is a Python class designed for managing head versions in customized Python projects. This class facilitates the versioning of codebases using a unique combination of head, yearweek, and build information. The head version serves as a general label for the current development state, while the yearweek and build provide additional details for tracking progress of the project.'))
        print('')
        print(f'\033[1m\033[4m{"Application:".ljust(25)}\033[0m')
        print(self.dformat(f' To utilize the {self.__class__.__name__} class, instantiate an object with three parameters representing the version information. These parameters include:\n'))
        print(f'    \u2013 \033[1mHEAD\033[0m [int]: Represents the \033[4mmajor\033[0m version number for the current development state')
        print(f'    \u2013 \033[1mYEARWEEK\033[0m [int]: Denotes the \033[4myear and week\033[0m information of last modification.')
        print(f'    \u2013 \033[1mBUILD\033[0m [int]: Specifies the \033[4mbuild\033[0m number for tracking project progress')
        print(self.dformat(f'\nHere is a usage example for creating a head version:'))
        version_head1 = HeadVer(5, '2408', 2)
        print(f'\n    \u2013 Create a head version:\n        $ >>> version_head1 = {repr(version_head1)}\n        $ ... print(\'Version notation: \', str(version_head1))\n        $ Version notation: {str(version_head1)}')
        print(self.dformat(f'\nDevelopers can choose to provide the yearweek either as a string or a datetime.datetime object for flexibility:'))
        version_head2 = HeadVer(5, dt.datetime.now(), 5)
        print(f'\n    \u2013 Create a head version with datetime.datetime:\n        $ >>> import datetime as dt\n        $ ... version_head2 = {self.__class__.__name__}(5, dt.datetime.strptime({self._HeadVer__lastupdate.strftime("%Y-%m-%d")}, "%Y-%m-%d"), 5)\n        $ ... print(\'Version notation: \', str(version_head2))\n        $ Version notation: {str(version_head2)}')
        print(self.dformat(f'\n As {self.__class__.__name__} supports comparison magic methods, you can use comparison operators to determine the relationship between different versions. For example:'))
        version_latest = repr(version_head1) if version_head1 > version_head2 else repr(version_head2) if version_head1 < version_head2 else "They are Equal"
        print(f'\n    \u2013 Compare versions\n        $ >>> print(\'Which is the later version? : \', end=\'\')\n        $ ... if version_wip > version_standard:\n        $ ...     print(repr(version_wip))\n        $ ... elif version_wip < version_standard:\n        $ ...     print(repr(version_standard))\n        $ ... else:\n        $ ...     print(\'They are Equal\')\n        $ Which is the later version? : {version_latest}')
        print(self.dformat(f'\nThis allows you to easily check whether the target code matches a specific version or if it was released later.\n HeadVer provides two additional methods for setting versions. The \'set_version_veryfirst()\' method is tailored for initializing project versioning. It effortlessly creates a HeadVer object representing the first version of the current yearweek, with the build number 0. In another context, the \'set_version_after(version_previous)\' method is handy for sequential versioning. This method generates a new HeadVer object with a build number incremented from the provided object version_previous which is type of HeadVer, allowing developers to indicate subsequent builds in the progression of project.'))
        version_headvf = HeadVer().set_version_veryfirst()
        print(f'\n    \u2013 Create a very first version:\n        $ >>> version_headvf = {self.__class__.__name__}().set_version_veryfirst()\n        $ ... print(\'Notation of very first version: \', str(version_headvf))\n        $ Notation of very first version: {str(version_headvf)}')
        version_headud = HeadVer().set_version_after(version_headvf)
        print(f'\n    \u2013 Update a project version:\n        $ >>> version_headud = {self.__class__.__name__}().set_version_after(version_headvf)\n        $ ... print(\'Notation of updated version: \', str(version_headud))\n        $ Notation of updated version: {str(version_headud)}')
        print(self.dformat(f'\nThese methods offer versatile options for version management, providing flexibility in scenarios ranging from project initialization to maintaining a sequential versioning scheme.'))
        print('')
        print(f'\033[1m\033[4m{"Versioning Guidance:".ljust(25)}\033[0m')
        print(self.dformat(f' {self.__class__.__name__} introduces a versioning approach that combines head, yearweek, and build information. The head version provides a general label for the development state, the yearweek represents the year and week of the project, and the build number tracks the progress within that week.\n When defining a head version, developers can choose to represent the yearweek information either as a YYWW string or a datetime.datetime object for flexibility. The recommended version increasing guideline is as follows:\n\n    HEAD \u2013 Regular development progress, increment the build number.\n    YEARWEEK \u2013 should reflect the current week of development.\n    BUILD \u2013 significant changes in the development state, update the head version.\n\nThis explicit versioning regulation maintains consistency and effectively communicates the nature of changes. Developers can make informed decisions about version updates based on the specific type of modifications introduced.'))
        print('')
        print(f'\n{"#" * 120}\n{f"Now, you can start {self.__class__.__name__}".rjust(120)}')

if __name__ == '__main__':

    SemVer().help()
    HeadVer().help()
