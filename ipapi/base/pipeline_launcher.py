import os
import json
from typing import Union
import logging
from timeit import default_timer as timer
import random

import pandas as pd
from ipapi.database.base import DbInfo
import tqdm

import ipapi.database.base as dbb
import ipapi.database.db_factory as dbf
from ipapi.tools.common_functions import force_directories, format_time
from ipapi.base.pipeline_processor import PipelineProcessor
from ipapi.base.ipt_loose_pipeline import LoosePipeline
from ipapi.file_handlers.fh_base import file_handler_factory


logger = logging.getLogger(__name__)

IS_LOG_DATA = True
IS_USE_MULTI_THREAD = True


def save_state(
    output_folder: str,
    csv_file_name: str,
    overwrite_existing: bool,
    sub_folder_name: str,
    append_time_stamp: bool,
    script,
    generate_series_id: bool,
    series_id_time_delta: int,
    images: list,
    database_data=None,
    thread_count: int = 1,
    build_annotation_csv: bool = False,
) -> dict:
    return dict(
        output_folder=output_folder,
        csv_file_name=csv_file_name,
        overwrite_existing=overwrite_existing,
        sub_folder_name=sub_folder_name,
        append_time_stamp=append_time_stamp,
        script=script,
        generate_series_id=generate_series_id,
        series_id_time_delta=series_id_time_delta,
        images=images,
        thread_count=thread_count,
        database_data=database_data,
        build_annotation_csv=build_annotation_csv,
    )


def restore_state(blob: Union[str, dict, None], overrides: dict = {}) -> dict:
    # Attempt to load state
    if isinstance(blob, str) and os.path.isfile(blob):
        with open(blob, "r") as f:
            res = json.load(f)
    elif isinstance(blob, dict):
        res = blob
    else:
        res = {}

    # Handle legacy states
    dataframe = res.pop("data_frame", None)
    if dataframe is not None:
        res["images"] = list(dataframe["FilePath"])
    sf = res.pop("append_experience_name", None)
    if sf is not None:
        res["sub_folder_name"] = sf

    def _get_key(key, main_dict, overrides_dict, default=None):
        if overrides_dict.get(key, None) is not None:
            return overrides_dict[key]
        elif key in main_dict:
            return main_dict[key]
        else:
            return default

    # Build state dictionnary with overrides
    return dict(
        output_folder=_get_key("output_folder", res, overrides),
        csv_file_name=_get_key("csv_file_name", res, overrides),
        overwrite_existing=_get_key("overwrite_existing", res, overrides, False),
        sub_folder_name=_get_key("sub_folder_name", res, overrides, ""),
        append_time_stamp=_get_key("append_time_stamp", res, overrides, False),
        script=_get_key("script", res, overrides),
        generate_series_id=_get_key("generate_series_id", res, overrides, False),
        series_id_time_delta=_get_key("series_id_time_delta", res, overrides, 0),
        images=_get_key("images", res, overrides),
        database_data=_get_key("database_data", res, overrides),
        thread_count=_get_key("thread_count", res, overrides, 1),
        included=_get_key("included", res, overrides, []),
        excluded=_get_key("excluded", res, overrides, []),
        overwrite=_get_key("overwrite", res, overrides, False),
        build_annotation_csv=_get_key("build_annotation_csv", res, overrides, False),
        database=_get_key("database", res, overrides, ""),
        experiment=_get_key("experiment", res, overrides, ""),
        randomize=_get_key("randomize", res, overrides, False),
    )


