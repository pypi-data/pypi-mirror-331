"""Prompt builder using Pydantic schema + examples"""
import json
from textwrap import dedent
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel


class PromptBuilder:
    """Builds an LLM prompt based on a predefined output schema given by a Pydantic model
    """

    def __init__(self, schema_model: type[BaseModel]):
        """
        Initialize the prompt builder with a Pydantic model and optional examples.
        
        Args:
            schema_model: The Pydantic model class defining the expected structure
            examples: Optional list of validated examples conforming to the schema
        """
        self.schema_model = schema_model

    def get_schema_description(self) -> str:
        """Generate a human-readable description of the schema requirements."""
        schema = self.schema_model.model_json_schema()

        def resolve_ref(ref: str, schema: dict) -> dict:
            """Resolve $ref by looking up in definitions."""
            if not ref.startswith('#/$defs/'):
                return {}
            ref_name = ref[len('#/$defs/'):]
            return schema.get('$defs', {}).get(ref_name, {})

        def format_field(name: str,
                         field_schema: dict,
                         schema: dict,
                         required_keys_at_level: list[str],
                         indent: int = 0) -> List[str]:
            """Format a field for the prompt"""
            lines = []

            description = field_schema.get('description', '')
            required = name in required_keys_at_level

            # Resolve $ref if present
            if '$ref' in field_schema:
                field_schema = resolve_ref(field_schema['$ref'], schema)

            is_nullable = False
            if 'type' in field_schema:
                field_type = field_schema.get('type', 'any')
            elif 'anyOf' in field_schema:
                any_of = field_schema['anyOf']
                is_nullable = any(p.get('type') == 'null' for p in any_of)
                any_of_non_null = [p for p in any_of if p.get('type') != 'null']

                if len(any_of_non_null) > 1:
                    raise ValueError("Union types are not supported.")

                if len(any_of_non_null) == 0:
                    raise RuntimeError("Unexpected error. No non-null type found.")

                any_of_non_null_item = any_of_non_null[0]
                if '$ref' in any_of_non_null_item:
                    any_of_non_null_item = resolve_ref(any_of_non_null_item['$ref'], schema)

                field_type = any_of_non_null_item.get('type', 'any')
                field_schema = any_of_non_null_item
            else:
                field_type = 'any'

            if field_type == 'array':
                items = field_schema.get('items', {})
                if '$ref' in items:
                    items = resolve_ref(items['$ref'], schema)
                    field_schema = items
                field_type = f"{field_type}[{items.get('type', 'any')}]"

            # Build base line
            line = "  " * indent + f"- {name} ({field_type})"
            if description:
                line += f": {description}"
            if required and not is_nullable:
                line += " (non-null)"
            else:
                line += " (nullable)"
            lines.append(line)

            # Handle nested objects
            if field_type in {'object', 'array[object]'} and 'properties' in field_schema:
                for nested_name, nested_schema in field_schema['properties'].items():
                    lines.extend(
                        format_field(name=nested_name,
                                     field_schema=nested_schema,
                                     schema=schema,
                                     required_keys_at_level=field_schema.get('required', []),
                                     indent=indent + 1))

            return lines

        fields = []
        for name, props in schema.get('properties', {}).items():
            fields.extend(
                format_field(name=name,
                             field_schema=props,
                             schema=schema,
                             required_keys_at_level=schema.get('required', [])))

        return "\n".join(fields)

    def build_prompt(self, examples: Optional[List[Tuple[str, Dict]]] = None, include_markdown: bool = False) -> str:
        """
        Build the instruction prompt with schema requirements and examples.
        
        Args:
            examples: Optional list of (input_text, output_json) pairs showing example extractions
        """
        include_markdown_instructions = """
All outputs must be formatted as valid JSON. Wrap the output in a markdown JSON code block.

Example of CORRECT output format:
```json
\\{"field1": "value1", "field2": null\\}
```

Example of INCORRECT output format:
\\{"field1": "value1", "field2": null\\}

""" if include_markdown else """
All outputs must be formatted as valid JSON. DO NOT include any markdown formatting.

Example of CORRECT output format:
\\{"field1": "value1", "field2": null\\}

Example of INCORRECT output format:
```json
\\{"field1": "value1", "field2": null\\}
```
"""

        def format_as_markdown(text: str) -> str:
            if include_markdown:
                return f"```json\n{text}\n```"
            return text

        prompt = dedent(f"""
Extract information according to this schema:

Required Output Structure:
{self.get_schema_description()}

Your task:
1. Extract the relevant information from the provided text
2. Format it exactly according to the schema above
3. Return the output ONLY as valid JSON. IMPORTANT NOTE: All double quotes must be escaped with a SINGLE backslash, not double backslash.
4. Ensure all fields are included
5. If a field is nullable, the information may not be present in the provided text. In this case, the value of the field should be null.
6. If a field is non-nullable, it MUST NOT be null
7. Use strings for text, numbers for numeric values, and booleans (true/false) as specified
{include_markdown_instructions}
""").strip()

        # Add input-output examples if provided
        if examples:
            example_texts = []
            for i, (input_text, output_json) in enumerate(examples[:3], 1):  # Limit to 3 examples
                # Ensure proper JSON formatting of output and escape quotes
                formatted_output = format_as_markdown(json.dumps(output_json, indent=2))
                # Escape single quotes in input text
                example_text = dedent(f"""
Example {i} Input:
{input_text}

Example {i} Output:
{formatted_output}
""").strip()
                example_texts.append(example_text)

            prompt += "\n\nExtraction Examples:\n" + "\n\n".join(example_texts)

        return prompt.replace("'", "\\'").replace('"', '\\"')
