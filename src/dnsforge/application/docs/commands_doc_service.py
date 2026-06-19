from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class CommandDocumentationEntry:
    """Rendered metadata for one concrete argparse command path."""

    command: str
    usage: str
    description: str
    options: tuple[str, ...]


class CommandDocumentationService:
    """Generate COMMANDS.md from the actual argparse tree.

    The CLI parser remains the source of truth. This service walks every
    subparser recursively and emits only commands that are actually exposed by
    argparse, with their current options and help text.
    """

    def generate(self, parser: argparse.ArgumentParser) -> str:
        entries = tuple(self._walk(parser))
        lines: list[str] = [
            "# DNSForge Commands",
            "",
            "Generated from the DNSForge CLI parser. Do not edit command entries manually.",
            "",
            "## Global syntax",
            "",
            "```bash",
            "dnsforge [--project-root PROJECT_ROOT] <command> [options]",
            "```",
            "",
            "## Command inventory",
            "",
        ]
        for entry in entries:
            lines.extend(self._render_entry(entry))
        return "\n".join(lines).rstrip() + "\n"

    def write(self, parser: argparse.ArgumentParser, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.generate(parser), encoding="utf-8")
        return output_path

    def _walk(self, parser: argparse.ArgumentParser) -> Iterable[CommandDocumentationEntry]:
        subparser_action = self._find_subparser_action(parser)
        if subparser_action is None:
            return
        for command_name in sorted(subparser_action.choices):
            yield from self._walk_command(subparser_action.choices[command_name])

    def _walk_command(self, parser: argparse.ArgumentParser) -> Iterable[CommandDocumentationEntry]:
        nested = self._find_subparser_action(parser)
        if nested is None:
            yield self._entry(parser)
            return
        if not getattr(nested, "required", False):
            yield self._entry(parser)
        for command_name in sorted(nested.choices):
            yield from self._walk_command(nested.choices[command_name])

    def _entry(self, parser: argparse.ArgumentParser) -> CommandDocumentationEntry:
        usage = parser.format_usage().strip().replace("usage: ", "", 1)
        description = parser.description or ""
        options = tuple(self._option_lines(parser))
        return CommandDocumentationEntry(command=parser.prog, usage=usage, description=description, options=options)

    def _find_subparser_action(self, parser: argparse.ArgumentParser) -> argparse._SubParsersAction | None:
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                return action
        return None

    def _option_lines(self, parser: argparse.ArgumentParser) -> Iterable[str]:
        for action in parser._actions:
            if isinstance(action, argparse._HelpAction):
                continue
            if isinstance(action, argparse._SubParsersAction):
                continue
            names = action.option_strings or [action.dest]
            rendered_name = ", ".join(names)
            if action.metavar is not None:
                value = action.metavar
            elif action.option_strings and action.nargs == 0:
                value = ""
            elif action.option_strings:
                value = action.dest.upper()
            else:
                value = ""
            default = ""
            if action.required:
                default = " required"
            elif action.default not in (None, argparse.SUPPRESS, False):
                default = f" default={action.default!r}"
            choices = f" choices={','.join(str(item) for item in action.choices)}" if action.choices else ""
            suffix = f" {value}" if value else ""
            help_text = action.help or ""
            yield f"- `{rendered_name}{suffix}`{default}{choices}: {help_text}".rstrip()

    def _render_entry(self, entry: CommandDocumentationEntry) -> list[str]:
        lines = [f"### `{entry.command}`", ""]
        if entry.description:
            lines.extend([entry.description, ""])
        lines.extend(["```bash", entry.usage, "```", ""])
        if entry.options:
            lines.extend(["Options:", ""])
            lines.extend(entry.options)
            lines.append("")
        return lines
