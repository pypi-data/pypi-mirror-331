import io
import json
import os.path
import re
from collections.abc import Mapping, Sequence
from itertools import product
from typing import IO, Any, Literal, Optional, TypeVar, Union, cast

import click
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic.alias_generators import to_camel

T = TypeVar("T")


def _expand_jinja(s: str, **fmt_keys) -> str:
    try:
        import jinja2  # type: ignore
    except ImportError:
        raise click.ClickException(
            "jinja2 is required for jinja strings templates. "
            "Did you install with [jinja2] extra?"
        ) from None

    return jinja2.Template(s).render(**fmt_keys)


def _expand_string(s: str, **fmt_keys: str) -> str:
    match = re.match(r"^\{\s*jinja\s*\}(.*)", s)
    if match:
        return _expand_jinja(match[1], **fmt_keys)

    try:
        return s.format(**fmt_keys)
    except KeyError as e:
        msg = f"unknown key {e} in format string: {s}"
        raise ValueError(msg) from None


def _format_json_strings(obj: T, **fmt_keys: str) -> T:
    r: Any

    if isinstance(obj, str):
        r = _expand_string(obj, **fmt_keys)
        return r

    if isinstance(obj, Sequence):
        r = [_format_json_strings(v, **fmt_keys) for v in obj]
        return r

    if isinstance(obj, Mapping):
        r = {k: _format_json_strings(v, **fmt_keys) for k, v in obj.items()}
        return r

    # obj is another type, return as-is
    return obj


class _Model(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)


class ParameterValue(_Model):
    name: str
    value: str


ParameterValuesList = Union[dict[str, str], list[str], list[ParameterValue]]


def _validate_parameter_list(
    parameters: ParameterValuesList,
) -> list[ParameterValue]:
    """
    Convert parameter to a list of ParameterValues, checking that the
    parameter names are unique.

    Each parameter has a 'name' and a 'value'. The name is used for generating
    preset names and prefixes, and the value is used for generating the actual
    configuration value. It may be useful to have a separate name and value if,
    for example, the parameter value is long or contains special characters.

    Parameters may be specified in JSON as either:

    - An object mapping parameter name to value.
    - An array of strings, where each string doubles as the parameter name and
      value.
    - An array of ParameterValue objects.
    """

    if isinstance(parameters, dict):
        return [ParameterValue(name=k, value=v) for k, v in parameters.items()]

    unique_names = set()
    converted: list[ParameterValue] = []
    for val in parameters:
        if isinstance(val, str):
            val = ParameterValue(name=val, value=val)
        if val.name in unique_names:
            raise ValueError(f"duplicate parameter name '{val.name}'")
        unique_names.add(val.name)
        converted.append(val)
    return converted


class PresetGroup(_Model):
    type: str = Field(
        ...,
        min_length=1,
        description="Type of configuration preset, "
        "e.g. configure, build, test.",
    )
    prefix: Optional[str] = Field(
        None,
        description="Prefix for preset names, "
        "defaults to name of preset group.",
    )
    sep: Optional[str] = Field(
        None,
        description="Separator for preset names, "
        "overrides separator set in matrix config.",
    )
    inherits: list[str] = Field(
        [],
        description="Name of pre-existing configuration presets to inherit "
        "in all generated presets.",
    )
    parameters: dict[str, ParameterValuesList] = Field(
        ...,
        min_length=1,
        description="Parameters to generate presets from.",
    )
    templates: dict[str, Union[dict, str]] = Field(
        {},
        description="Template for generating configuration options.",
    )

    @field_validator("parameters", mode="after")
    @classmethod
    def _validate_parameters(
        cls,
        parameters: dict[str, ParameterValuesList],
    ) -> dict[str, list[ParameterValue]]:
        """
        Narrow the type of the `parameters` member to
        `dict[str, list[ParameterValue]]`. We keep the `ParameterValuesList`
        in the type annotation so that the JSON schema type is correctly
        specified.
        """
        return {k: _validate_parameter_list(v) for k, v in parameters.items()}

    def _parameters_dict(self) -> dict[str, list[ParameterValue]]:
        """
        Returns `self.parameters`, casted to `dict[str, list[ParameterValue]]`.
        The `parameters` attribute will have already been narrowed to this type
        by `_validate_parameters`, so safe to cast.
        """
        return cast(dict[str, list[ParameterValue]], self.parameters)

    @model_validator(mode="after")
    def _validate_template_parameters(self) -> "PresetGroup":
        missing = []
        for param_name in self.templates:
            if param_name not in self.parameters:
                missing.append(param_name)

        if missing:
            s = "" if len(missing) == 1 else "s"
            missing_str = ", ".join(missing)
            msg = f"Missing parameter{s} for template keys: {missing_str}"
            raise ValueError(msg)

        return self

    def _get_template(self, param_name: str) -> dict[str, Any]:
        template = self.templates.get(param_name)
        if template is None:
            return {param_name: "{value}"}

        if isinstance(template, str):
            return {param_name: template}

        return template

    def _base_config(
        self,
        template: dict,
        prefix: str,
        sep: str,
        param: ParameterValue,
        hidden: bool,
    ) -> dict:
        config: dict = {"name": f"{prefix}{sep}{param.name}"}
        if hidden:
            config["hidden"] = True
        if self.inherits:
            config["inherits"] = self.inherits
        config.update(
            _format_json_strings(template, name=param.name, value=param.value)
        )
        return config

    def generate_presets(self, prefix: str, sep: str) -> list:
        parameters = self._parameters_dict()

        if len(self.parameters) == 1:
            param_name, values = parameters.popitem()
            template = self._get_template(param_name)
            return [
                self._base_config(template, prefix, sep, param, False)
                for param in values
            ]

        presets: list[dict] = []
        for param_name, values in parameters.items():
            template = self._get_template(param_name)
            presets.extend(
                self._base_config(template, prefix, sep, param, True)
                for param in values
            )

        for names in product(
            *((p.name for p in params) for params in parameters.values())
        ):
            preset = {
                "name": f"{prefix}{sep}{sep.join(names)}",
                "inherits": self.inherits
                + [f"{prefix}{sep}{n}" for n in names],
            }
            presets.append(preset)

        return presets


