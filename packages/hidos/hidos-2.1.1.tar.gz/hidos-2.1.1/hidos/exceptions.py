class HidosError(Exception):
    """Base class for all hidos exceptions"""


class EditionNumberError(HidosError):
    """Error with edition number"""


class MultipleBranchError(HidosError):
    """More than one branch for succession"""


class SuccessionCheckedOut(HidosError):
    """Succession is checked-out"""


class SignedCommitVerifyFailedError(HidosError):
    """Git verify of signed commit failed"""


class HidosWarning(Warning):
    """Base class for all hidos exceptions"""


class SuccessionSplitWarning(HidosWarning):
    """Succession revision chain split"""


class EditionRevisionWarning(HidosWarning):
    """Ignored revision to edition"""


class SignedCommitVerifyFailedWarning(HidosWarning):
    """Git verify of signed commit failed"""
