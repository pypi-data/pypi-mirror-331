import json
import logging
import os
import re
import sys
import time
from contextlib import suppress
from datetime import datetime
from itertools import zip_longest
from pathlib import Path

import bson
import numpy as np
from _ctypes import PyObj_FromPtr  # see https://stackoverflow.com/a/15012814/355230
from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table
from tabulate import tabulate

# class NoIndent(object):
# 	""" Value wrapper. """
# 	def __init__(self, value):
# 		if not isinstance(value, (list, tuple)):
# 			raise TypeError('Only lists and tuples can be wrapped')
# 		self.value = value

log = logging.getLogger(__name__)
log.setLevel("INFO")


class MyEncoder(json.JSONEncoder):
    FORMAT_SPEC = "@@{}@@"  # Unique string pattern of NoIndent object ids.
    regex = re.compile(FORMAT_SPEC.format(r"(\d+)"))  # compile(r'@@(\d+)@@')

    def __init__(self, **kwargs):
        # Keyword arguments to ignore when encoding NoIndent wrapped values.
        ignore = {"cls", "indent"}

        # Save copy of any keyword argument values needed for use here.
        self._kwargs = {k: v for k, v in kwargs.items() if k not in ignore}
        super().__init__(**kwargs)

    def default(self, o):
        # return (self.FORMAT_SPEC.format(id(o)) if isinstance(o, NoIndent)
        return (
            self.FORMAT_SPEC.format(id(o))
            if isinstance(o, list)
            else super().default(o)
        )

    def iterencode(self, o, _one_shot=False):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.

        # Replace any marked-up NoIndent wrapped values in the JSON repr
        # with the json.dumps() of the corresponding wrapped Python object.
        for encoded in super().iterencode(o, _one_shot):
            match = self.regex.search(encoded)
            new_encoded = encoded
            if match:
                the_id = int(match.group(1))
                no_indent = PyObj_FromPtr(the_id)
                json_repr = json.dumps(no_indent.value, **self._kwargs)
                # Replace the matched the_id string with json formatted representation
                # of the corresponding Python object.
                new_encoded = encoded.replace(
                    f'"{format_spec.format(the_id)}"', json_repr
                )

            yield new_encoded


def save_dict_list(path, output):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    sorted_output = []
    serial_numbers = []
    isAnalysis = False
    # Separate into separate lists for each chip if saving measurement output
    for out in output:
        if isAnalysis and "passed" not in out:
            log.error(
                "List of dictionaries being saved to output contain both measurement and output formats. Please fix."
            )
            return
        if "passed" in out:  # is analysis output
            sorted_output += [out]
            isAnalysis = True
        elif out.get("serialNumber") in serial_numbers:
            sorted_output[serial_numbers.index(out.get("serialNumber"))] += [out]
        else:
            serial_numbers += [out.get("serialNumber")]
            sorted_output += [[out]]
    with Path(path).open("w", encoding="UTF-8") as fp:
        json.dump(sorted_output, fp, cls=MyEncoder, indent=4)


def load_json(path):
    with Path(path).open(encoding="UTF-8") as serialized:
        inputdata = json.load(serialized)
    alldf = []
    # Can read measurement jsons (nested list) or analysis jsons (1D list)
    for chip in inputdata:
        if isinstance(chip, list):
            for _dict in chip:
                alldf += [outputDataFrame(_dict=_dict)]
        else:
            alldf += [outputDataFrame(_dict=chip)]
    return alldf


