
import numpy as np
import pandas as pd


def create_input_dataframe():
    """
    Create input dataframe with variable labour_income and pension
    """
    # Almost 15 millions people
    # Around 1.5 million household
    np.random.seed(216)
    number_of_households = 1.5e6
    household_weight = 50
    minimum_labour_income = 70
    size = int(number_of_households / household_weight)
    mean_labour_income = 3.5e3
    median_labour_income = .4 * mean_labour_income
    pension_labour_income_ratio = .9
    mean_pension = pension_labour_income_ratio * mean_labour_income
    median_pension = .9 * mean_pension
    is_retired = np.random.binomial(1, .2, size = size)
    # mean_labour_income = exp(mu + sigma ** 2 / 2)
    # median_labour_income = exp(mu)
    potential_wage_earner = np.logical_not(is_retired)
    mu = np.log(median_labour_income)
    sigma = np.sqrt(2 * np.log(mean_labour_income / median_labour_income))
    potential_wage = (
        potential_wage_earner
        * np.random.lognormal(mean = mu, sigma = sigma, size = int(size))
        )
    potential_wage = potential_wage_earner * np.maximum(minimum_labour_income, potential_wage)
    is_employed = potential_wage_earner * np.random.binomial(1, .9, size = size)
    labour_income = is_employed * potential_wage
    mu = np.log(median_pension)
    sigma = np.sqrt(2 * np.log(mean_pension / median_pension))
    pension = (
        is_retired
        * np.random.lognormal(mean = mu, sigma = sigma, size = int(size))
        )
    dividends = (
        10
        + np.maximum(
            0,
            np.random.normal(
                loc = pension + labour_income / 4,
                scale = (pension + labour_income) / 5
                )
            )
        )
    weight_individus = household_weight + 0 * pension
    return pd.DataFrame({
        'dividends': dividends,
        'labour_income': labour_income,
        'pension': pension,
        'potential_wage': potential_wage,
        'weight_individus': weight_individus,
        })


if __name__ == "__main__":
    df = create_input_dataframe()
