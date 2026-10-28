"""Correlation analysis and statistical relationship modeling module.

Calculates Pearson (r) and Spearman (rho) coefficients with robust edge-case handling
(constant values, zero variance, <2 observations, missing values) and plain-language
non-causal statistical interpretations.
"""

from dataclasses import dataclass
import math
from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd


@dataclass
class CorrelationResult:
    """Detailed correlation statistical result."""

    pearson_r: Optional[float]
    spearman_rho: Optional[float]
    p_value_pearson: Optional[float]
    p_value_spearman: Optional[float]
    t_statistic_pearson: Optional[float]
    valid_count: int
    missing_count: int
    is_valid: bool
    status: str  # 'valid', 'insufficient_data', 'zero_variance', 'empty'
    interpretation: str
    direction: str  # 'positive', 'negative', 'negligible', 'undefined'
    strength: str  # 'negligible', 'weak', 'moderate', 'strong', 'undefined'
    disclaimer: str


def _regularized_incomplete_beta(a: float, b: float, x: float) -> float:
    """Compute regularized incomplete beta function I_x(a, b) via continued fraction."""
    if x < 0.0 or x > 1.0:
        return 0.0
    if x == 0.0:
        return 0.0
    if x == 1.0:
        return 1.0

    # Symmetry transform if x > (a + 1) / (a + b + 2)
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - _regularized_incomplete_beta(b, a, 1.0 - x)

    # Factors in front of continued fraction
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(x) + b * math.log(1.0 - x) - lbeta) / a

    # Lentz's method for continued fraction
    f = 1.0
    c = 1.0
    d = 0.0
    tiny = 1e-30

    for m in range(1, 100):
        # Even step
        m2 = 2 * m
        numerator = (
            -(a + m) * (a + b + m) * x / ((a + m2) * (a + m2 + 1.0))
            if m > 0
            else -(a + b) * x / (a + 1.0)
        )
        if m == 1:
            d = 1.0 + numerator
        else:
            d = 1.0 + numerator * d
        if abs(d) < tiny:
            d = tiny
        d = 1.0 / d

        c = 1.0 + numerator / c
        if abs(c) < tiny:
            c = tiny
        f *= c * d

        # Odd step
        numerator = m * (b - m) * x / ((a + m2 - 1.0) * (a + m2))
        d = 1.0 + numerator * d
        if abs(d) < tiny:
            d = tiny
        d = 1.0 / d

        c = 1.0 + numerator / c
        if abs(c) < tiny:
            c = tiny
        delta = c * d
        f *= delta
        if abs(delta - 1.0) < 1e-10:
            break

    return front * (f - 1.0) if f != 1.0 else front


def _compute_p_value_from_t(t_stat: float, df: int) -> float:
    """Two-tailed p-value for Student's t-distribution with df degrees of freedom."""
    if df < 1:
        return 1.0
    if math.isnan(t_stat):
        return 1.0

    t2 = t_stat * t_stat
    x = df / (df + t2)
    try:
        p_val = _regularized_incomplete_beta(0.5 * df, 0.5, x)
        return min(max(p_val, 0.0), 1.0)
    except Exception:
        # Fallback to standard normal approximation if beta fails
        z = abs(t_stat)
        p_norm = math.erfc(z / math.sqrt(2.0))
        return min(max(p_norm, 0.0), 1.0)