def load_iv_alt(path, test_type, input_vdepl):
    ## loads data from sensor IV json format [1], input into non-electric-GUI [2] and output from non-electric-GUI [3]
    ## [1] https://gitlab.cern.ch/atlas-itk/sw/db/production_database_scripts/-/blob/pixel_preproduction_GUI/pixels/sensors_prototype/data/IV_DATA_TILE.json
    ## [2] https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/uploads/b0c6d5edde5514865e27574810a3a449/ivcurve_result_20230403_235249.json
    ## [3] https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-tools/uploads/8dbdc2f81ff479343318dfe25e6ae96d/20UPGXM2000013_MODULE__INITIAL_WARM_IV_MEASURE_2023Y03m27d__04_49_56+0000.json

    qchelper = False
    timestart = None

    with Path(path).open(encoding="utf-8") as serialized:
        if "QCHELPER" in serialized.read():
            qchelper = True
        serialized.seek(0)  ## move cursur back to the beginning of file
        inputdata = json.load(serialized)

    alldf = []
    # Can read one IV measurement in sensor json format at a time
    if not isinstance(inputdata, list):
        inputdata = [inputdata]
        log.info("Found data for one measurement.")
    else:
        log.info("Found data for {%i} measurement(s).", len(inputdata))
        if qchelper:
            log.info("Output format from QC helper/non-electric GUI detected.")

    for item in inputdata:
        module_sn = ""
        test = ""
        institution = ""
        date = ""
        prefix = None
        vdepl = 0
        IV_ARRAY = {}

        iv_array = []

        keys = {
            "component": module_sn,
            "test": test,
            "institution": institution,
            "date": date,
            "prefix": prefix,
            "depletion_voltage": vdepl,
            "IV_ARRAY": IV_ARRAY,
        }

        for key in keys:
            if key not in item and not qchelper:
                log.warning("Key {%s} is missing in the input file!", key)
        if not qchelper:
            if item["component"]:
                module_sn = item["component"]
            else:
                log.error("No module SN found.")
                return None

            if "iv" not in item["test"].lower():
                log.error("No test type found.")
                return None

            try:
                institution = item["institution"]
            except Exception:
                log.warning("No institution found in measurement file!")
                institution = ""

            try:
                if item["date"]:
                    try:
                        timestart = time.mktime(
                            datetime.strptime(
                                item["date"], "%d.%m.%Y %H:%M"
                            ).timetuple()
                        )
                    except Exception:
                        log.warning("Cannot decode time stamp format {err}")
                        timestart = item["date"]
            except Exception:
                log.warning("No measurement time found.")
                timestart = datetime.now().strftime("%Y-%m-%d_%H%M%S")

            try:
                vdepl = item["depletion_voltage"]
            except Exception:
                if input_vdepl is not None:
                    vdepl = input_vdepl
                    log.warning(
                        "No depletion voltage found, using manual input via --vdepl."
                    )
                else:
                    log.warning(
                        "No depletion voltage found! Will use database or default value."
                    )
            if item["IV_ARRAY"]:
                iv_array = item["IV_ARRAY"]
            else:
                log.error("No measurement data found!")
                return None
            current_unit = "uA"
            try:
                if item["prefix"] and "A" in item["prefix"]:
                    current_unit = item["prefix"]
            except Exception:
                log.warning(
                    "No prefix found. Assuming default current unit {%s}!", current_unit
                )
        elif qchelper:
            if len(item) == 1:
                jtem = item[0]
            else:
                log.error("Unknown format.")
                return None

            metadata = jtem["results"].get("Metadata") or jtem["results"].get(
                "metadata"
            )

            if jtem["serialNumber"] == metadata["MODULE_SN"]:
                module_sn = jtem["serialNumber"]
            elif not jtem["serialNumber"] and metadata["MODULE_SN"]:
                module_sn = metadata["MODULE_SN"]
            elif jtem["serialNumber"] and not metadata["MODULE_SN"]:
                module_sn = jtem["serialNumber"]
            else:
                log.error("'serialNumber' and 'MODULE_SN' are inconsistent or missing!")
                return None

            if "IV_MEASURE" not in jtem["testType"]:
                log.error("No test type found.")
                return None

            ## not there by default
            try:
                institution = jtem["institution"]
            except Exception:
                log.warning("No institution found in measurement file!")
                institution = ""

            try:
                if jtem["date"]:
                    try:
                        timestart = time.mktime(
                            datetime.strptime(
                                jtem["date"], "%d.%m.%Y %H:%M"
                            ).timetuple()
                        )
                    except Exception as err:
                        log.warning("Cannot decode time stamp format {%s}", err)
                        timestart = jtem["date"]
            except Exception:
                log.warning("No measurement time found, using current time.")
                timestart = datetime.now().strftime("%Y-%m-%d_%H%M%S")

            try:
                vdepl = jtem["depletion_voltage"]
            except Exception:
                if input_vdepl is not None:
                    vdepl = input_vdepl
                    log.warning(
                        "No depletion voltage found, using manual input via --vdepl ."
                    )
                else:
                    log.warning(
                        "No depletion voltage found! Will use database or default value."
                    )
            if jtem["results"]["IV_ARRAY"]:
                iv_array = jtem["results"]["IV_ARRAY"]
            else:
                log.error("No measurement data found!")
                return None

            current_unit = "uA"
            try:
                if jtem["prefix"] and "A" in jtem["prefix"]:
                    current_unit = jtem["prefix"]
            except Exception:
                log.warning(
                    "No prefix found. Assuming default current unit {%s}!", current_unit
                )
        else:
            log.error("Unknown format.")

        data = qcDataFrame(
            columns=[
                "time",
                "voltage",
                "current",
                "sigma current",
                "temperature",
                "humidity",
            ],
            units=["s", "V", current_unit, current_unit, "C", "%"],
        )

        data.set_x("voltage", True)
        data.add_data(iv_array)
        data.add_meta_data("Institution", institution)
        data.add_meta_data("ModuleSN", module_sn)
        data.add_meta_data("TimeStart", timestart)
        data.add_meta_data("DepletionVoltage", vdepl)
        data.add_meta_data("AverageTemperature", np.average(data["temperature"]))
        outputDF = outputDataFrame()
        outputDF.set_test_type(test_type)
        outputDF.set_results(data)
        alldf.append(outputDF)
    return alldf


