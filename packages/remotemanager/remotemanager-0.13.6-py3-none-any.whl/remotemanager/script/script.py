from __future__ import annotations

import copy
import logging
import os.path
import re
from os import PathLike
from typing import Union, Any, List

from remotemanager.connection.computers import Substitution
from remotemanager.connection.computers.dynamicvalue import (
    DynamicMixin,
    EMPTY_TREATMENT_STYLES,
    INVALID_EMPTY_TREATMENT,
)
from remotemanager.storage.sendablemixin import SendableMixin
from remotemanager.utils.tokenizer import Tokenizer
from remotemanager.utils.uuid import generate_uuid

logger = logging.getLogger(__name__)

DELETION_FLAG_LINE = "~marked_for_line_deletion~"
DELETION_FLAG_LOCAL = "~marked_for_local_deletion~"
PLACEHOLDER_PATTERN = r"#(\w+)(?::([^#]+))?#"
REPLACEMENT_PATTERN = r"#{name}(?::[^#]+)?#"
ESCAPE_SEQ_PATTERN = r"(?<!!\\)\\(?!\\)"


class EscapeStub:
    """
    Stub class for avoiding regex's internal escape sequence handling

    If the `repl` argument of `re.sub` is a callable, escape sequences will not be
    processed, allowing us to handle them at a later stage.

    This is important for allowing templates to escape the `:` character
    """

    __slots__ = ["content"]

    def __init__(self, content: Any):
        self.content: str = str(content)

    def __call__(self, *args, **kwargs) -> str:
        return self.content

    def __str__(self) -> str:
        return self.content

    def __repr__(self) -> str:
        return self.content