class Exploder(_Model):
    version: Literal[0]
    sep: str = Field(
        "-",
        description="Separator for generated preset names. Can be overridden "
        "by 'sep' property in preset groups.",
    )
    preset_groups: dict[str, PresetGroup] = Field(
        ...,
        description="Preset groups. Presets are generated from the Cartesian "
        "product of the parameters in each group.",
    )


def _generate_schema(ctx: click.Context, _, value):
    if not value or ctx.resilient_parsing:
        return

    click.echo(json.dumps(Exploder.model_json_schema(), indent=2))
    ctx.exit(0)


@click.command()
@click.argument(
    "template_path",
    type=click.Path(
        dir_okay=False,
        exists=True,
        readable=True,
        allow_dash=True,
    ),
    required=False,
)
@click.option(
    "--yaml",
    is_flag=True,
    help="""Parse template file as a YAML file instead of JSON. Requires that
    this package is installed with the [yaml] extra enabled.""",
)
@click.option(
    "-o",
    "--output",
    default="-",
    type=click.Path(dir_okay=False, writable=True, allow_dash=True),
    help="""File to write to; use '-' for stdout (the default).""",
)
@click.option(
    "--indent",
    "-i",
    type=int,
    default=2,
    show_default=True,
    help="""JSON indent size in spaces; pass negative number for no
    indent.""",
)
@click.option(
    "--verify",
    is_flag=True,
    help="""Instead of writing to output, verify that output file would not be
    changed, and exit with non-zero code if it would.""",
)
@click.option(
    "--include-vendor",
    is_flag=True,
    help="""Include the 'exploder' object (or whatever name is passed to
    --vendor-name option) in the 'vendor' section of output presets JSON.""",
)
@click.option(
    "--vendor-name",
    default="exploder",
    show_default=True,
    help="""Name of the property in the 'vendor' object of the template to
    look for matrix configuration.""",
)
@click.option(
    "--generate-schema",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_generate_schema,
    help="""Print JSON schema for the vendor object and exit.""",
)
@click.pass_context
def explode(
    ctx: click.Context,
    template_path: Optional[str],
    yaml: bool,
    output: str,
    indent: int,
    verify: bool,
    include_vendor: bool,
    vendor_name: str,
) -> None:
    """
    Generate CMake presets JSON from template specified in TEMPLATE_PATH.

    If TEMPLATE_PATH not provided, defaults to CMakePresetsMatrixTemplate.json
    or CMakePresetsMatrixTemplate.yaml if --yaml is passed. If -, reads from
    stdin.
    """

    if template_path is None:
        suffix = "yaml" if yaml else "json"
        template_path = f"CMakePresetsMatrixTemplate.{suffix}"
        click.Path(exists=True, readable=True, dir_okay=False).convert(
            template_path, None, ctx
        )

    if verify:
        if output == "-":
            raise click.UsageError(
                "cannot use --verify with stdout output "
                "(did you specify a path with --output?)"
            )
        if not os.path.exists(output):
            raise click.ClickException(f"path does not exist: {output}")

    if output == template_path and not output == "-":
        raise click.ClickException(
            "output file cannot be the same as input file"
        )

    with click.open_file(template_path) as f:
        template: dict = _load_yaml(f) if yaml else json.load(f)

    vendor = template.get("vendor")
    if not vendor:
        raise click.ClickException("template missing 'vendor' property")
    exploder_json_obj = vendor.get(vendor_name)
    if not exploder_json_obj:
        raise click.ClickException(
            f"vendor object missing '{vendor_name}' property"
        )

    try:
        exploder = Exploder.model_validate(exploder_json_obj)
    except ValueError as e:
        raise click.ClickException(
            f"Invalid '{vendor_name}' object: {e}"
        ) from None

    for name, group in exploder.preset_groups.items():
        presets = group.generate_presets(
            group.prefix or name,
            group.sep or exploder.sep,
        )
        template.setdefault(f"{group.type}Presets", []).extend(presets)

    if not include_vendor:
        del template["vendor"][vendor_name]
        if not template["vendor"]:
            del template["vendor"]

    if verify:
        _verify_template_unchanged(template, output, indent)
    else:
        with click.open_file(output, "w") as f:
            _write_json(f, template, indent)


def _load_yaml(f: IO[str]) -> dict:
    try:
        import yaml  # type: ignore
    except ImportError as e:
        msg = (
            "PyYAML is required to parse YAML files. "
            "Did you install with [yaml] extra?"
        )
        raise click.ClickException(msg) from e

    return yaml.safe_load(f)


def _verify_template_unchanged(template: dict, output_path: str, indent: int):
    with io.StringIO() as buf:
        _write_json(buf, template, indent)
        buf.seek(0)
        with open(output_path) as f:
            changed = not _file_cmp(buf, f)

    if changed:
        raise click.ClickException("output file would be changed")
    click.echo("No changes to output file", err=True)


def _file_cmp(f1: IO[str], f2: IO[str], chunksize: int = 1024) -> bool:
    while True:
        data = f1.read(chunksize)
        if data != f2.read(chunksize):
            return False
        if not data:
            return True


def _write_json(f: IO[str], obj: dict, indent: int):
    json.dump(obj, f, indent=indent if indent >= 0 else None)
    if indent >= 0:
        f.write("\n")


if __name__ == "__main__":
    explode()
