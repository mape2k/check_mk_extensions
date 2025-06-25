#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# duallevel: /omd/sites/omdsus24/lib/check_mk/plugins/memory/rulesets/mem_win.py


# (c) 2022 Marcel Pennewiss <opensource@pennewiss.de>
# (c) 2025 Christian Kreidl <christian.kreidl@ziti.uni-heidelberg.de>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  This file is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from cmk.rulesets.v1 import Label, Title, Help
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    SingleChoice,
    SingleChoiceElement,
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    Float,
    Percentage,
    LevelDirection,
    SimpleLevels,
    SimpleLevelsConfigModel,
    migrate_to_float_simple_levels,
    migrate_to_integer_simple_levels,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostCondition, Topic


from typing import Generic, TypedDict, TypeVar

_NumberT = TypeVar("_NumberT", int, float)

class _DualLevels(TypedDict, Generic[_NumberT]):
    upper: SimpleLevelsConfigModel[_NumberT]
    lower: SimpleLevelsConfigModel[_NumberT]


def migrate_to_dual_levels(
    model: object, scale: float, ntype: type[_NumberT]
) -> SimpleLevelsConfigModel[_NumberT]:
    match model:
        case None | (None, None, None, None) :
            return _DualLevels(
                    upper=("no_levels", None),
                    lower=("no_levels", None),
            )

        case (float(lower_warn), float(lower_crit), float(upper_warn), float(upper_crit)) :
            return _DualLevels(
                    upper=("fixed", (ntype(upper_warn), ntype(upper_crit))),
                    lower=("fixed", (ntype(lower_warn), ntype(lower_crit))),
            )

        case dict():
            if set(model) == {"upper", "lower"}:
                return model

        case _:
            raise TypeError(f"Could not migrate {model!r} to DualLevel.")


def migrate_to_integer_dual_levels(
    model: object, scale: float = 1.0
) -> SimpleLevelsConfigModel[int]:

    return migrate_to_dual_levels(model, scale, int)


def migrate_to_float_dual_levels(
    model: object, scale: float = 1.0
) -> SimpleLevelsConfigModel[float]:

    return migrate_to_dual_levels(model, scale, float)



