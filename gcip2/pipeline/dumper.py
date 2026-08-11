import typing_extensions
import yaml


class CustomDumper(yaml.SafeDumper):
    @staticmethod
    def str_presenter(
        dumper: yaml.representer.BaseRepresenter,
        data: str,
    ) -> yaml.ScalarNode:
        if "\n" in data:
            return dumper.represent_scalar(  # type: ignore
                "tag:yaml.org,2002:str",
                data,
                style="|",
            )

        return dumper.represent_scalar(  # type: ignore
            "tag:yaml.org,2002:str",
            data,
        )

    yaml_representers = {
        **yaml.SafeDumper.yaml_representers,
        str: str_presenter,
    }

    @typing_extensions.override
    def increase_indent(
        self: typing_extensions.Self,
        flow: bool = False,
        indentless: bool = False,
    ):
        return super().increase_indent(flow, False)

    @typing_extensions.override
    def write_line_break(self, data: typing_extensions.Optional[str] = None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()