def convert_name_to_serial(chipName):
    serialPrefix = "20UPGFC"  # This will change to 20UPGFW for real wafers
    try:
        chip_number = str(int(chipName, base=16))
        # Add preceding zeros
        while len(chip_number) < 7:
            chip_number = "0" + chip_number
        return serialPrefix + str(chip_number)
    except Exception:
        msg = f"Can't convert chip name ({chipName}) into serial number, setting serial number to {chipName}"
        log.warning(msg)
        return chipName


def convert_serial_to_name(chipSerial):
    # Assumes prefix is of length 7 (i.e. "20UPGFC")
    try:
        # Remove prefix and preceding 0's
        chipSerial = chipSerial[7:]
        chipSerial = chipSerial.lstrip("0")
        chipName = hex(int(chipSerial))
    except Exception:
        chipName = chipSerial
        msg = f"Can't convert chip serial number ({chipSerial}) into name, setting chip name to {chipSerial}"
        log.warning(msg)
    return chipName


def get_nominal_current(meas_config, layer, chip_type, n_chips_input=0):
    default_n_chips_in_module = get_n_chips(layer)

    if n_chips_input > default_n_chips_in_module:
        log.error(
            "Invalid input: input n chips (%s) is higher than the default n chips for the given module type (%s)",
            n_chips_input,
            default_n_chips_in_module,
        )
        sys.exit(1)

    try:
        nom_current = (
            meas_config["tasks"]["GENERAL"]["i_config"][chip_type][layer]
            / default_n_chips_in_module
        )
    except KeyError as e:
        log.error("KeyError: Missing key in configuration - %s", e)
        sys.exit(1)
    except ZeroDivisionError as e:
        log.error("ZeroDivisionError: Division by zero - %s", e)
        sys.exit(1)
    except TypeError as e:
        log.error("TypeError: Invalid JSON structure - %s", e)
        sys.exit(1)
    except Exception as e:
        log.error("Cannot retrieve nominal current from meas_config: %s", e)
        sys.exit(1)

    n_chips = default_n_chips_in_module
    if n_chips_input not in {0, default_n_chips_in_module}:
        log.warning(
            "Overwriting default number of chips (%s) with manual input (%s)!",
            default_n_chips_in_module,
            n_chips_input,
        )
        n_chips = n_chips_input

    return nom_current * n_chips


def get_n_chips(layer):
    chips_per_layer = {"L0": 3, "L1": 4, "L2": 4}
    return chips_per_layer.get(layer, 0)