def interpret_correlation(r: float) -> Tuple[str, str, str]:
    """Generate objective, non-causal interpretation based on documented thresholds.

    Thresholds:
        - |r| < 0.20: Negligible association
        - 0.20 <= |r| < 0.40: Weak association
        - 0.40 <= |r| < 0.70: Moderate association
        - 0.70 <= |r| <= 1.00: Strong association

    Returns:
        Tuple[str, str, str]: (direction, strength, textual_statement)
    """
    abs_r = abs(r)

    if abs_r < 0.20:
        strength = "negligible"
        direction = "negligible"
        desc = (
            f"The observed correlation coefficient (r = {r:.2f}) indicates a negligible or very weak "
            "statistical association between attendance percentage and academic marks in this cohort."
        )
    elif abs_r < 0.40:
        strength = "weak"
        direction = "positive" if r > 0 else "negative"
        desc = (
            f"The observed correlation coefficient (r = {r:.2f}) indicates a weak {direction} association. "
            f"Students with {'higher' if r > 0 else 'lower'} attendance demonstrate a slight tendency toward higher marks."
        )
    elif abs_r < 0.70:
        strength = "moderate"
        direction = "positive" if r > 0 else "negative"
        desc = (
            f"The observed correlation coefficient (r = {r:.2f}) indicates a moderate {direction} association. "
            f"There is an observable pattern where {'higher' if r > 0 else 'lower'} attendance co-occurs with higher marks."
        )
    else:
        strength = "strong"
        direction = "positive" if r > 0 else "negative"
        desc = (
            f"The observed correlation coefficient (r = {r:.2f}) indicates a strong {direction} linear relationship. "
            "A substantial degree of variance in marks corresponds with attendance trends."
        )

    return direction, strength, desc


def calculate_correlation(
    df: pd.DataFrame,
    col_x: str = "attendance_percentage",
    col_y: str = "average_marks",
) -> CorrelationResult:
    """Calculate Pearson and Spearman correlations with rigorous edge-case checking.

    Handles:
        - Missing values
        - Non-numeric entries
        - Fewer than 2 observations
        - Constant-valued columns (standard deviation == 0)
        - Empty datasets

    Returns:
        CorrelationResult
    """
    disclaimer = (
        "Important Academic Note: Correlation reflects statistical co-occurrence and does not "
        "establish causation. High attendance does not automatically guarantee higher marks, nor "
        "does low attendance definitively cause academic struggles without considering other factors."
    )

    if df.empty or len(df) == 0:
        return CorrelationResult(
            pearson_r=None,
            spearman_rho=None,
            p_value_pearson=None,
            p_value_spearman=None,
            t_statistic_pearson=None,
            valid_count=0,
            missing_count=0,
            is_valid=False,
            status="empty",
            interpretation="Not available: The current dataset or filtered selection is empty.",
            direction="undefined",
            strength="undefined",
            disclaimer=disclaimer,
        )

    if col_x not in df.columns or col_y not in df.columns:
        return CorrelationResult(
            pearson_r=None,
            spearman_rho=None,
            p_value_pearson=None,
            p_value_spearman=None,
            t_statistic_pearson=None,
            valid_count=0,
            missing_count=len(df),
            is_valid=False,
            status="missing_columns",
            interpretation=f"Not available: Missing required analysis columns ('{col_x}', '{col_y}').",
            direction="undefined",
            strength="undefined",
            disclaimer=disclaimer,
        )

    # Extract numeric series
    s_x = pd.to_numeric(df[col_x], errors="coerce")
    s_y = pd.to_numeric(df[col_y], errors="coerce")

    # Valid pairwise observations
    valid_mask = s_x.notna() & s_y.notna()
    x = s_x[valid_mask].values
    y = s_y[valid_mask].values

    valid_n = len(x)
    total_n = len(df)
    missing_n = total_n - valid_n

    if valid_n < 2:
        return CorrelationResult(
            pearson_r=None,
            spearman_rho=None,
            p_value_pearson=None,
            p_value_spearman=None,
            t_statistic_pearson=None,
            valid_count=valid_n,
            missing_count=missing_n,
            is_valid=False,
            status="insufficient_data",
            interpretation=(
                f"Not available: Fewer than 2 valid paired observations found ({valid_n} valid). "
                "At least 2 complete numeric observations are required to calculate correlation."
            ),
            direction="undefined",
            strength="undefined",
            disclaimer=disclaimer,
        )

    # Check for zero variance / constant column
    var_x = float(np.var(x, ddof=1)) if valid_n > 1 else 0.0
    var_y = float(np.var(y, ddof=1)) if valid_n > 1 else 0.0

    if var_x == 0.0 or var_y == 0.0 or np.isclose(var_x, 0.0) or np.isclose(var_y, 0.0):
        const_col = col_x if np.isclose(var_x, 0.0) else col_y
        return CorrelationResult(
            pearson_r=None,
            spearman_rho=None,
            p_value_pearson=None,
            p_value_spearman=None,
            t_statistic_pearson=None,
            valid_count=valid_n,
            missing_count=missing_n,
            is_valid=False,
            status="zero_variance",
            interpretation=(
                f"Not available: Zero variance detected in '{const_col}'. "
                "When all observations in a column are constant, Pearson and Spearman correlations are mathematically undefined."
            ),
            direction="undefined",
            strength="undefined",
            disclaimer=disclaimer,
        )

    # Compute Pearson r
    cov = float(np.cov(x, y, ddof=1)[0, 1])
    std_x = math.sqrt(var_x)
    std_y = math.sqrt(var_y)
    r_val = cov / (std_x * std_y)
    r_val = max(min(r_val, 1.0), -1.0)  # clamp to [-1, 1] due to float precision

    # Compute Spearman rank rho
    rank_x = pd.Series(x).rank().values
    rank_y = pd.Series(y).rank().values
    cov_rank = float(np.cov(rank_x, rank_y, ddof=1)[0, 1])
    std_rank_x = math.sqrt(float(np.var(rank_x, ddof=1)))
    std_rank_y = math.sqrt(float(np.var(rank_y, ddof=1)))
    rho_val = cov_rank / (std_rank_x * std_rank_y)
    rho_val = max(min(rho_val, 1.0), -1.0)

    # Pearson t-statistic and p-value
    df_resid = valid_n - 2
    if df_resid >= 1:
        denom = math.sqrt(max(1.0 - r_val * r_val, 1e-12))
        t_stat = r_val * math.sqrt(df_resid) / denom
        p_val_pearson = _compute_p_value_from_t(t_stat, df_resid)

        denom_rho = math.sqrt(max(1.0 - rho_val * rho_val, 1e-12))
        t_stat_rho = rho_val * math.sqrt(df_resid) / denom_rho
        p_val_spearman = _compute_p_value_from_t(t_stat_rho, df_resid)
    else:
        t_stat = None
        p_val_pearson = None
        p_val_spearman = None

    direction, strength, interp_text = interpret_correlation(r_val)

    return CorrelationResult(
        pearson_r=round(r_val, 3),
        spearman_rho=round(rho_val, 3),
        p_value_pearson=round(p_val_pearson, 4) if p_val_pearson is not None else None,
        p_value_spearman=round(p_val_spearman, 4) if p_val_spearman is not None else None,
        t_statistic_pearson=round(t_stat, 3) if t_stat is not None else None,
        valid_count=valid_n,
        missing_count=missing_n,
        is_valid=True,
        status="valid",
        interpretation=interp_text,
        direction=direction,
        strength=strength,
        disclaimer=disclaimer,
    )