def launch(**kwargs):
    start = timer()

    # Script
    script = kwargs.get("script", None)
    if script is not None and os.path.isfile(script):
        with open(script, "r") as f:
            script = json.load(f)
    kwargs["script"] = script

    # Image(s)
    image = kwargs.get("image", None)
    images = kwargs.get("images", None)
    if image is not None and images is not None:
        kwargs["images"] = images + [image]
    elif image is None and images is not None:
        kwargs["images"] = images
    elif image is not None and images is None:
        kwargs["images"] = [image]

    # State
    stored_state = kwargs.pop("stored_state", None)

    res = restore_state(blob=stored_state, overrides=kwargs)

    def exit_error_message(msg: str) -> None:
        logger.error(msg)

    # Retrieve images
    image_list_ = res.get("images", None)

    # Build database
    db_data = res.get("database_data", None)
    if db_data is None:
        database = res.get("database", None)
        experiment = res.get("experiment", None)
        if database is None or experiment is None:
            db = None
        else:
            db = dbf.db_info_to_database(
                DbInfo(
                    display_name=experiment,
                    target=database,
                    dbms="pandas",
                )
            )
            if "sub_folder_name" not in res or not res["sub_folder_name"]:
                res["sub_folder_name"] = experiment
            if "csv_file_name" not in res or not res["csv_file_name"]:
                res["csv_file_name"] = f"{experiment.lower()}_raw_data"
    else:
        db = dbf.db_info_to_database(dbb.DbInfo(**db_data))

    # Retrieve output folder
    output_folder_ = res.get("output_folder", None)
    if not output_folder_:
        exit_error_message("Missing output folder")
        return 1
    elif res.get("sub_folder_name", ""):
        output_folder_ = os.path.join(output_folder_, res["sub_folder_name"], "")
    else:
        output_folder_ = os.path.join(output_folder_, "")
    force_directories(output_folder_)
    csv_file_name = res.get("csv_file_name", None)
    if not csv_file_name:
        exit_error_message("Missing output file name")
        return 1
    if IS_USE_MULTI_THREAD and "thread_count" in res:
        try:
            mpc = int(res["thread_count"])
        except Exception as e:
            mpc = False
    else:
        mpc = False

    try:
        if isinstance(res["script"], str) and os.path.isfile(res["script"]):
            script = LoosePipeline.load(res["script"])
        elif isinstance(res["script"], dict):
            script = LoosePipeline.from_json(json_data=res["script"])
        else:
            exit_error_message("Failed to load script: Unknown error")
            return 1
    except Exception as e:
        exit_error_message(f"Failed to load script: {repr(e)}")
        return 1

    # Build pipeline processor
    pp = PipelineProcessor(
        database=db.copy(),
        dst_path=output_folder_,
        overwrite=res["overwrite_existing"],
        seed_output=res["append_time_stamp"],
        group_by_series=res["generate_series_id"],
        store_images=False,
    )
    if not image_list_:
        pp.grab_files_from_data_base(
            experiment=db.db_info.display_name.lower(),
            **db.main_selector,
        )
    else:
        pp.accepted_files = image_list_

    if res.get("randomize", False) is True:
        random.shuffle(pp.accepted_files)

    logger.info("Process summary")
    logger.info("_______________")
    logger.info(f'database: {res.get("database_data", None)}')
    logger.info(f'Output folder: {res["output_folder"]}')
    logger.info(f'CSV file name: {res["csv_file_name"]}')
    logger.info(f'Overwrite data: {res["overwrite_existing"]}')
    logger.info(f'Subfolder name: {res["sub_folder_name"]}')
    logger.info(f'Append timestamp to root folder: {res["append_time_stamp"]}')
    logger.info(f'Generate series ID: {res["generate_series_id"]}')
    logger.info(f'Series ID time delta allowed: {res["series_id_time_delta"]}')
    logger.info(f'Build annotation ready CSV: {res["build_annotation_csv"]}')
    logger.info(f"Images: {len(pp.accepted_files)}")
    logger.info(f"Concurrent processes count: {mpc}")
    logger.info(f"Script summary: {str(script)}")

    if pp.accepted_files is None or len(pp.accepted_files) < 1:
        exit_error_message("No images to process")
        return 1

    pp.progress_callback = kwargs.get("progress_callback", None)
    pp.error_callback = kwargs.get("error_callback", None)
    pp.ensure_root_output_folder()

    pp.script = script
    if not pp.accepted_files:
        logger.error("Nothing to precess")
        return 1

    # Process data
    groups_to_process = pp.prepare_groups(res["series_id_time_delta"])
    if res["build_annotation_csv"]:
        try:
            if pp.options.group_by_series:
                files, luids = map(list, zip(*groups_to_process))
                wrappers = [
                    file_handler_factory(files[i], db)
                    for i in [luids.index(x) for x in set(luids)]
                ]
            else:
                wrappers = [
                    file_handler_factory(f, db)
                    for f in tqdm.tqdm(groups_to_process, desc="Building annotation CSV")
                ]
            pd.DataFrame.from_dict(
                {
                    "plant": [i.plant for i in wrappers],
                    "date_time": [i.date_time for i in wrappers],
                    "disease_index": "",
                }
            ).sort_values(
                by=["plant", "date_time"], axis=0, na_position="first", ascending=True
            ).to_csv(
                os.path.join(pp.options.dst_path, f"{csv_file_name}_diseaseindex.csv"),
                index=False,
            )
        except Exception as e:
            preffix = "FAIL"
            logger.exception("Unable to build disease index file")
        else:
            preffix = "SUCCESS"
            logger.info("Built disease index file")
        print(f"{preffix} - Disease index file")

    groups_to_process_count = len(groups_to_process)
    if groups_to_process_count > 0:
        pp.multi_thread = mpc
        pp.process_groups(groups_list=groups_to_process)

    # Merge dataframe
    pp.merge_result_files(csv_file_name=csv_file_name + ".csv")
    logger.info(
        f"Processed {groups_to_process_count} groups/images in {format_time(timer() - start)}"
    )

    # Build videos

    print("Done, see logs for more details")

    return 0
