from collections import defaultdict
import copy
from dataclasses import fields, is_dataclass
import json
import logging
from pathlib import Path
import re
from typing import Optional, Type, TypeVar, List, Dict
from nemo_library.features.focus import focusMoveAttributeBefore
from nemo_library.features.projects import (
    FilterType,
    deserializeMetaDataObject,
    createApplications,
    createAttributeGroups,
    createDefinedColumns,
    createDiagrams,
    createMetrics,
    createPages,
    createReports,
    createTiles,
    deleteApplications,
    deleteAttributeGroups,
    deleteDefinedColumns,
    deleteDiagrams,
    deleteMetrics,
    deletePages,
    deleteReports,
    deleteTiles,
    getApplications,
    getAttributeGroups,
    getDefinedColumns,
    getDiagrams,
    getImportedColumns,
    getMetrics,
    getPages,
    getReports,
    getTiles,
)
from nemo_library.model.application import Application
from nemo_library.model.attribute_group import AttributeGroup
from nemo_library.model.defined_column import DefinedColumn
from nemo_library.model.diagram import Diagram
from nemo_library.model.metric import Metric
from nemo_library.model.pages import Page
from nemo_library.model.report import Report
from nemo_library.model.tile import Tile
from nemo_library.utils.config import Config

__all__ = ["MetaDataLoad", "MetaDataCreate"]

T = TypeVar("T")


def MetaDataLoad(
    config: Config,
    projectname: str,
) -> None:

    functions = {
        "definedcolumns": getDefinedColumns,
        "metrics": getMetrics,
        "attributegroups": getAttributeGroups,
        "pages": getPages,
        "applications": getApplications,
        "diagrams": getDiagrams,
        "reports": getReports,
    }

    for name, func in functions.items():
        data = func(
            config=config,
            projectname=projectname,
            filter="(Conservative)",
            filter_type=FilterType.STARTSWITH,
        )

        if name == "attributegroups":
            hierarchy, _ = _attribute_groups_build_hierarchy(data)
            data = attribute_groups_sort_hierarchy(hierarchy, root_key=None)

        _export_data_to_json(config, name, data)


def _attribute_groups_build_hierarchy(attribute_groups):
    hierarchy = defaultdict(list)
    group_dict = {group.internalName: group for group in attribute_groups}

    for group in attribute_groups:
        parent_name = group.parentAttributeGroupInternalName
        hierarchy[parent_name].append(group)

    return hierarchy, group_dict


def attribute_groups_sort_hierarchy(hierarchy, root_key=None):
    sorted_list = []

    def add_children(parent):
        for child in sorted(hierarchy.get(parent, []), key=lambda x: x.displayName):
            sorted_list.append(child)
            add_children(child.internalName)

    add_children(root_key)
    return sorted_list


def MetaDataCreate(
    config: Config,
    projectname: str,
) -> None:

    # load data from model and nemo
    (
        definedcolumns_model,
        metrics_model,
        attributegroups_model,
        tiles_model,
        pages_model,
        applications_model,
        diagrams_model,
        reports_model,
    ) = _load_model_from_json(config=config)

    (
        definedcolumns_nemo,
        metrics_nemo,
        attributegroups_nemo,
        tiles_nemo,
        pages_nemo,
        applications_nemo,
        diagrams_nemo,
        reports_nemo,
    ) = _load_model_from_nemo(config=config, projectname=projectname)

    # reconcile data
    new_objects_found = _reconcile_model_and_nemo(
        config=config,
        projectname=projectname,
        definedcolumns_model=definedcolumns_model,
        metrics_model=metrics_model,
        attributegroups_model=attributegroups_model,
        tiles_model=tiles_model,
        pages_model=pages_model,
        applications_model=applications_model,
        diagrams_model=diagrams_model,
        reports_model=reports_model,
        definedcolumns_nemo=definedcolumns_nemo,
        metrics_nemo=metrics_nemo,
        tiles_nemo=tiles_nemo,
        attributegroups_nemo=attributegroups_nemo,
        pages_nemo=pages_nemo,
        applications_nemo=applications_nemo,
        diagrams_nemo=diagrams_nemo,
        reports_nemo=reports_nemo,
    )

    # move attributes and groups
    if new_objects_found:
        _move_objects_in_focus(
            config=config,
            projectname=projectname,
            defined_columns=definedcolumns_model,
            metrics=metrics_model,
            attribute_groups=attributegroups_model,
        )


