import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm, ttest_ind
from scipy import stats
from statsmodels.stats.proportion import test_proportions_2indep
import statsmodels.stats.weightstats as ws
from typing import List, Tuple, Union
import seaborn as sns
from tqdm import tqdm

def get_mde(
    mean: float,
    std: float,
    sample_size: list,
    n_groups: int = 2,
    n_metrics: int = 1,
    compare: str = 'only_control',
    alpha_correction: bool = False,
    alpha: float = 0.05,
    beta: float = 0.2
) -> pd.DataFrame(): # type: ignore
    
    """
    Calculate the Minimum Detectable Effect (MDE) for a given set of parameters such as mean, standard deviation, and sample size. MDE represents the smallest effect size that can be detected given statistical constraints.

    Args:
        mean (float): The mean value of the metric.
        std (float): The standard deviation of the metric.
        sample_size (list): A list of sample sizes for which MDE will be calculated.
        n_groups (int, default=2): The number of experimental groups.
        n_metrics (int, default=1): The number of metrics in the analysis.
        compare (str, default='only_control'): Defines comparison type. Options: 'only_control' or 'together'.
        alpha_correction (bool, default=False): If True, applies alpha correction for multiple comparisons.
        alpha (float, default=0.05): The significance level for the test.
        beta (float, default=0.2): The probability of a Type II error (1 - power).

    Returns:
        A DataFrame containing MDE values (absolute and percentage) for each sample size.
    """

    if alpha_correction and compare == 'together':
        alpha_correction = math.factorial(n_groups) / (math.factorial(n_groups - 2) * 2)
        t_alpha = norm.ppf(1 - (alpha / 2) / (alpha_correction * n_metrics))
    elif alpha_correction and compare == 'only_control':
        alpha_correction = n_groups - 1
        t_alpha = norm.ppf(1 - (alpha / 2) / (alpha_correction * n_metrics))
    else:
        t_alpha = norm.ppf(1 - (alpha / 2))
    
    t_beta = norm.ppf(1 - beta)
    variance = std**2

    data = []

    for size in sample_size:
        mde_formula = (t_alpha + t_beta) * np.sqrt((variance*4) / (size))
        data.append({
        'sample_size': size,
        'mde_abs': mde_formula,
        'mde_%': (mde_formula * 100 / mean),
        'alpha': alpha,
        'beta': beta
    })
        
    mde = pd.DataFrame(data)
    mde['sample_size'] = mde['sample_size'].astype('int64')

    for column in mde.columns[1:]:
        mde[column] = mde[column].astype('float')

    return mde

def get_mde_ratio(
    num: np.ndarray,
    denom: np.ndarray,
    sample_size: int,
    n_groups: int = 2,
    n_metrics: int = 1,
    compare: str = 'only_control',
    alpha_correction: bool = False,
    alpha: float = 0.05,
    beta: float = 0.2
) -> Tuple[float, float]:
    
    """
    Calculate the Minimum Detectable Effect (MDE) for ratios, using numerator and denominator arrays to compute variance.

    Args:
        num (np.ndarray): The numerator values.
        denom (np.ndarray): The denominator values.
        sample_size (int): The sample size for the calculation.
        n_groups (int, default=2): Number of experimental groups.
        n_metrics (int, default=1): Number of metrics.
        compare (str, default='only_control'): Defines comparison type.
        alpha_correction (bool, default=False): If True, applies alpha correction for multiple comparisons.
        alpha (float, default=0.05): Significance level.
        beta (float, default=0.2): Probability of Type II error.

    Returns:
        A tuple containing the MDE in percentage and absolute values.
    """

    if alpha_correction and compare == 'together':
        alpha_correction = math.factorial(n_groups) / (math.factorial(n_groups - 2) * 2)
        t_alpha = norm.ppf(1 - (alpha / 2) / (alpha_correction * n_metrics))
    elif alpha_correction and compare == 'only_control':
        alpha_correction = n_groups - 1
        t_alpha = norm.ppf(1 - (alpha / 2) / (alpha_correction * n_metrics))
    else:
        t_alpha = norm.ppf(1 - (alpha / 2))
    
    mean_nom = np.mean(num)
    mean_denom = np.mean(denom)
    std_nom = np.std(num)
    std_denom = np.std(denom)
    cov_nom_denom = np.cov(num, denom)[0, 1]
    mean = np.sum(num) / np.sum(denom)
    var_metric = (
        (std_nom**2) / (mean_denom**2) +
        (mean_nom**2) / (mean_denom**4) * (std_denom**2) -
        2 * mean_nom / (mean_denom**3) * cov_nom_denom
    )
    variance = var_metric
    t_beta = norm.ppf(1 - beta)
    mde = (t_alpha + t_beta) * np.sqrt((variance*4) / (sample_size))
    return mde * 100 / mean, mde

