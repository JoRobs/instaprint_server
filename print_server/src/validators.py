from dataclasses import dataclass, field
from pathlib import Path
from fastapi import UploadFile

@dataclass
class ValidationResult:
  valid: bool = True
  errors: list = field(default_factory=list)


class ImageValidator:
  def __init__(self, max_size: int = 10 * 1024 * 1024):  # 10MB default
    self.max_size = max_size
    self.allowed_extensions = (
      '.png',
      '.jpeg',
      '.jpg',
    )

  async def validate_file(self, file: UploadFile) -> ValidationResult:
    """Check if the image file is valid"""
    result = ValidationResult()

    # Check if user selected a file
    if not file.filename or file.filename.strip() == "":
      result.valid = False
      result.errors.append("No file selected")
      return result

    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in self.allowed_extensions:
      result.valid = False
      result.errors.append(
          f"File extension '{file_ext}' not allowed. Use: {', '.join(self.allowed_extensions[:-1])}, or {self.allowed_extensions[-1]}"
      )

    # Read file to check size
    content = await file.read()
    await file.seek(0)  # Reset file pointer for later use

    # Check file size
    file_size = len(content)
    if file_size > self.max_size:
      result.valid = False
      result.errors.append(
          f"File too large ({file_size:,} bytes). Maximum: {self.max_size:,} bytes"
      )

    return result
