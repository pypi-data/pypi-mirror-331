import logging
import re
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from pydantic import BaseModel, Field, create_model

from zmp_zcp_toolkit.openapi.fastapi_models import (
    OpenAPI,
    Operation,
    Parameter,
    ParameterInType,
    PathItem,
    Reference,
    Schema,
    SchemaOrBool,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SchemaType(Enum):
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    NULL = "null"


class ZmpOpenAPI(OpenAPI):
    """ZmpOpenAPI is a subclass of OpenAPI"""

    @classmethod
    def from_spec_file(cls, file_path: str | Path):
        """
        Load OpenAPI from file.

        Args:
            file_path (str | Path): File path.

        Returns:
            ZmpOpenAPI: ZmpOpenAPI instance.
        """
        with open(file_path, "r") as file:
            openapi = cls.model_validate_json(file.read())

            # convert paths to PathItem enforced
            if openapi.paths:
                converted_paths = {}
                for path, path_item in openapi.paths.items():
                    if isinstance(path_item, dict):
                        converted_paths[path] = PathItem.model_validate(path_item)
                    else:
                        converted_paths[path] = path_item
                openapi.paths.update(converted_paths)

            return openapi

    def generate_models_by_path_and_method(
        self,
        *,
        path: str,
        method: str,
    ) -> Tuple[Optional[BaseModel], Optional[BaseModel], Optional[BaseModel]]:
        """
        Generate parameter models from operation.

        Returns:
            Tuple[BaseModel, BaseModel, BaseModel]: Tuple of parameter models.
                First element is query parameter model.
                Second element is path parameter model.
                Third element is request body model.
        """
        operation = self.get_operation_by_path_method(path=path, method=method)

        query_parameter_model = None
        path_parameter_model = None
        request_body_model = None

        query_parameters = []
        path_parameters = []

        if operation.parameters:
            for parameter in operation.parameters:
                if parameter.in_ is ParameterInType.query:
                    query_parameters.append(parameter)
                elif parameter.in_ is ParameterInType.path:
                    path_parameters.append(parameter)

        if len(query_parameters) > 0:
            query_parameter_model = self._generate_model_from_parameters(
                path=path,
                method=method,
                parameters=query_parameters,
                parameter_in_type=ParameterInType.query,
            )
        else:
            query_parameter_model = None

        if len(path_parameters) > 0:
            path_parameter_model = self._generate_model_from_parameters(
                path=path,
                method=method,
                parameters=path_parameters,
                parameter_in_type=ParameterInType.path,
            )
        else:
            path_parameter_model = None

        if operation.requestBody:
            ref = operation.requestBody.content["application/json"].schema_.ref
            if ref:
                component_schema = self._get_component_schema_by_ref(ref=ref)
                request_body_model = self._generate_model_from_component_schema(
                    schema_=component_schema
                )
            else:
                request_body_model = None
        else:
            request_body_model = None

        return query_parameter_model, path_parameter_model, request_body_model

    def get_operation_by_path_method(self, *, path: str, method: str) -> Operation:
        """Get operation from path.

        Args:
            path (str): Path.

        Returns:
            Operation: Operation.
        """
        method = method.lower()

        logger.debug(f"path: {path}, method: {method}")
        path_item = self.paths[path]

        if path_item is None:
            raise ValueError(f"Path {path} not found")

        logger.debug(
            f"path_item ::\n{path}: {path_item.model_dump_json(indent=4, exclude_none=True)}"
        )

        operation = None
        if isinstance(path_item, PathItem):
            if hasattr(path_item, method):
                operation = getattr(path_item, method)
                if operation is None:
                    raise ValueError(f"Method {method} not found in path {path}")
            else:
                raise ValueError(f"Method {method} not found in path {path}")
        else:
            raise ValueError(f"Path item {path_item} is not a PathItem")

        logger.debug(
            f"operation ::\n{method}: {operation.model_dump_json(indent=4, exclude_none=True)}"
        )

        return operation

    def _generate_model_from_parameters(
        self,
        *,
        path: str,
        method: str,
        parameter_in_type: ParameterInType,
        parameters: Optional[List[Union[Parameter, Reference]]],
    ) -> Optional[Type[BaseModel]]:
        """
        Generate model from parameters.

        Args:
            operation_id (str): Operation ID.
            parameter_in_type (ParameterInType): Parameter in type.
                Can be query, path, header, cookie.
            parameters (Optional[List[Union[Parameter, Reference]]]): Parameters.

        Returns:
            Type[BaseModel]: Generated model.
                If parameter_in_type is query, the model is query parameter model.
                If parameter_in_type is path, the model is path parameter model.
        """
        if parameters is None:
            return None

        if len(parameters) == 0:
            return None

        fields = {}
        for parameter in parameters:
            logger.debug(
                f"parameter: {parameter.model_dump_json(indent=4, exclude_none=True)}"
            )

            if isinstance(parameter, Reference):
                ...  # don't support reference
            else:
                field_name = parameter.name
                fields[field_name] = self._make_field_from_parameter(
                    parameter=parameter
                )
                logger.debug(f"field_name: {field_name}")
                logger.debug(f"field: {fields[field_name]}")

        replaced_path = re.sub(r"[/{}_]", "-", path)  # remove path params brackets
        model_name = "".join(word.capitalize() for word in replaced_path.split("-"))
        model_name = f"{model_name}{parameter_in_type.value.capitalize()}Parameters"

        logger.debug(f"model_name: {model_name} will be created")

        return create_model(model_name, **fields)

    def _make_field_from_parameter(
        self,
        *,
        parameter: Parameter,
    ) -> Tuple[Type[Any], Field]:
        """
        Make field from parameter.

        Args:
            parameter_in_type (ParameterInType): Parameter in type.
            parameter (Parameter): Parameter.

        Returns:
            Tuple[Any, Field]: Tuple of field type and field.
        """

        logger.debug(f"parameter: {parameter}")

        # This schema is the schema of the parameter
        field_schema: Schema = parameter.schema_
        field_type = self._get_field_type_from_schema(schema_=field_schema)

        field = self._make_field_from_schema(
            schema_=field_schema, required=parameter.required
        )

        logger.debug(f"field_type: {field_type}")
        logger.debug(f"field: {field}")

        return (field_type, field)

    def _get_field_type_from_schema(
        self,
        *,
        schema_: Schema,
    ) -> Type[Any]:
        """Get field type from schema.

        Args:
            schema_ (Schema): Schema.

        Returns:
            Type[Any]: Field type.
        """
        logger.debug(f"schema_.type: {schema_.type}")

        field_type = None
        if schema_.type == SchemaType.STRING.value:
            field_type = str
        elif schema_.type == SchemaType.NUMBER.value:
            field_type = float
        elif schema_.type == SchemaType.INTEGER.value:
            field_type = int
        elif schema_.type == SchemaType.BOOLEAN.value:
            field_type = bool
        elif schema_.type == SchemaType.OBJECT.value:
            if schema_.additionalProperties:
                if schema_.additionalProperties.type:
                    field_type = dict[str, schema_.additionalProperties.type]
                else:
                    field_type = dict
            else:
                field_type = dict
        elif schema_.type == SchemaType.ARRAY.value:
            if schema_.items:
                if schema_.items.type:
                    if schema_.items.type == SchemaType.STRING.value:
                        field_type = list[str]
                    elif schema_.items.type == SchemaType.INTEGER.value:
                        field_type = list[int]
                    elif schema_.items.type == SchemaType.NUMBER.value:
                        field_type = list[float]
                    elif schema_.items.type == SchemaType.BOOLEAN.value:
                        field_type = list[bool]
                    elif schema_.items.type == SchemaType.OBJECT.value:
                        # TODO: check if the additionalProperties is exist or not
                        field_type = list[dict]
                    else:
                        raise ValueError(
                            f"Unsupported array item type: {schema_.items.type}"
                        )
                else:
                    if schema_.items.ref:
                        component_schema = self._get_component_schema_by_ref(
                            ref=schema_.items.ref
                        )
                        model_ = self._generate_model_from_component_schema(
                            schema_=component_schema
                        )

                        logger.debug(f"model_: {model_}")
                        logger.debug(f"type(model_): {type(model_)}")

                        field_type = list[model_]

                        # Append enum items into the description for LLM
                        # TODO: refactor this in another function
                        if isinstance(model_, type(Enum)):
                            schema_.description = (
                                f"{schema_.description}"
                                f". Values are {', '.join(v.value for v in model_)}"
                            )
                    else:
                        logger.warning(
                            f"Unsupported array type because of ref is not found: {schema_.items}"
                        )
                        field_type = Any
            else:
                logger.warning(f"Type is array but items is not found: {schema_.items}")
                field_type = Any
        else:
            field_type = self._get_field_type_from_none_type_schema(schema_=schema_)

        return field_type

    def _get_field_type_from_none_type_schema(
        self,
        *,
        schema_: Schema,
    ) -> Type[Any]:
        """Get field type from none schema.

        Args:
            schema_ (Schema): Schema.

        Returns:
            Type[Any]: Field type.
        """
        if schema_.type is not None:
            raise ValueError(f"Schema has type: {schema_.type}")

        all_of: List[SchemaOrBool] = schema_.allOf
        one_of: List[SchemaOrBool] = schema_.oneOf
        any_of: List[SchemaOrBool] = schema_.anyOf
        ref: str = schema_.ref

        if any_of:
            types = []
            for f_schema in any_of:
                # This is the schema of the parameter's schema (anyOf)
                if isinstance(f_schema, Schema):
                    f_type = self._get_field_type_from_schema(schema_=f_schema)
                    types.append(f_type)

                    # Extract other properties from f_schema and send to parent schema
                    # format, maxLength, minLength, pattern, etc.
                    for field_name, field_value in f_schema.model_dump(
                        exclude_none=True
                    ).items():
                        setattr(schema_, field_name, field_value)

            if len(types) == 0:
                field_type = Any
            elif len(types) == 1:
                field_type = types[0]
            else:
                field_type = Union[tuple(types)]
        elif one_of:
            # TODO: support oneOf, check using the real example
            ...
        elif all_of:
            types = []
            for f_schema in all_of:
                # This is the schema of the parameter's schema (allOf)
                if isinstance(f_schema, Schema):
                    if f_schema.type is not None:
                        raise ValueError(f"Schema has type: {f_schema.type}")
                    else:
                        component_schema = self._get_component_schema_by_ref(
                            ref=f_schema.ref
                        )
                        model_ = self._generate_model_from_component_schema(
                            schema_=component_schema
                        )

                        logger.debug(f"model_: {model_}")
                        logger.debug(f"type(model_): {type(model_)}")

                        types.append(model_)

                        # Append enum items into the description for LLM
                        if isinstance(model_, type(Enum)):
                            schema_.description = (
                                f"{schema_.description}"
                                f". Values are {', '.join(v.value for v in model_)}"
                            )
                else:
                    raise ValueError(f"Unsupported schema type: {type(f_schema)}")

            if len(types) == 0:
                field_type = Any
            elif len(types) == 1:
                field_type = types[0]
            else:
                field_type = Union[tuple(types)]
        elif ref:
            component_schema = self._get_component_schema_by_ref(ref=ref)
            model_ = self._generate_model_from_component_schema(
                schema_=component_schema
            )

            logger.warn(f"model_: {model_}")
            logger.debug(f"type(model_): {type(model_)}")

            # Append enum items into the description for LLM
            if isinstance(model_, type(Enum)):
                schema_.description = (
                    f"{schema_.description}"
                    f". Values are {', '.join(v.value for v in model_)}"
                )

            field_type = model_
        else:
            field_type = None

        return field_type

    def _make_field_from_schema(
        self,
        *,
        schema_: Schema,
        required: bool,
    ) -> Field:
        """
        Make field from schema.

        Args:
            schema_ (Schema): Schema.
            required (bool): Required.

        Returns:
            Field: Field of pydantic.
        """
        field = Field(
            default=schema_.default if not required else ...,
            title=schema_.title,
            description=schema_.description,
            min_length=schema_.minLength,
            max_length=schema_.maxLength,
            pattern=schema_.pattern,
            max_digits=schema_.maximum,
            lt=schema_.exclusiveMaximum,
            lte=schema_.maximum,
            gt=schema_.exclusiveMinimum,
            gte=schema_.minimum,
        )

        logger.debug(f"field from schema: {field}")

        return field

    def _get_component_schema_by_ref(self, *, ref: str) -> Optional[Schema]:
        """Get component schema from reference.

        Args:
            ref (str): Reference.

        Returns:
            Schema: Component schema.
        """
        ref = ref.replace("#/components/schemas/", "")

        if ref in self.components.schemas:
            return self.components.schemas[ref]
        else:
            logger.warning(f"Component schema not found: {ref}")
            return None

    def _generate_model_from_component_schema(
        self,
        *,
        schema_: Schema,
    ) -> Optional[Union[Type[Enum], Type[BaseModel]]]:
        """
        Generate model from component schema.

        Args:
            schema_ (Schema): Component schema.

        Raises:
            ValueError: Unsupported schema type.

        Returns:
            Type[BaseModel]: Generated model.
        """
        type_ = schema_.type

        if type_ == SchemaType.STRING.value:
            # for enum
            enum_: List[str] = schema_.enum
            if len(enum_) > 0:
                return Enum(schema_.title, {v: v for v in enum_})
            else:
                raise ValueError(f"Enum is not found: {schema_.title}")
        elif type_ == SchemaType.OBJECT.value:
            # for object
            if schema_.properties:
                return self._generate_model_from_properties(
                    class_name=schema_.title,
                    required_fields=schema_.required,
                    properties=schema_.properties,
                )
            else:
                return ValueError(f"Properties is not found: {schema_.title}")
        else:
            raise ValueError(f"Unsupported schema type: {type_}")

    def _generate_model_from_properties(
        self,
        *,
        class_name: str,
        required_fields: List[str],
        properties: Dict[str, Tuple[Type[Any], Field]],
    ) -> Type[BaseModel]:
        """
        Generate model from properties.

        Args:
            properties (Dict[str, Tuple[Type[Any], Field]]): Properties.

        Returns:
            Type[BaseModel]: Generated model.
        """
        fields = {}
        for field_name, field_schema in properties.items():
            if isinstance(field_schema, Schema):
                field_type = self._get_field_type_from_schema(schema_=field_schema)

                required = True if field_name in required_fields else False

                field = self._make_field_from_schema(
                    schema_=field_schema, required=required
                )

                logger.debug(f"field_type: {field_type}")
                logger.debug(f"field: {field}")

                fields[field_name] = (field_type, field)
            else:
                raise ValueError(f"Unsupported schema type: {type(field_schema)}")

        return create_model(class_name, **fields)
