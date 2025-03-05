import subprocess
from pylint.lint import Run
import tempfile
import black

def format_and_check_code(source_code: str) -> dict:
    """
    Formats the source code using black, and checks for linting errors and security issues
    :param source_code:
    :return:
    """
    results = {"formatted_code": "", "lint_errors": "", "security_warnings": ""}

    try:
        formatted_code = black.format_str(source_code, mode=black.Mode())
        results["formatted_code"] = formatted_code
    except Exception as e:
        raise RuntimeError(f"Formatting failed: {str(e)}")

    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
        temp_file.write(formatted_code.encode())
        temp_file_path = temp_file.name

    # Lint the code using pylint
    try:
        Run(['--errors-only', temp_file_path], exit=False)
    except Exception as e:
        results["lint_errors"] = f"Linting failed: {str(e)}"

    # Check for security issues using bandit
    try:
        security_result = subprocess.run(
            ["bandit", "-r", temp_file_path],
            capture_output=True,
            text=True,
        )
        results["security_warnings"] = security_result.stdout
    except Exception as e:
        results["security_warnings"] = f"Security check failed: {str(e)}"

    return results