def plot_p_value_over_time(
    dates: List[Union[str, float]],
    test_group: List[List[float]],
    control_group: List[List[float]],
    significance_level: float = 0.05
) -> None:
    
    """
    Plot the dynamics of p-values over time during an experiment. Highlights areas where the p-value is below the significance threshold.

    Args:
        dates (List[Union[str, float]]): Dates or time periods corresponding to the data.
        test_group (List[List[float]]): Test group data for each time point.
        control_group (List[List[float]]): Control group data for each time point.
        significance_level (float, default=0.05): The threshold for statistical significance.
    
    Returns:
        None. Displays a line plot showing p-value dynamics.
    """

    if len(dates) != len(test_group) or len(dates) != len(control_group):
        raise ValueError("Lengths of 'dates', 'test_group', and 'control_group' must match.")
    
    p_values = [
        ttest_ind(test_data, control_data, equal_var=False)[1]
        for test_data, control_data in zip(test_group, control_group)
    ]
    
    plt.figure(figsize=(15, 6))
    plt.plot(dates, p_values, marker='o', linestyle='-', label='P-value', color='blue')
    plt.axhline(y=significance_level, color='red', linestyle='--', label=f'Significance level ({significance_level})')
    plt.fill_between(
        dates, 0, p_values, where=np.array(p_values) < significance_level,
        color='green', alpha=0.2, label='Below significance'
    )
    plt.title('P-value Over Time During Experiment', fontsize=14)
    plt.xlabel('Date/Period', fontsize=12)
    plt.ylabel('P-value', fontsize=12)
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(alpha=0.5)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()

def ttest(
    df: pd.DataFrame,
    metric_col: str,
    ab_group_col: str,
    pairs_list: List[Tuple[str, str]] = [(0, 1)],
    corrected_ci: float = 0.95,
    flag_notation: bool = False
) -> pd.DataFrame:
    
    """
    Perform two-sample t-tests between specified groups and compute confidence intervals for the differences.

    Args:
        df (pd.DataFrame): The dataset containing the metric and group columns.
        metric_col (str): The column name for the metric being analyzed.
        ab_group_col (str): The column identifying groups (e.g., A/B).
        pairs_list (List[Tuple[str, str]], default=[(0, 1)]): Pairs of groups to compare.
        corrected_ci (float, default=0.95): Confidence level for the intervals.
        flag_notation (bool, default=False): If True, prints detailed results.
    
    Returns:
        A DataFrame containing t-statistics, p-values, means, and confidence intervals for each group comparison.
    """

    res_table = pd.DataFrame()
    tail = (1 + corrected_ci) / 2
    for pair in pairs_list:
        sample0 = df.loc[df[ab_group_col] == pair[0], metric_col]
        sample1 = df.loc[df[ab_group_col] == pair[1], metric_col]
        m0 = sample0.mean()
        m1 = sample1.mean()
        v0 = sample0.std()**2
        v1 = sample1.std()**2
        n0 = len(sample0)
        n1 = len(sample1)
        value = ws.ttest_ind(
            sample0,
            sample1,
            alternative='two-sided',
            usevar='unequal'
        )
        se = np.sqrt(v0 / n0 + v1 / n1)
        delta = m1 - m0
        delta_per = (m1 / m0 - 1) * 100
        lb = delta - stats.t.ppf(tail, value[2]) * se
        ub = delta + stats.t.ppf(tail, value[2]) * se
        lb_per = lb * 100 / m0
        ub_per = ub * 100 / m0
        
        if flag_notation == True:
            print(f'\nComparison between groups: {pair[0]} and {pair[1]}')
            print(f't-statistic: {value[0]}, pvalue: {value[1]}, df: {value[2]}')
            print(f'delta = {delta}')
            print(f'delta,% = {delta_per}%')
            print(f'Confidence interval for delta: ({lb}, {ub})')
            print(f'Confidence interval for delta, %: ({lb_per}, {ub_per})')

        result = pd.DataFrame(
            np.array([metric_col, n0, n1, pair[0], pair[1], value[0], value[2], value[1], m0, m1, delta, delta_per, lb, ub, lb_per, ub_per]).reshape(1, -1),
            columns=['metric_name', 
                     'group0_sample_size', 
                     'group1_sample_size',
                     'group0', 
                     'group1', 
                     'statistic', 
                     'pvalue', 
                     'mean0', 
                     'mean1', 
                     'diff_mean', 
                     'diff_mean_%', 
                     'lb', 
                     'ub', 
                     'lb_%', 
                     'ub_%']
        )
        res_table = pd.concat([res_table, result])
    
    for column in res_table.columns[5:]:
        res_table[column] = res_table[column].astype(float)

    return res_table

