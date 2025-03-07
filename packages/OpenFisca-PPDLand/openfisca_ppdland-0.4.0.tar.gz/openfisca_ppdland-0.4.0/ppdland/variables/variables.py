import numpy as np


from openfisca_core.model_api import *
from openfisca_survey_manager.statshelpers import mark_weighted_percentiles


from ppdland.entities import *


class dividends(Variable):
    value_type = float
    entity = Individu
    label = "Dividends"
    definition_period = YEAR


class labour_income(Variable):
    value_type = float
    entity = Individu
    label = "Labour_income"
    definition_period = YEAR


class potential_wage(Variable):
    value_type = float
    entity = Individu
    label = "Potential wage"
    definition_period = YEAR


class pension(Variable):
    value_type = float
    entity = Individu
    label = "Pension"
    definition_period = YEAR

class weight_individus(Variable):
    is_period_size_independent = True
    value_type = float
    entity = Individu
    label = "Personal weight"
    definition_period = YEAR


class income_tax(Variable):
    value_type = float
    entity = Individu
    label = "Income tax"
    definition_period = YEAR

    def formula(individu, period, parameters):
        dividends = individu('dividends', period)
        labour_income = individu('labour_income', period)
        pension = individu('pension', period)
        taxable_income = dividends + labour_income + pension
        tax_scale = parameters(period).tax_scale
        return tax_scale.calc(taxable_income)


class disposable_income(Variable):
    definition_period = YEAR
    label = "Disposable income"
    entity = Individu
    value_type = float

    def formula(individu, period):
        dividends = individu('dividends', period)
        labour_income = individu('labour_income', period)
        pension = individu('pension', period)
        income_tax = individu('income_tax', period)
        return dividends + labour_income + pension - income_tax


class pre_tax_income(Variable):
    definition_period = YEAR
    label = "Pre-tax income"
    entity = Individu
    value_type = float

    def formula(individu, period):
        dividends = individu('dividends', period)
        labour_income = individu('labour_income', period)
        pension = individu('pension', period)
        return dividends + labour_income + pension


class pre_tax_income_decile(Variable):
    value_type = int
    entity = Individu
    label = "Pre-tax income decile"
    definition_period = YEAR

    def formula(individu, period):
        pre_tax_income = individu('pre_tax_income', period)
        labels = np.arange(1, 11)
        weights = 1.0 * np.ones(shape = len(pre_tax_income))
        decile, _ = mark_weighted_percentiles(
            pre_tax_income,
            labels,
            weights,
            method = 2,
            return_quantiles = True,
            )
        return decile