def _load_model_from_json(config: Config) -> (
    List[DefinedColumn],
    List[Metric],
    List[AttributeGroup],
    List[Tile],
    List[Page],
    List[Application],
    List[Diagram],
    List[Report],
):  # type: ignore
    definedcolumns_model = _load_data_from_json(config, "definedcolumns", DefinedColumn)
    metrics_model = _load_data_from_json(config, "metrics", Metric)
    attributegroups_model = _load_data_from_json(
        config, "attributegroups", AttributeGroup
    )
    pages_model = _load_data_from_json(config, "pages", Page)
    applications_model = _load_data_from_json(config, "applications", Application)
    diagrams_model = _load_data_from_json(config, "diagrams", Diagram)
    tiles_model = _generate_tiles(metrics_model)
    reports_model = _load_data_from_json(config, "reports", Report)

    return (
        definedcolumns_model,
        metrics_model,
        attributegroups_model,
        tiles_model,
        pages_model,
        applications_model,
        diagrams_model,
        reports_model,
    )


def _fetch_data(func, **kwargs):
    return func(**kwargs)


def _load_model_from_nemo(config: Config, projectname: str) -> (
    List[DefinedColumn],
    List[Metric],
    List[AttributeGroup],
    List[Tile],
    List[Page],
    List[Application],
    List[Diagram],
):  # type: ignore

    def fetchData(config: Config, projectname: str, func):
        return func(
            config=config,
            projectname=projectname,
            filter="(Conservative)",
            filter_type=FilterType.STARTSWITH,
        )

    definedcolumns_nemo = fetchData(config, projectname, getDefinedColumns)
    metrics_nemo = fetchData(config, projectname, getMetrics)
    tiles_nemo = fetchData(config, projectname, getTiles)
    attributegroups_nemo = fetchData(config, projectname, getAttributeGroups)
    pages_nemo = fetchData(config, projectname, getPages)
    applications_nemo = fetchData(config, projectname, getApplications)
    diagrams_nemo = fetchData(config, projectname, getDiagrams)
    reports_nemo = fetchData(config, projectname, getReports)

    return (
        definedcolumns_nemo,
        metrics_nemo,
        attributegroups_nemo,
        tiles_nemo,
        pages_nemo,
        applications_nemo,
        diagrams_nemo,
        reports_nemo,
    )


def _load_data_from_json(config, file: str, cls: Type[T]) -> List[T]:
    """
    Loads JSON data from a file and converts it into a list of DataClass instances,
    handling nested structures recursively.
    """
    path = Path(config.get_metadata()) / f"{file}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [deserializeMetaDataObject(item, cls) for item in data]


def _generate_tiles(metrics: List[Metric]) -> List[Tile]:
    tiles = [
        Tile(
            aggregation="Mean",
            description=f"Tile for metric {metric.displayName}",
            descriptionTranslations={},
            displayName=metric.displayName,
            displayNameTranslations={},
            frequency="Month",
            graphic="",
            internalName=metric.internalName,
            status="Mandatory",
            tileGroup="(Conservative)",
            tileGroupTranslations={},
            tileSourceID=metric.id,
            tileSourceInternalName=metric.internalName,
            type="Metric",
            unit="",
            id="",
            projectId="",
            tenant="",
        )
        for metric in metrics
    ]

    return tiles