class Script(SendableMixin):
    """
    Class for a generic, parameterisable script.

    Args:
        template (str):
            Base script to use. Accepts #parameters#
    """

    __slots__ = [
        "_template",
        "_subs",
        "_empty_treatment",
        "_init_args",
        "_temporary_args",
    ]

    def __init__(self, template: str, empty_treatment: str | None = None, **init_args):
        self._template: str = self._parse_input(template)

        self._subs: dict[str:Substitution] = {}
        self._init_args = init_args
        self._temporary_args = {}

        self._empty_treatment = None
        self.empty_treatment = empty_treatment

        self._extract_subs()

    def __getattr__(self, item):
        if item != "_subs" and hasattr(self, "_subs") and item in self._subs:
            val = self._subs[item]
            logger.debug("returning alt __getattribute__ %s=%s", item, val)
            return val
        return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        try:
            self._subs[key].value = value
            if key in self._init_args:
                del self._init_args[key]
        except (AttributeError, KeyError):
            object.__setattr__(self, key, value)

    def __hash__(self) -> int:
        """
        We should return the hash of the template, not the output

        This means that two "different" scripts will be treated as equivalent,
        but if we're relying on the uuid of a script to generate a Dataset UUID for a
        non-function run, then we are physically unable to generate the UUID at init
        """
        return hash(self.template)

    def _parse_input(self, inp: Union[str, PathLike]) -> str:
        """
        Takes an input and checks if it is a file

        Args:
            inp (str, PathLike):
                input to check. May either be a "raw" template,
                or a path to a file containing one, for example
        """
        if os.path.isfile(inp):
            print(f"reading template from file: {inp}")
            with open(inp, mode="r", encoding="utf8") as o:
                data = o.read()
            return data
        return inp

    @property
    def uuid(self) -> str:
        return generate_uuid(self.template)

    @property
    def short_uuid(self) -> str:
        return self.uuid[:8]

    def _extract_subs(self) -> None:
        """
        Extract all substitution objects from the template
        """
        # wipe cache
        self._subs = {}
        # extract all replacement targets
        symbols = re.findall(PLACEHOLDER_PATTERN, self.template)  # noqa: W605
        logger.info("Found substitution targets within script:%s", symbols)

        for match in symbols:
            logger.debug("processing match %s", match)
            name = match[0].lower()
            kwargs = match[1]

            if name in self._subs:
                if kwargs is not None and kwargs != "":
                    raise ValueError(
                        f"Got more kwargs for already registered argument "
                        f"{name}: {kwargs}"
                    )
                logger.debug("\talready processed, continuing")
                continue
            if kwargs == "":
                tmp = Substitution.from_string(name)
            else:
                tmp = Substitution.from_string(":".join(match))
            existing = getattr(self, tmp.name, None)
            if existing is not None and not isinstance(existing, DynamicMixin):
                raise ValueError(
                    f'Variable "{tmp.name}" already exists. This could '
                    f"cause unintended behaviour, please choose another "
                    f"name"
                )

            self._subs[tmp.name] = tmp

    def _link_subs(self) -> None:
        for sub in self.sub_objects:
            self._process_links(sub)

    def _process_links(self, sub: Substitution) -> None:
        if sub.static or sub.linked:
            return
        value_cache = sub.value

        logger.debug("linking sub %s, value=%s", sub.name, sub.value)

        # find all instances of an {expandable} section
        to_parse = _get_expandables(str(sub.value))

        if len(to_parse) == 0:
            return

        for section in to_parse:
            tokenized = Tokenizer(section)

            for sym in self.subs:
                if sym in tokenized.names:
                    tokenized.exchange_name(sym, f"self.{sym}")
                    if not self._subs[sym].linked:
                        self._process_links(self._subs[sym])
            logger.debug("evaluating exchanged source: %s", tokenized.source)
            try:
                evaluated = eval(tokenized.source)
            except Exception as ex:
                raise ValueError(
                    f"Exception ({type(ex)}) when "
                    f"evaluating source in: {section}\n{ex}"
                ) from ex
            try:
                evaluated = evaluated.value
            except AttributeError:
                pass

            # if the whole value is to be evaluated, we can preserve the type
            preserve_type = (
                    len(to_parse) <= 1
                    and str(sub.value).startswith("{")
                    and str(sub.value).endswith("}")
            )
            if preserve_type:
                if evaluated is None:
                    # None is a "protected" type, so passing it onward is dangerous
                    value_cache = "None"
                else:
                    value_cache = evaluated
            else:
                value_cache = value_cache.replace(f"{{{section}}}", str(evaluated))

        self._subs[sub.name].temporary_value = value_cache

    @property
    def template(self) -> str:
        """Returns the template"""
        return self._template

    @template.setter
    def template(self, template: str) -> None:
        """
        Update the template with a new one and regenerate the substitutions

        Args:
            template (str):
                new template to use
        """
        self._template = template
        self._extract_subs()

    @property
    def subs(self) -> list[str]:
        """Returns a list of all substitution names"""
        return list(self._subs.keys())

    @property
    def sub_objects(self) -> list[Substitution]:
        """Returns a list of all substitution objects"""
        return list(self._subs.values())

    @property
    def args(self) -> list:
        """Alias for self.subs"""
        return self.subs

    @property
    def arguments(self):
        """Alias for self.subs"""
        return self.subs

    @property
    def required(self) -> list[str]:
        required = []  # store the required values
        for sub in self.sub_objects:
            # if this sub is not optional, add it
            if not sub.optional:
                required.append(sub.name)
                required += sub.requires  # also add any dependencies
            # if this sub is replacing any others, check if *they* are required
            for name in sub.replaces:
                if not self._subs[name].optional:
                    required.append(sub.name)

            if not sub._optional:
                required += sub.requires

        return list(set(required))

    @property
    def missing(self) -> list[str]:
        output = []
        covered = []
        for sub in self.sub_objects:
            if not sub.optional and not sub.has_value:
                output.append(sub.name)

            for name in sub.requires:
                tmp = self._subs[name]
                if not tmp.has_value:
                    output.append(tmp.name)

            if sub.has_value:
                for name in sub.replaces:
                    covered.append(name)

        return list(set(output) - set(covered))

    @property
    def valid(self) -> bool:
        return len(self.missing) == 0

    @property
    def empty_treatment(self):
        return self._empty_treatment

    @empty_treatment.setter
    def empty_treatment(self, style: Union[str | None]):
        if style is not None and style not in EMPTY_TREATMENT_STYLES:
            raise ValueError(INVALID_EMPTY_TREATMENT.format(style=style))
        self._empty_treatment = style

    def script(self, empty_treatment: Union[str, None] = None, **run_args) -> str:
        """
        Generate the script

        Args:
            empty_treatment (str, None):
                Overrides any local setting of ``empty_treatment`` if not None

        Returns:
            str: the formatted script
        """
        # check that empty_treatment is valid
        if empty_treatment is None:
            empty_treatment = self.empty_treatment
        if (
            empty_treatment is not None
            and empty_treatment not in EMPTY_TREATMENT_STYLES
        ):
            raise ValueError(INVALID_EMPTY_TREATMENT.format(style=empty_treatment))
        # update the values
        for k, v in self._init_args.items():
            if k in self.subs:
                self._subs[k].temporary_value = v
        for k, v in run_args.items():
            if k in self.subs:
                self._subs[k].temporary_value = v
        # check validity
        if not self.valid:
            raise ValueError(f"Missing values for parameters:\n{self.missing}")
        # generation section
        self._link_subs()  # ensure values are properly linked
        script = copy.deepcopy(self._template)  # do not clobber the internal template
        for sub in self.sub_objects:
            if sub.hidden:  # don't print any values that are hidden
                value = DELETION_FLAG_LINE
            else:
                value = sub.value  # get the value in string form

            if value is None or value == "None":
                # no value, triage this argument
                treatment = empty_treatment or sub.empty_treatment
                if treatment == "ignore":
                    continue
                elif treatment == "line":
                    value = DELETION_FLAG_LINE
                elif treatment == "local":
                    value = DELETION_FLAG_LOCAL
            # replace any instance of #name#, capturing args.
            # avoid any whitespace to not get tripped up by comments
            search = re.compile(
                REPLACEMENT_PATTERN.format(name=sub.name), re.IGNORECASE
            )
            script = re.sub(search, EscapeStub(value), script)
        # replacements complete, generate the output while handling missing values
        output = []
        for line in script.split("\n"):
            if DELETION_FLAG_LINE in line:
                continue
            output.append(line.replace(DELETION_FLAG_LOCAL, ""))
        # reset temporaries
        for sub in self.sub_objects:
            sub.reset_temporary_value()
        self._temporary_args = {}

        return re.sub(
            ESCAPE_SEQ_PATTERN, "", "\n".join(output)
        )  # remove any escape sequences

    def pack(self, values: bool = True, file: str | None = None) -> str:
        """
        Store the Script

        Args:
            values (bool):
                includes any set values if True
            file (str):
                path to save to, returns the content if None

        Returns:
            str:
                File path if file is not None, else the storage content
        """
        output = copy.deepcopy(self.template)
        if values:
            for sub in self.sub_objects:
                search = re.compile(
                    REPLACEMENT_PATTERN.format(name=sub.name), re.IGNORECASE
                )
                if sub.value is not None and sub.value != sub.default:
                    value_insert = f"#{sub.target}:value={sub.value}#"
                    output = re.sub(search, EscapeStub(value_insert), output, count=1)

        if file is not None:
            with open(file, "w+", encoding="utf8") as o:
                o.write(output)
            return os.path.abspath(file)

        return output

    @classmethod
    def unpack(cls, input: str):
        if os.path.exists(input):
            with open(input, "r", encoding="utf8") as o:
                input = o.read()

        return cls(template=input)


def _get_expandables(string: str) -> List[str]:
    output = []

    cache = []
    inset = []
    escape = False
    for char in string:
        if char == "\\" and not escape:
            escape = True
            continue

        if not escape:
            if char == "{":
                inset.append("{")

                # do not append the first instance
                if len(inset) == 1:
                    continue

            if char == "}":
                if len(inset) != 0:
                    if inset[-1] == "{":
                        del inset[-1]

                if len(inset) == 0:
                    output.append("".join(cache).strip())
                    cache = []
                    inset = []
                    continue
        else:
            escape = False

        if len(inset) == 0:
            continue

        cache.append(char)

    if len(cache) != 0:
        output.append("".join(cache).strip())

    return output
