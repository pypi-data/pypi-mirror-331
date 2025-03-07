import pytest
from unittest.mock import patch, mock_open, MagicMock
from datafact.templates.items import (
    FilenameMapping,
    template_mapping,
    DataFactProjectTemplate,
    render_template,
    Context,
)


def test_filename_mapping_with_target_string():
    mapping = template_mapping(("package", "template.jinja"), "output.txt")
    assert mapping.source == ("package", "template.jinja")
    assert mapping.target == "output.txt"
    assert mapping.target_fn is None


def test_filename_mapping_with_target_callable():
    def target_fn(context: Context):
        return f"{context['name']}.txt"

    mapping = template_mapping(("package", "template.jinja"), target_fn)
    assert mapping.source == ("package", "template.jinja")
    assert mapping.target is None
    assert mapping.target_fn is target_fn


def test_template_mapping_invalid_target():
    with pytest.raises(ValueError, match="target_str_or_fn must be either a string or a callable"):
        template_mapping(("package", "template.jinja"), 42)


@patch("datafact.templates.items.render_template", return_value="rendered content")
@patch("builtins.open", new_callable=mock_open)
def test_datafact_project_template_create(mock_open_file, mock_render_template):
    context = {"name": "test_project"}
    files = [
        FilenameMapping(source=("package", "template1.jinja"), target="file1.txt"),
        FilenameMapping(
            source=("package", "template2.jinja"),
            target_fn=lambda ctx: f"{ctx['name']}_file2.txt"
        ),
    ]
    project = DataFactProjectTemplate(
        name="Test Project",
        description="A test project",
        files=files,
    )

    with patch("datafact.templates.items.resources.open_text",
               mock_open(read_data="template content")) as mock_resources:
        project.create("output_folder", context)

    # Assert the correct number of files were processed
    assert mock_render_template.call_count == 2
    assert mock_open_file.call_count == 2

    # Check file write operations
    mock_open_file.assert_any_call("output_folder/file1.txt", "w")
    mock_open_file.assert_any_call("output_folder/test_project_file2.txt", "w")

    # Check render_template calls
    mock_render_template.assert_any_call("package", "template1.jinja", context)
    mock_render_template.assert_any_call("package", "template2.jinja", context)


@patch("datafact.templates.items.resources.open_text", mock_open(read_data="{{ name }} template content"))
def test_render_template():
    context = {"name": "test_project"}
    result = render_template("package", "template.jinja", context)
    assert result == "test_project template content"
