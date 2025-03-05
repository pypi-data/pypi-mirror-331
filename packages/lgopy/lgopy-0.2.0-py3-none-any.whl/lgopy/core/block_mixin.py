import importlib
import inspect
import logging
import sys
import typing
from io import StringIO
from typing import Annotated
from typing import get_args
from typing import get_origin

from pydantic import create_model
from pydantic import Field
from lgopy.utils import extract_imports_for_class, extract_classes_code, format_and_check_code, LibUtils

logger = logging.getLogger(__name__)

class BlockMixin:
    """
    Block mixin class
    """
    @classmethod
    def to_pydantic_model(cls):
        """
        it returns a json schema for the block
        """
        model_fields = {}
        block_init_vars = inspect.signature(cls.__init__).parameters
        for k, v in block_init_vars.items():
            if k == "self":
                continue
            input_annot = v.annotation

            field_default = None if v.default == inspect.Parameter.empty else v.default
            field_description = None
            if input_annot is inspect.Parameter.empty and field_default is None:
                field_type = typing.Any
            elif input_annot is inspect.Parameter.empty:
                field_type = type(field_default)
            else:
                field_type = input_annot
                annot_origin = get_origin(input_annot)
                annot_args = get_args(input_annot)
                if annot_origin is Annotated:
                    field_description = annot_args[1]
            model_fields[k] = (
                field_type,
                Field(field_default, description=field_description),
            )

        output_annot = getattr(cls.call, "__annotations__", {}).get("return", typing.Any)
        output_type = output_annot if output_annot is not inspect.Parameter.empty else typing.Any
        output_type_str = output_type.__name__ if isinstance(output_type, type) else str(output_type)

        model_desc = cls.__dict__.get("description", None)
        model_title = cls.__name__
        model_args = {**model_fields,
                      **{"__doc__": model_desc},
                        **{"__config__": type("Config", (), {
                            "json_schema_extra": {
                                "category": cls.__dict__.get("category", None),
                                "display_name": cls.__dict__.get("display_name", None),
                                "output_type": output_type_str
                            }
                        })}
                      }

        return create_model(model_title, **model_args)


    @classmethod
    def build(cls):
        """
        it builds the block
        """

        class_file_path = inspect.getfile(cls)
        class_name = cls.__name__
        logger.info(f"Building block: {class_name} from {class_file_path}")

        with open(class_file_path, "r") as file:
            source_code = file.read()
        class_code_dict = extract_classes_code(source_code)

        with StringIO() as source_io:
            class_code = class_code_dict.get(cls.__name__, None)
            assert class_code, f"Class {cls.__name__} not found in the source code"
            used_imports = extract_imports_for_class(source_code, cls.__name__)
            if used_imports:
                for import_statement in used_imports:
                    source_io.write(f"{import_statement}\n")

            source_io.write(f"\n\n{class_code}")
            output = format_and_check_code(source_io.getvalue())
            formatted_code = output.pop("formatted_code")

        lib_home = LibUtils.get_lib_home()
        block_folder = lib_home / "blocks" / cls.__name__
        block_folder.mkdir(parents=True, exist_ok=True)

        block_file = block_folder / "block.py"
        with open(block_file, "w") as file:
            file.write(formatted_code)

        with open(block_folder / "__init__.py", "w") as file:
            file.write(f"from .block import {cls.__name__}")

        logger.info(f"Block {cls.__name__} built at {block_folder}")

        # load module
        block_module = cls.__name__
        block_module_path = block_folder / "block.py"
        block_module_spec = importlib.util.spec_from_file_location(block_module, block_module_path)
        block_module = importlib.util.module_from_spec(block_module_spec)
        #sys.modules[block_module] = block_module
        block_module_spec.loader.exec_module(block_module)
        block_cls = getattr(block_module, cls.__name__)
        return block_cls

    def to_dict(self):
        """
        it returns a json schema for the block
        """
        pydantic_model = self.to_pydantic_model()
        model = pydantic_model(**self.__dict__)
        return model.model_dump( exclude_none=True, exclude_unset=True)