# Returns module type component code, given module serial number
def get_type_from_sn(module_sn):
    module_types = {
        "PI": {
            "MS": "TRIPLET_L0_STAVE_MODULE",
            "M0": "TRIPLET_L0_RING0_MODULE",
            "M5": "TRIPLET_L0_RING0.5_MODULE",
            "M1": "L1_QUAD_MODULE",
            "R6": "DIGITAL_TRIPLET_L0_STAVE_MODULE",
            "R7": "DIGITAL_TRIPLET_L0_RING0_MODULE",
            "R8": "DIGITAL_TRIPLET_L0_RING0.5_MODULE",
            "RB": "DIGITAL_L1_QUAD_MODULE",
            "RT": "DUMMY_TRIPLET_L0_STAVE_MODULE",
            "RU": "DUMMY_TRIPLET_L0_RING0_MODULE",
            "RV": "DUMMY_TRIPLET_L0_RING0.5_MODULE",
        },
        "PG": {
            "M2": "OUTER_SYSTEM_QUAD_MODULE",
            "R0": "SINGLE_CHIP_MODULE",
            "R2": "DUAL_CHIP_MODULE",
            "R9": "DIGITAL_QUAD_MODULE",
            "RQ": "DUMMY_QUAD_MODULE",
            "RR": "DUMMY_L1_QUAD_MODULE",
            "XM": "TUTORIAL_MODULE",
        },
    }

    try:
        return module_types[module_sn[3:5]][module_sn[5:7]]
    except Exception:
        msg = f"Unknown module type ({module_sn}) - will not separate inner from outer pixels in disconnected bump analysis"
        log.warning(msg)
        return "unknown"


def get_sensor_type_from_sn(sensor_sn):
    sensor_types = {
        "S0": "L0_INNER_PIXEL_3D_SENSOR_TILE_25",
        "S1": "L0_INNER_PIXEL_3D_SENSOR_TILE_50",
        "S2": "L1_INNER_PIXEL_QUAD_SENSOR_TILE",
        "S3": "OUTER_PIXEL_QUAD_SENSOR_TILE",
    }
    try:
        return sensor_types[sensor_sn[5:7]]
    except KeyError as exc:
        msg = f"Unknown sensor type for serial number: {sensor_sn}"
        raise ValueError(msg) from exc


def get_sensor_type_from_layer(layer):
    sensor_type = {
        "R0": "3D",
        "R0.5": "3D",
        "L0": "3D",
        "L1": "L1_INNER_PIXEL_QUAD_SENSOR_TILE",
        "L2": "OUTER_PIXEL_QUAD_SENSOR_TILE",
        "L3": "OUTER_PIXEL_QUAD_SENSOR_TILE",
        "L4": "OUTER_PIXEL_QUAD_SENSOR_TILE",
    }
    try:
        return sensor_type[layer]
    except KeyError as exc:
        msg = f"Layer {layer} invalid!"
        raise ValueError(msg) from exc


# requires the connectivity file name to be "<ATLAS_SN>_<layer>_<suffix>.json" as output from the database tool
def get_sn_from_connectivity(fileName):
    try:
        moduleSN = Path(fileName).stem.split("_")[0]
        check_sn_format(moduleSN)
    except Exception as e:
        msg = f"Cannot extract module serial number from path ({fileName}): {e}"
        log.error(msg)
        sys.exit(1)
    return moduleSN


def get_layer_from_sn(sn):
    check_sn_format(sn)
    if "PIMS" in sn or "PIR6" in sn:
        return "L0"

    if "PIM0" in sn or "PIR7" in sn:
        return "L0"  # "R0"

    if "PIM5" in sn or "PIR8" in sn:
        return "L0"  # "R0.5"

    if "PIM1" in sn or "PIRB" in sn:
        return "L1"

    if "PG" in sn:
        return "L2"

    msg = f"Cannot recognise {sn}, not a valid module SN."
    log.error(msg)
    sys.exit(2)


def get_nlanes_from_sn(sn):
    check_sn_format(sn)
    if "PIMS" in sn or "PIR6" in sn:
        return 4  # L0

    if "PIM0" in sn or "PIR7" in sn:
        return 3  # R0

    if "PIM5" in sn or "PIR8" in sn:
        return 2  # R0.5

    if "PIM1" in sn or "PIRB" in sn:
        return 1  # L1

    if "PG" in sn:
        return 1  # L2-L4

    msg = f"Cannot get the number of lanes from this SN: {sn} \U0001F937"
    log.error(msg)
    sys.exit(3)


def check_sn_format(sn):
    if len(sn) != 14 or not sn.startswith("20U"):
        msg = f"Cannot recognise ATLAS SN {sn}. Please enter a valid ATLAS SN."
        log.error(msg)
        sys.exit(5)
    return True


def get_env(key):
    value = os.getenv(key, default=None)
    if value:
        msg = f"{key} is {value}."
        log.info(msg)
    else:
        msg = f"Variable '{key}' is not set."
        log.warning(msg)
    return value


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


