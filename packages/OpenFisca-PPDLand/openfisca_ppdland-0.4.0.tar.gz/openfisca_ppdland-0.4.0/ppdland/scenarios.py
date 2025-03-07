import logging

from openfisca_survey_manager.scenarios.abstract_scenario import AbstractSurveyScenario


from ppdland import CountryTaxBenefitSystem as PPDLandTaxBenefitSystem


log = logging.getLogger(__name__)


class PPDLandSurveyScenario(AbstractSurveyScenario):
    def __init__(self, data = None, tax_benefit_system = None,
            baseline_tax_benefit_system = None, period = None):
        super(PPDLandSurveyScenario, self).__init__()
        assert data is not None
        assert period is not None
        self.period = period
        if tax_benefit_system is None:
            tax_benefit_system = PPDLandTaxBenefitSystem()
        if baseline_tax_benefit_system is None:
            self.set_tax_benefit_systems(
                tax_benefit_systems = {'baseline' : tax_benefit_system}
            )
        else:
            self.set_tax_benefit_systems(
                tax_benefit_systems = {'reform' : tax_benefit_system,
                'baseline' : baseline_tax_benefit_system}
            )
        self.used_as_input_variables = list(
            set(tax_benefit_system.variables.keys()).intersection(
                set(data['input_data_frame'].columns)
                ))
        self.weight_variable_by_entity = dict(
            individu = "weight_individus",
        )
        self.init_from_data(data = data)


def init_single_entity(scenario, axes = None, parent1 = None, period = None):
    assert parent1 is not None

    individus = {}
    count_so_far = 0
    for nth in range(0, 1):
        group = [parent1]
        for index, individu in enumerate(group):
            if individu is None:
                continue
            id = individu.get('id')
            if id is None:
                individu = individu.copy()
                id = 'ind{}'.format(index + count_so_far)
            individus[id] = individu

        count_so_far += len(group)

    test_data = {
        'period': period,
        'individus': individus
        }
    if axes:
        test_data['axes'] = axes
    scenario.init_from_dict(test_data)
    return scenario
