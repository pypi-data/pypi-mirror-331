import re
from typing import List, Optional

from django.template.base import TokenType, Lexer

from django_unused2.dataclasses import TemplateTokenReference, ReferenceType


def extract_template_reference(token: str) -> Optional[str]:
    include_pattern = re.compile(r"[a-z]+\s*['\" ](?P<file_path>[^'\" ]+)['\"]")

    include_match = include_pattern.search(token)
    if include_match:
        return include_match.group("file_path")

    return token.split(" ")[0]


def extract_template_references(template_text: str) -> List[TemplateTokenReference]:
    """
    Extract all template references from a template string with its type.
    """
    lexer = Lexer(template_text)

    tokens = lexer.tokenize()
    result = []
    for token in tokens:
        contents = token.contents
        if token.token_type == TokenType.BLOCK and (
            contents.startswith("include ") or contents.startswith("extends ")
        ):
            reference_type: ReferenceType = ReferenceType.unknown
            if contents.startswith("include "):
                reference_type = ReferenceType.include
            if contents.startswith("extends "):
                reference_type = ReferenceType.extends
            relative_path = extract_template_reference(contents)
            if not relative_path:
                raise ValueError(f"Unknown token: {contents}")
            result.append(
                TemplateTokenReference(
                    relative_path,
                    line_number=token.lineno,
                    reference_type=reference_type,
                )
            )
    return result