def ztest_proportion(
    df: pd.DataFrame,
    metric_col: str,
    ab_group_col: str,
    pairs_list: List[Tuple[str, str]] = [(0, 1)],
    corrected_ci: float = 0.95,
    flag_notation: bool = False
) -> pd.DataFrame:
    
    """
    Perform z-tests to compare proportions between two groups.

    Args:
        df (pd.DataFrame): The dataset containing the metric and group columns.
        metric_col (str): The column representing binary outcomes (e.g., success/failure).
        ab_group_col (str): The column identifying groups.
        pairs_list (List[Tuple[str, str]], default=[(0, 1)]): Pairs of groups to compare.
        corrected_ci (float, default=0.95): Confidence level.
        flag_notation (bool, default=False): If True, prints detailed results.
    
    Returns:
        A DataFrame containing z-statistics, p-values, proportions, and confidence intervals for each comparison.
    """

    res_table = pd.DataFrame()
    tail = (1 + corrected_ci) / 2
    for pair in pairs_list:
        num0 = df[df[ab_group_col] == pair[0]][metric_col].sum()
        denom0 = df[df[ab_group_col] == pair[0]][metric_col].count()
        num1 = df[df[ab_group_col] == pair[1]][metric_col].sum()
        denom1 = df[df[ab_group_col] == pair[1]][metric_col].count()
        p0 = num0 / denom0
        p1 = num1 / denom1
        std0 = df[df[ab_group_col] == pair[0]][metric_col].std()
        std1 = df[df[ab_group_col] == pair[1]][metric_col].std()
        r = test_proportions_2indep(
            num0, denom0,
            num1, denom1,
            value=0,
            method='wald',
            compare='diff',
            alternative='two-sided',
            return_results = True
        )
        se = np.sqrt(r.variance)
        delta = p1 - p0
        delta_per = (p1 / p0 - 1) * 100
        lb = delta - stats.norm.ppf(tail) * se
        ub = delta + stats.norm.ppf(tail) * se
        lb_per = lb * 100 / p0
        ub_per = ub * 100 / p0
        
        if flag_notation == True:
            print(f'\nComparison between groups: {pair[0]} and {pair[1]}')
            print(f'statistic: {r.statistic}, pvalue: {r.pvalue}')
            print(f'delta = {delta}')
            print(f'delta,% = {delta_per}%')
            print(f'Confidence interval for delta: ({lb}, {ub})')
            print(f'Confidence interval for delta, %: ({lb_per}, {ub_per})')

        result = pd.DataFrame(
            np.array([metric_col, denom0, denom1, pair[0], pair[1], r.statistic, r.pvalue, p0, p1, delta, delta_per, lb, ub, lb_per, ub_per]).reshape(1, -1),
            columns=['metric_name', 
                     'group0_sample_size', 
                     'group1_sample_size', 
                     'group0', 
                     'group1', 
                     'statistic', 
                     'pvalue', 
                     'mean0', 
                     'mean1', 
                     'diff_mean', 
                     'diff_mean_%', 
                     'lb', 
                     'ub', 
                     'lb_%', 
                     'ub_%',]
        )
        res_table = pd.concat([res_table, result])

        for column in res_table.columns[5:]:
            res_table[column] = res_table[column].astype(float)
        
    return res_table