def generate_correlation_report(res: CorrelationResult) -> str:
    """Generate a clean text/markdown report summarizing correlation results."""
    lines = [
        "# Correlation Analysis Report",
        "## Student Attendance & Academic Performance Correlation",
        "",
        f"- **Status**: {res.status.replace('_', ' ').title()}",
        f"- **Valid Observations**: {res.valid_count}",
        f"- **Missing / Excluded Records**: {res.missing_count}",
    ]

    if res.is_valid and res.pearson_r is not None:
        lines.extend(
            [
                f"- **Pearson Correlation (r)**: {res.pearson_r:.3f}",
                f"- **Spearman Rank Correlation (rho)**: {res.spearman_rho:.3f}",
                f"- **Pearson t-Statistic**: {res.t_statistic_pearson}",
                f"- **Pearson p-value**: {res.p_value_pearson} (assumes bivariate normal distribution)",
                f"- **Spearman p-value**: {res.p_value_spearman}",
                f"- **Relationship Direction**: {res.direction.capitalize()}",
                f"- **Relationship Strength**: {res.strength.capitalize()}",
                "",
                "### Plain-Language Interpretation",
                res.interpretation,
                "",
                "### Methodological & Ethical Disclaimer",
                res.disclaimer,
            ]
        )
    else:
        lines.extend(
            [
                "",
                "### Calculation Notice",
                res.interpretation,
            ]
        )

    return "\n".join(lines)