class qcDataFrame:
    """
    The QC data frame which stores meta data and task data.
    """

    def __init__(self, columns=None, units=None, x=None, _dict=None):
        self._identifiers = {}
        self._meta_data = {}
        self._data = {}
        self._property = {}
        self._parameter = {}
        self._comment = ""
        if _dict:
            self.from_dict(_dict)
            return

        columns = columns or []

        for i, column in enumerate(columns):
            self._data[column] = {
                "X": x[i] if x else False,
                "Unit": units[i] if units else None,
                "Values": [],
            }

    def add_meta_data(self, key, value):
        self._meta_data[key] = value

    def add_data(self, data):
        for key, value in data.items():
            self._data[key]["Values"] += list(value)

    def add_column(self, column, unit=False, x=False, data=None):
        data = data or []
        if column in self._data:
            msg = f"column {column} already exists! Will overwrite."
            log.warning(msg)
        self._data[column] = {"X": x, "Unit": unit, "Values": list(data)}

    def add_property(self, key, value, precision=-1):
        if key in self._property:
            msg = f"property {key} already exists! Will overwrite."
            log.warning(msg)
        if precision != -1:
            with suppress(Exception):
                value = self._round(key, value, precision)
        self._property[key] = value

    def add_parameter(self, key, value, precision=-1):
        if key in self._parameter:
            msg = f"parameter {key} already exists! Will overwrite."
            log.warning(msg)
        if precision != -1:
            if isinstance(value, dict):
                for k, v in value.items():
                    value[k] = self._round(k, v, precision)
            else:
                value = self._round(key, value, precision)
        self._parameter[key] = value

    def _round(self, key, value, precision):
        try:
            if isinstance(value, list):
                value = np.around(value, precision).tolist()
            else:
                value = round(value, precision)
        except Exception:
            msg = f"Unable to round value stored in output file for {key}."
            log.warning(msg)
        return value

    def add_comment(self, comment, override=False):
        if override or self._comment == "":
            self._comment = comment
        else:
            self._comment += ". " + str(comment)

    def __getitem__(self, column):
        return np.array(self._data[column]["Values"])

    def set_unit(self, column, unit):
        self._data[column]["Unit"] = unit

    def get_unit(self, column):
        return self._data[column]["Unit"]

    def set_x(self, column, x):
        self._data[column]["X"] = x

    def get_x(self, column):
        return self._data[column]["X"]

    def __len__(self):
        return max(len(value["Values"]) for value in self._data.values())

    def sort_values(self, by, reverse=False):
        for key, value in self._data.items():
            if key == by:
                continue
            value["Values"] = list(
                next(
                    zip(
                        *sorted(
                            zip(
                                value["Values"], self._data[by]["Values"], strict=False
                            ),
                            key=lambda x: x[1],
                            reverse=reverse,
                        ),
                        strict=False,
                    )
                )
            )
        self._data[by]["Values"].sort(reverse=reverse)

    def get_meta_data(self):
        return self._meta_data

    def get_identifiers(self):
        return {
            k: self._meta_data.get(k)
            for k in (
                "ChipID",
                "Name",
                "ModuleSN",
                "Institution",
                "TestType",
                "TimeStart",
                "TimeEnd",
            )
        }

    def get_properties(self):
        return self._property

    def get_comment(self):
        return self._comment

    def __str__(self):
        text = "Identifiers:\n"
        text += str(json.dumps(self.get_identifiers(), cls=MyEncoder, indent=4))
        text += "\n"
        # text += "Meta data:\n"
        # text += str(json.dumps(self._meta_data, cls=MyEncoder, indent=4))
        # text += "\n"
        table = []
        for key, value in self._data.items():
            table.append(
                [key + (f" [{value['Unit']}]" if value["Unit"] else "")]
                + value["Values"]
            )
        text += tabulate(table, floatfmt=".3f")
        return text

    def __rich_identifiers__(self):
        pretty = Pretty(self.get_identifiers())
        return Panel(pretty)

    def __rich_data__(self):
        for chunk in chunks(list(self._data.items()), 10):
            table = Table()

            data = []
            for key, column in chunk:
                unit = f"({column['Unit']})" if column["Unit"] else ""
                identifier = f"{key} {unit}" if column["Unit"] else key
                table.add_column(
                    identifier, justify="right", style="cyan" if column["X"] else None
                )
                data.append(column["Values"])

            for row in list(zip_longest(*data, fillvalue=np.nan)):
                table.add_row(*[f"{x:0.2f}" for x in row])

            yield table

    def __rich_console__(
        self, _console: Console, _options: ConsoleOptions
    ) -> RenderResult:
        yield self.__rich_identifiers__()
        yield Group(*self.__rich_data__())

    def to_dict(self):
        return {
            "property": self._property,
            "parameter": self._parameter,
            "comment": self._comment,
            "Measurements": self._data,
            "Metadata": self._meta_data,
        }

    def from_dict(self, _dict):
        self._meta_data = _dict.get("metadata", {}) or _dict["Metadata"]
        self._identifiers = self.get_identifiers()
        self._data = _dict["Measurements"]
        self._property = _dict["property"]
        self._comment = _dict["comment"]

    def to_json(self):
        _dict = self.to_dict()
        return json.dumps(_dict, cls=MyEncoder, indent=4)

    def save_json(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        _dict = self.to_dict()
        with Path(path).open("w", encoding="UTF-8") as fp:
            json.dump(_dict, fp, cls=MyEncoder, indent=4)


class outputDataFrame:
    """
    The output file format, designed to work well with localDB and prodDB
    """

    def __init__(self, _dict=None):
        self._serialNumber = "Unknown"
        self._testType = "Not specified"
        self._subtestType = ""
        self._results = qcDataFrame()  # holds qcDataFrame
        self._passed = False
        self._runNumber = None
        if _dict:
            self.from_dict(_dict)

    def set_serial_num(self, serial_num=None):
        if serial_num is not None:
            self._serialNumber = serial_num
        else:
            try:
                chipName = self._results.get_meta_data()["Name"]
            except Exception:
                log.warning("Can't find chip name for serial number conversion")
                return
            self._serialNumber = convert_name_to_serial(chipName)

    @property
    def run_number(self):
        if not bson.ObjectId.is_valid(self._runNumber):
            self._runNumber = bson.ObjectId()
        return self._runNumber

    @property
    def passed(self):
        return self._passed

    def set_test_type(self, test_type=None):
        if test_type is not None:
            self._testType = test_type
        else:
            self._testType = "Not specified"

    def set_subtest_type(self, subtest_type=None):
        if subtest_type is not None:
            self._subtestType = subtest_type
        else:
            self._subtestType = "Not specified"

    def set_pass_flag(self, passed=False):
        self._passed = passed

    def set_results(self, results=None):
        if results is not None:
            self._results = results
        else:
            self._results = qcDataFrame()
        if self._serialNumber == "Unknown":
            self.set_serial_num()

    def get_results(self):
        return self._results

    def to_dict(self, forAnalysis=False):
        _dict = {
            "serialNumber": self._serialNumber,
            "testType": self._testType,
            "runNumber": str(self.run_number),
        }
        if not forAnalysis:
            _dict.update({"subtestType": self._subtestType})
        all_results = self.get_results().to_dict()
        parameters = all_results.get("parameter")
        all_results.pop("parameter")

        # Write out different information, depending on if we are in measurement or analysis step
        if forAnalysis:
            all_results.pop("Measurements")
            metadata_keep = [
                "MEASUREMENT_VERSION",
                "YARR_VERSION",
                "MEASUREMENT_DATE",
                "QC_LAYER",
                "INSTITUTION",
                "MODULE_SN",
            ]  # Metadata we want to write out
            metadata = all_results.get("metadata", {}) or all_results["Metadata"]
            metadata_keys = list(metadata.keys())
            for key in metadata_keys:
                if key not in metadata_keep:
                    metadata.pop(key)
            all_results.pop("comment")
            for key, value in parameters.items():
                all_results[key] = value
            _dict["passed"] = self._passed
        results = {"results": all_results}
        _dict.update(results)
        return _dict

    def save_json(self, path, forAnalysis=False):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        _dict = self.to_dict(forAnalysis)
        with Path(path).open("w", encoding="UTF-8") as fp:
            json.dump(_dict, fp, cls=MyEncoder, indent=4)

    def from_dict(self, _dict):
        self._serialNumber = _dict.get("serialNumber")
        self._testType = _dict.get("testType")
        self._subtestType = _dict.get("subtestType")
        self._runNumber = _dict.get("runNumber")
        self._passed = _dict.get("passed", False)
        try:
            self._results = qcDataFrame(_dict=_dict.get("results"))
        except Exception:
            self._results = _dict.get("results")
