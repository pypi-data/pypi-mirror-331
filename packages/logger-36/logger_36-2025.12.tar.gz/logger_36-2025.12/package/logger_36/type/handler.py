"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import logging as l
import sys as s
import typing as h

from logger_36.config.message import (
    LEVEL_CLOSING,
    LEVEL_OPENING,
    MESSAGE_MARKER,
    WHERE_SEPARATOR,
)
from logger_36.constant.error import MEMORY_MEASURE_ERROR
from logger_36.constant.handler import HANDLER_KINDS
from logger_36.constant.message import NEXT_LINE_PROLOGUE
from logger_36.task.format.message import MessageWithActualExpected
from logger_36.task.measure.chronos import TimeStamp
from logger_36.task.measure.memory import CanCheckUsage as CanCheckMemoryUsage

MessageFromRecordRaw_h = h.Callable[[l.LogRecord], str]


@h.runtime_checkable
class MessageFromRecordPreprocessed_p(h.Protocol):
    def __call__(
        self,
        record: l.LogRecord,
        /,
        *,
        PreProcessed: h.Callable[[str], str] | None = None,
    ) -> str: ...


MessageFromRecord_h = MessageFromRecordRaw_h | MessageFromRecordPreprocessed_p

_MEMORY_MEASURE_ERROR = MEMORY_MEASURE_ERROR


@d.dataclass(slots=True, repr=False, eq=False)
class handler_extension_t:
    name: str | None = None
    should_store_memory_usage: bool = False
    message_width: int = -1
    MessageFromRecord: MessageFromRecord_h = d.field(init=False)

    handler: d.InitVar[l.Handler | None] = None
    level: d.InitVar[int] = l.NOTSET
    formatter: d.InitVar[l.Formatter | None] = None

    def __post_init__(
        self, handler: l.Handler | None, level: int, formatter: l.Formatter | None
    ) -> None:
        """"""
        global _MEMORY_MEASURE_ERROR

        if self.name in HANDLER_KINDS:
            raise ValueError(
                MessageWithActualExpected(
                    "Invalid handler name",
                    actual=self.name,
                    expected=f"a name not in {str(HANDLER_KINDS)[1:-1]}",
                )
            )

        if self.name is None:
            self.name = TimeStamp()

        if self.should_store_memory_usage and not CanCheckMemoryUsage():
            self.should_store_memory_usage = False
            if _MEMORY_MEASURE_ERROR is not None:
                s.__stderr__.write(_MEMORY_MEASURE_ERROR + "\n")
                _MEMORY_MEASURE_ERROR = None

        handler.setLevel(level)

        if 0 < self.message_width < 5:
            self.message_width = 5
        if formatter is None:
            self.MessageFromRecord = self._MessageFromRecord
        else:
            handler.setFormatter(formatter)
            self.MessageFromRecord = handler.formatter.format

    def _MessageFromRecord(
        self,
        record: l.LogRecord,
        /,
        *,
        PreProcessed: h.Callable[[str], str] | None = None,
    ) -> str:
        """
        See logger_36.catalog.handler.README.txt.
        """
        message = record.msg

        if PreProcessed is not None:
            message = PreProcessed(message)
        if (self.message_width <= 0) or (message.__len__() <= self.message_width):
            if "\n" in message:
                message = NEXT_LINE_PROLOGUE.join(message.splitlines())
        else:
            if "\n" in message:
                lines = _WrappedLines(message.splitlines(), self.message_width)
            else:
                lines = _WrappedLines([message], self.message_width)
            message = NEXT_LINE_PROLOGUE.join(lines)

        if (where := getattr(record, "where", None)) is None:
            where = ""
        else:
            where = f"{NEXT_LINE_PROLOGUE}{WHERE_SEPARATOR} {where}"

        return (
            f"{record.when_or_elapsed}"
            f"{LEVEL_OPENING}{record.level_first_letter}{LEVEL_CLOSING} "
            f"{MESSAGE_MARKER} {message}{where}"
        )


def _WrappedLines(lines: list[str], message_width: int, /) -> list[str]:
    """"""
    output = []

    for line in lines:
        while line.__len__() > message_width:
            if all(
                _elm != " " for _elm in line[(message_width - 1) : (message_width + 1)]
            ):
                if line[message_width - 2] == " ":
                    piece, line = (
                        line[: (message_width - 2)].rstrip(),
                        line[(message_width - 1) :],
                    )
                else:
                    piece, line = (
                        line[: (message_width - 1)] + "-",
                        line[(message_width - 1) :],
                    )
            else:
                piece, line = (
                    line[:message_width].rstrip(),
                    line[message_width:].lstrip(),
                )
            output.append(piece)

        output.append(line)

    return output


"""
COPYRIGHT NOTICE

This software is governed by the CeCILL  license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

SEE LICENCE NOTICE: file README-LICENCE-utf8.txt at project source root.

This software is being developed by Eric Debreuve, a CNRS employee and
member of team Morpheme.
Team Morpheme is a joint team between Inria, CNRS, and UniCA.
It is hosted by the Centre Inria d'Université Côte d'Azur, Laboratory
I3S, and Laboratory iBV.

CNRS: https://www.cnrs.fr/index.php/en
Inria: https://www.inria.fr/en/
UniCA: https://univ-cotedazur.eu/
Centre Inria d'Université Côte d'Azur: https://www.inria.fr/en/centre/sophia/
I3S: https://www.i3s.unice.fr/en/
iBV: http://ibv.unice.fr/
Team Morpheme: https://team.inria.fr/morpheme/
"""