def ttest_delta(
    df: pd.DataFrame,
    metric_num_col: str,
    metric_denom_col: str,
    ab_group_col: str,
    pairs_list: List[Tuple[str, str]] = [(0, 1)],
    corrected_ci: float = 0.95,
    flag_notation: bool = False
    ) -> pd.DataFrame:

    """
    Perform t-tests to compare deltas (differences) between two ratios for specified groups.

    Args:
        df (pd.DataFrame): The dataset containing the numerator, denominator, and group columns.
        metric_num_col (str): Column for the numerator metric.
        metric_denom_col (str): Column for the denominator metric.
        ab_group_col (str): Column identifying groups.
        pairs_list (List[Tuple[str, str]], default=[(0, 1)]): Pairs of groups to compare.
        corrected_ci (float, default=0.95): Confidence level.
        flag_notation (bool, default=False): If True, prints detailed results.
    
    Returns:
        A DataFrame containing t-statistics, p-values, ratios, deltas, and confidence intervals.
    """

    def get_ratio_var(
    num: np.ndarray,
    denom: np.ndarray
    ) -> float:
        cov = np.cov(num, denom, ddof=1)[0, 1]
        var = (
            (np.std(num) ** 2) / (np.mean(denom) ** 2) +
            (np.mean(num) ** 2) / (np.mean(denom) ** 4) * (np.std(denom) ** 2) -
            2 * np.mean(num) / (np.mean(denom) ** 3) * cov
        )
        return var

    res_table = pd.DataFrame()
    for pair in pairs_list:
        num0 = df.loc[df[ab_group_col] == pair[0], metric_num_col]
        denom0 = df.loc[df[ab_group_col] == pair[0], metric_denom_col]
        num1 = df.loc[df[ab_group_col] == pair[1], metric_num_col]
        denom1 = df.loc[df[ab_group_col] == pair[1], metric_denom_col]
        group0_sample_size = df.loc[df[ab_group_col] == pair[0], metric_num_col].count()
        group1_sample_size = df.loc[df[ab_group_col] == pair[1], metric_num_col].count()
        metric_name = f'({metric_num_col}, {metric_denom_col})'
        ratio0 = np.sum(num0) / np.sum(denom0)
        ratio1 = np.sum(num1) / np.sum(denom1)
        se = np.sqrt(get_ratio_var(num0, denom0)/len(num0) + get_ratio_var(num1, denom1)/len(num1))
        delta = ratio1 - ratio0
        delta_per = (ratio1 / ratio0 - 1) * 100
        statistic = delta / se
        df_ = len(num0) + len(num1) - 2
        pvalue = (1 - stats.t.cdf(np.abs(statistic), df_)) * 2
        tail = (1 + corrected_ci) / 2
        lb = delta - stats.t.ppf(tail, df_) * se
        ub = delta + stats.t.ppf(tail, df_) * se
        lb_per = lb * 100 / ratio0
        ub_per = ub * 100 / ratio0
        
        if flag_notation == True:
            print(f'\nComparison between groups: {pair[0]} and {pair[1]}')
            print(f'statistic: {statistic}, pvalue: {pvalue}')
            print(f'delta = {delta}')
            print(f'delta,% = {delta_per}%')
            print(f'Confidence interval for delta: ({lb}, {ub})')
            print(f'Confidence interval for delta, %: ({lb_per}, {ub_per})')

        result = pd.DataFrame(
            np.array([metric_name, group0_sample_size, group1_sample_size, pair[0], pair[1], statistic, pvalue, ratio0, ratio1, delta, delta_per, lb, ub, lb_per, ub_per]).reshape(1, -1),
            columns=['metric_name', 'group0_sample_size', 'group1_sample_size', 'group0', 'group1', 'statistic', 'pvalue', 'mean0', 'mean1', 'diff_mean', 'diff_mean_%', 'lb', 'ub', 'lb_%', 'ub_%']
        )
        res_table = pd.concat([res_table, result])

        for column in res_table.columns[5:]:
            res_table[column] = res_table[column].astype(float)

    return res_table