def _reconcile_model_and_nemo(
    config: Config,
    projectname: str,
    definedcolumns_model: List[DefinedColumn],
    metrics_model: List[Metric],
    attributegroups_model: List[AttributeGroup],
    tiles_model: List[Tile],
    pages_model: List[Page],
    applications_model: List[Application],
    diagrams_model: List[Diagram],
    reports_model: List[Report],
    definedcolumns_nemo: List[DefinedColumn],
    metrics_nemo: List[Metric],
    tiles_nemo: List[Tile],
    attributegroups_nemo: List[AttributeGroup],
    pages_nemo: List[Page],
    applications_nemo: List[Application],
    diagrams_nemo: List[Diagram],
    reports_nemo: List[Report],
) -> bool:
    def find_deletions(model_list: List[T], nemo_list: List[T]) -> List[T]:
        model_keys = {obj.internalName for obj in model_list}
        return [obj for obj in nemo_list if obj.internalName not in model_keys]

    def find_updates(model_list: List[T], nemo_list: List[T]) -> List[T]:
        updates = []
        nemo_dict = {getattr(obj, "internalName"): obj for obj in nemo_list}
        for model_obj in model_list:
            key = getattr(model_obj, "internalName")
            if key in nemo_dict:
                nemo_obj = nemo_dict[key]
                if is_dataclass(model_obj) and is_dataclass(nemo_obj):
                    differences = {
                        attr.name: (
                            getattr(model_obj, attr.name),
                            getattr(nemo_obj, attr.name),
                        )
                        for attr in fields(model_obj)
                        if getattr(model_obj, attr.name) != getattr(nemo_obj, attr.name)
                    }

                if differences:
                    for attrname, (old_value, new_value) in differences.items():
                        logging.info(f"{attrname}: {old_value} --> {new_value}")
                    updates.append(model_obj)

        return updates

    def find_new_objects(model_list: List[T], nemo_list: List[T]) -> List[T]:
        nemo_keys = {getattr(obj, "internalName") for obj in nemo_list}
        return [
            obj for obj in model_list if getattr(obj, "internalName") not in nemo_keys
        ]

    deletions: Dict[str, List[T]] = {}
    updates: Dict[str, List[T]] = {}
    creates: Dict[str, List[T]] = {}

    for key, model_list, nemo_list in [
        ("definedcolumns", definedcolumns_model, definedcolumns_nemo),
        ("metrics", metrics_model, metrics_nemo),
        ("tiles", tiles_model, tiles_nemo),
        ("attributegroups", attributegroups_model, attributegroups_nemo),
        ("applications", applications_model, applications_nemo),
        ("pages", pages_model, pages_nemo),
        ("diagrams", diagrams_model, diagrams_nemo),
        ("reports", reports_model, reports_nemo),
    ]:
        nemo_list_cleaned = copy.deepcopy(nemo_list)
        nemo_list_cleaned = _clean_fields(nemo_list_cleaned)

        deletions[key] = find_deletions(model_list, nemo_list)
        updates[key] = find_updates(model_list, nemo_list_cleaned)
        creates[key] = find_new_objects(model_list, nemo_list)

    # Start with deletions
    delete_functions = {
        "applications": deleteApplications,
        "pages": deletePages,
        "tiles": deleteTiles,
        "metrics": deleteMetrics,
        "definedcolumns": deleteDefinedColumns,
        "attributegroups": deleteAttributeGroups,
        "diagrams": deleteDiagrams,
        "reports": deleteReports,
    }

    for key, delete_function in delete_functions.items():
        if deletions[key]:
            objects_to_delete = [data_nemo.id for data_nemo in deletions[key]]
            delete_function(config=config, **{key: objects_to_delete})

    # Now do updates and creates in a dedicated order
    create_functions = {
        "attributegroups": createAttributeGroups,
        "definedcolumns": createDefinedColumns,
        "metrics": createMetrics,
        "tiles": createTiles,
        "pages": createPages,
        "applications": createApplications,
        "diagrams": createDiagrams,
        "reports": createReports,
    }

    new_objects = False
    for key, create_function in create_functions.items():
        # create new objects first
        if creates[key]:
            create_function(
                config=config, projectname=projectname, **{key: creates[key]}
            )
            new_objects = True
        # now the changes
        if updates[key]:
            create_function(
                config=config, projectname=projectname, **{key: updates[key]}
            )

    return new_objects


def _export_data_to_json(config: Config, file: str, data):
    data = _clean_fields(data)
    path = Path(config.get_metadata()) / f"{file}.json"
    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            [element.to_dict() for element in data], file, indent=4, ensure_ascii=True
        )


def _clean_fields(data):
    for element in data:
        element.id = ""
        element.tenant = ""
        element.projectId = ""
        element.tileSourceID = ""

        if isinstance(element, Diagram):
            for value in element.values:
                value.id = ""

        elif isinstance(element, Page):
            for visual in element.visuals:
                visual.id = ""

    return data


def _extract_fields(formulas_dict):
    field_pattern = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b")

    extracted_fields = {}

    for key, formulas in formulas_dict.items():
        extracted_fields[key] = set()
        for formula in formulas:
            if isinstance(formula, str) and formula.strip():
                fields = field_pattern.findall(formula)
                extracted_fields[key].update(fields)

    return {k: sorted(v) for k, v in extracted_fields.items()}


def _move_objects_in_focus(
    config: Config,
    projectname: str,
    defined_columns: List[DefinedColumn],
    metrics: List[Metric],
    attribute_groups: List[AttributeGroup],
) -> None:

    # move fields that belong to metrics and defined columns into according groups
    fields = {}
    for defined_column in defined_columns:
        key = defined_column.parentAttributeGroupInternalName
        if key not in fields:
            fields[key] = []
        fields[key].append(defined_column.formula)

    for metric in metrics:
        key = metric.parentAttributeGroupInternalName
        if key not in fields:
            fields[key] = []
        fields[key].append(metric.aggregateBy)
        fields[key].append(metric.dateColumn)
        fields[key].append(metric.groupByColumn)
        for agg in metric.groupByAggregations:
            fields[key].append(agg)

    # extract fields from formulae
    fields_dict = _extract_fields(fields)

    # remove doublicates
    for key in fields:
        fields_dict[key] = list(set(fields_dict[key]))

    # move attributes now
    fields_nemo = getImportedColumns(config=config, projectname=projectname)
    fields_nemo_internal_names = fields_nemo["internalName"].to_list()
    for key, fields in fields_dict.items():
        logging.info(f"group {key}")
        for field in fields:
            if field in fields_nemo_internal_names:
                logging.info(f"move object {field}")
                focusMoveAttributeBefore(
                    config=config,
                    projectname=projectname,
                    sourceInternalName=field,
                    groupInternalName=key,
                )
