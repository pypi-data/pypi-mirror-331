
import re
from importlib.metadata import version


###################################
# Versioning Class
###################################
#
# This class is used to manage the versioning of the
# software or other products
#
# The versioning is based on the Semantic Versioning 2.0.0
#


__version__ = version('semantic_version_tools')

code = {"d": "devel", "a": "alpha", "b": "beta", "rc": "ReleaseCandidate", "f": "Final"}

numeric_map = {"d": 1, "a": 2, "b": 3, "rc": 4, "f": 5}


class Vers:
    """
    Class for the manipulation of objects version following the Semantic Versioning

    major.minor.patch-<prerel>.<build>

    Is implemented a special dialect.



    The admitted pre-release values are

        * d  for the developing version
        * a  for the alpha version
        * b  for the beta version
        * rc for the release candidate
        * f  for the final version
    """

    def __init__(self, ver: tuple | str) -> None:

        if isinstance(ver, str):
            a = re.match(
                r"(\d+)\.(\d+)(?:\.(\d+))?(?:[-\.]([a-zA-Z]*)(?:\.?(\d+))?)?", ver
            )
            prt = list(a.groups())
            prt[0:2] = [int(i) for i in prt[0:2]]
            if prt[2] is not None:
                prt[2] = int(prt[2])
            if prt[3] is not None:
                if prt[3].lower() in "development":
                    prt[3] = "d"
                elif prt[3].lower() in "alpha":
                    prt[3] = "a"
                elif prt[3].lower() in "beta":
                    prt[3] = "b"
                elif prt[3].lower() in "releasecandidate":
                    prt[3] = "rc"
                elif prt[3].lower() in "final":
                    prt[3] = "f"
            else:
                prt[3] = None
            if prt[3] is not None and prt[4] is None:
                prt[4] = None
            else:
                if prt[3] is not None:
                    prt[4] = int(prt[4])
            ver = tuple([x for x in prt if x is not None])
        # print(ver)
        self._len = 3
        if len(ver) < 3:
            self.major, self.minor, *extra = ver
            self.patch = 0
            self._len = 2
        else:
            self.major, self.minor, self.patch, *extra = ver
        # self.patch = extra[0] if extra else None
        self.type = extra[0] if len(extra) != 0 else 'f'
        if self.type is not None:
            if not isinstance(self.type, str):
                raise Exception(
                    f"The fourth element of the version number must be a string"
                )
            if not self.type in code.keys():
                raise ValueError(
                    f"the fourth element of the version mus be one of {
                                ','.join(code.keys())}"
                )
        self.build = extra[1] if len(extra) > 1 else 1

    def full(self) -> str:
        """
        Return the full version

        Returns:
            str: the version string
        """
        if self.type is None or self.type.lower() == "f":
            nVer = f"{self.major}.{self.minor}{
                f'.{self.patch}' if self._len == 3 else ''}"
        # elif:
        #     nVer = f"{self.major}.{self.minor}.{self.patch}"
        else:
            nVer = f"{self.major}.{self.minor}.{
                self.patch}-{code[self.type]}.{self.build}"
        return nVer

    def short(self) -> str:
        """
        Return the version in the form major.minor.patch

        Returns:
            str: the version string
        """
        return f"{self.major}.{self.minor}{f'.{self.patch}' if self._len==3 else ''}"

    def __repr__(self) -> str:
        return f"Version {self.full()}"

    def __str__(self) -> str:
        return f"Version {self.full()}"

    def __eq__(self, other) -> bool:
        if (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
        ):
            if self.type is None:
                return True
            else:
                if self.type == other.type and self.build == other.build:
                    return True
                else:
                    return False
        else:
            return False
        # return all(getattr(self, item) == getattr(other, item) for item in self.__dict__ if not item.startswith('_'))

    def __ne__(self, other) -> bool:
        return not self == other

    def __gt__(self, other) -> bool:
        if self.major != other.major:
            return self.major > other.major
        elif self.minor != other.minor:
            return self.minor > other.minor
        elif self.patch != other.patch:
            return self.patch > other.patch
        elif numeric_map[self.type] != numeric_map[other.type]:
            return numeric_map[self.type] > numeric_map[other.type]
        else:
            return self.build > other.build

    def __ge__(self, other) -> bool:
        if self > other or self == other:
            return True
        else:
            return False

    def __lt__(self, other) -> bool:
        if self.major != other.major:
            return self.major < other.major
        elif self.minor != other.minor:
            return self.minor < other.minor
        elif self.patch != other.patch:
            return self.patch < other.patch
        elif numeric_map[self.type] != numeric_map[other.type]:
            return numeric_map[self.type] < numeric_map[other.type]
        else:
            return self.build < other.build

    def __le__(self, other) -> bool:
        if self < other or self == other:
            return True
        else:
            return False

    def __add__(self, other:"Vers") -> "Vers":
        
        if isinstance(other,int):
            self.minor += other
            
        if isinstance(other,float):
            a=str(other).split(".")
            self.major += int(a[0])
            self.minor += int(a[1])
            
        if isinstance(other, Vers):
            self.major += other.major
            self.minor += other.minor
            if self._len == 3:
                self.patch += other.patch
        return self
# version = Vers(VERSION)