def plot_p_value_distribution(
    control_group: np.ndarray,
    test_group: np.ndarray,
    num_tests: int = 1000
) -> None:
    
    """
    Plot the distribution of p-values generated from A/A tests, highlighting the frequency of false positives.

    Args:
        control_group (np.ndarray): Data for the control group.
        test_group (np.ndarray): Data for the test group.
        num_tests (int, default=1000): Number of A/A tests to perform.
    
    Returns:
        None. Displays a histogram of p-values.
    """

    np.random.seed(42)

    p_values = [
        ttest_ind(np.random.choice(control_group, size=len(control_group), replace=True),
                  np.random.choice(test_group, size=len(test_group), replace=True), equal_var=False)[1]
        for _ in tqdm(range(num_tests))
    ]
    
    plt.figure(figsize=(15, 6))
    plt.hist(p_values, bins=50, color='blue', alpha=0.7, edgecolor='black')
    plt.axvline(x=0.05, color='red', linestyle='--', label='Significance level (0.05)')
    plt.title('P-value Distribution from A/A Tests', fontsize=14)
    plt.xlabel('P-value', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(alpha=0.5)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()

def plot_pvalue_ecdf(control_group, test_group, title=None):

    """
    Plot the histogram and empirical cumulative distribution function (ECDF) of p-values.

    Args:
        control_group (pd.DataFrame): Data for the control group.
        test_group (pd.DataFrame): Data for the test group.
        title (str, optional): Title for the plot.
    
    Returns:
        None. Displays a histogram and ECDF plot for p-values.
    """

    pvalues = [
        ttest_ind(np.random.choice(control_group[control_group['has_treatment'] == 1]['gmv'], size=64, replace=True),
                np.random.choice(test_group[test_group['has_treatment'] == 0]['gmv'], size=64, replace=True), equal_var=False)[1]
        for _ in tqdm(range(1000))
]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    if title:
        plt.suptitle(title)

    sns.histplot(pvalues, ax=ax1, bins=20, stat='density') # type: ignore
    ax1.plot([0,1],[1,1], 'k--')
    ax1.set(xlabel='p-value', ylabel='Density')

    sns.ecdfplot(pvalues, ax=ax2) # type: ignore
    ax2.plot([0,1],[0,1], 'k--')
    ax2.set(xlabel='p-value', ylabel='Probability')
    ax2.grid()

def method_benjamini_hochberg(
    pvalues: np.ndarray,
    alpha: float = 0.05
) -> np.ndarray:
    
    """
    Implements the Benjamini-Hochberg procedure to control the False Discovery Rate (FDR) in multiple hypothesis testing. This method determines which null hypotheses to reject based on a set of p-values and a specified significance level (alpha).

    Args:
        pvalues (np.ndarray): An array of p-values from multiple hypothesis tests.
        alpha (float, default=0.05): The desired False Discovery Rate (FDR) threshold.
    
    Returns:
        np.ndarray: A binary array of the same length as pvalues, where:
            1 indicates that the corresponding null hypothesis is rejected (statistically significant).
            0 indicates that the null hypothesis is not rejected.
    """

    m = len(pvalues)
    array_alpha = np.arange(1, m + 1) * alpha / m
    sorted_pvalue_indexes = np.argsort(pvalues)
    res = np.zeros(m)
    for idx, pvalue_index in enumerate(sorted_pvalue_indexes):
        pvalue = pvalues[pvalue_index]
        alpha_ = array_alpha[idx]
        if pvalue <= alpha_:
            res[pvalue_index] = 1
        else:
            break
    return res.astype(int)