def _parameter_valuespec_nut() -> Dictionary:
    return Dictionary(
        elements={
          "battery_charge": DictElement(
            parameter_form = SimpleLevels(
              title = Title("Battery charge"),
              help_text = Help("Set the levels for the minimum charge amount of the battery."),
              form_spec_template = Integer(unit_symbol="%"),
              migrate=migrate_to_integer_simple_levels,
              level_direction = LevelDirection.LOWER,
              prefill_fixed_levels = DefaultValue(value=(90, 85)),
            ),
            required = False,
          ),
          "battery_runtime": DictElement(
            parameter_form = SimpleLevels(
              title = Title("Battery runtime"),
              help_text = Help("Set the levels for time left on battery."),
              form_spec_template = Integer(unit_symbol="minutes"),
              migrate=migrate_to_integer_simple_levels,
              level_direction = LevelDirection.LOWER,
              prefill_fixed_levels = DefaultValue(value=(1200, 900)),
            ),
            required = False,
          ),
          "battery_voltage": DictElement(
            parameter_form = SimpleLevels(
              title = Title("Battery voltage"),
              help_text = Help("Set the levels for the battery voltage."),
              form_spec_template = Float(unit_symbol="V"),
              migrate=migrate_to_float_simple_levels,
              level_direction = LevelDirection.LOWER,
              prefill_fixed_levels = DefaultValue(value=(10.0, 5.0)),
            ),
            required = False,
          ),
          "input_frequency": DictElement(
            parameter_form = Dictionary(
              title = Title("Input frequency"),
              help_text = Help("Set the levels for the input frequency."),
              migrate=migrate_to_float_dual_levels,
              elements = {
                "lower": DictElement(
                  parameter_form = SimpleLevels(
                    title = Title("Lower levels"),
                    form_spec_template = Float(unit_symbol="Hz"),
                    migrate=migrate_to_float_simple_levels,
                    level_direction = LevelDirection.LOWER,
                    prefill_fixed_levels = DefaultValue(value=(49.0, 45.0)),
                  ),
                  required = False,
                ),
                "upper": DictElement(
                  parameter_form = SimpleLevels(
                    title = Title("Upper levels"),
                    form_spec_template = Float(unit_symbol="Hz"),
                    migrate=migrate_to_float_simple_levels,
                    level_direction = LevelDirection.UPPER,
                    prefill_fixed_levels = DefaultValue(value=(51.0, 55.0)),
                  ),
                  required = False,
                ),
              },
            ),
          ),
          "input_voltage": DictElement(
            parameter_form = Dictionary(
              title = Title("Input voltage"),
              help_text = Help("Set the levels for the input voltage."),
              migrate=migrate_to_float_dual_levels,
              elements = {
                "lower": DictElement(
                  parameter_form = SimpleLevels(
                    title = Title("Lower levels"),
                    form_spec_template = Float(unit_symbol="V"),
                    migrate=migrate_to_float_simple_levels,
                    level_direction = LevelDirection.LOWER,
                    prefill_fixed_levels = DefaultValue(value=(0.0, 0.0)),
                  ),
                  required = False,
                ),
                "upper": DictElement(
                  parameter_form = SimpleLevels(
                    title = Title("Upper levels"),
                    form_spec_template = Float(unit_symbol="V"),
                    migrate=migrate_to_float_simple_levels,
                    level_direction = LevelDirection.UPPER,
                    prefill_fixed_levels = DefaultValue(value=(245.0, 250.0)),
                  ),
                  required = False,
                ),
              },
            ),
          ),
          "input_voltage_fault": DictElement(
            parameter_form = SimpleLevels(
              title = Title("Input voltage fault"),
              help_text = Help("Set the levels for the input voltage fault."),
              form_spec_template = Float(unit_symbol="V"),
              migrate=migrate_to_float_simple_levels,
              level_direction = LevelDirection.UPPER,
              prefill_fixed_levels = DefaultValue(value=(155.0, 160.0)),
            ),
            required = False,
          ),
          "output_voltage": DictElement(
            parameter_form = Dictionary(
              title = Title("Output voltage"),
              help_text = Help("Set the levels for the output voltage."),
              migrate=migrate_to_float_dual_levels,
              elements = {
                "lower": DictElement(
                  parameter_form = SimpleLevels(
                    title = Title("Lower levels"),
                    form_spec_template = Float(unit_symbol="V"),
                    migrate=migrate_to_float_simple_levels,
                    level_direction = LevelDirection.LOWER,
                    prefill_fixed_levels = DefaultValue(value=(0.0, 0.0)),
                  ),
                  required = False,
                ),
                "upper": DictElement(
                  parameter_form = SimpleLevels(
                    title = Title("Upper levels"),
                    form_spec_template = Float(unit_symbol="V"),
                    migrate=migrate_to_float_simple_levels,
                    level_direction = LevelDirection.UPPER,
                    prefill_fixed_levels = DefaultValue(value=(245.0, 250.0)),
                  ),
                  required = False,
                ),
              },
            ),
          ),
          "ups_beeper_status": DictElement(
            parameter_form=SingleChoice(
              title=Title("Beeper status"),
              help_text=Help("Set the expected beeper status."),
              elements=[
                  SingleChoiceElement(name="enabled", title=Title("Enabled")),
                  SingleChoiceElement(name="disabled", title=Title("Disabled")),
              ],
              prefill=DefaultValue("disabled"),
            ),
            required = False,
          ),
          "ups_load": DictElement(
            parameter_form = Dictionary(
              title = Title("Load"),
              help_text = Help("Set the levels for the load of the UPS."),
              migrate=migrate_to_float_dual_levels,
              elements = {
                "lower": DictElement(
                  parameter_form = SimpleLevels(
                    title = Title("Lower levels"),
                    form_spec_template = Percentage(),
                    migrate=migrate_to_float_simple_levels,
                    level_direction = LevelDirection.LOWER,
                    prefill_fixed_levels = DefaultValue(value=(0.0, 0.0)),
                  ),
                  required = False,
                ),
                "upper": DictElement(
                  parameter_form = SimpleLevels(
                    title = Title("Upper levels"),
                    form_spec_template = Percentage(),
                    migrate=migrate_to_float_simple_levels,
                    level_direction = LevelDirection.UPPER,
                    prefill_fixed_levels = DefaultValue(value=(50.0, 70.0)),
                  ),
                  required = False,
                ),
              },
            ),
          ),
          "ups_temperature": DictElement(
            parameter_form = SimpleLevels(
              title = Title("Temperature"),
              help_text = Help("Set the levels for the temperature of the UPS."),
              form_spec_template = Float(unit_symbol="°C"),
              migrate=migrate_to_float_simple_levels,
              level_direction = LevelDirection.UPPER,
              prefill_fixed_levels = DefaultValue(value=(35.0, 40.0)),
            ),
            required = False,
          ),
        },
    )

rule_spec_nut = CheckParameters(
    name = "nut",
    title = Title("Network UPS Tools"),
    topic = Topic.GENERAL,
    parameter_form = _parameter_valuespec_nut,
    condition = HostCondition(),
)

