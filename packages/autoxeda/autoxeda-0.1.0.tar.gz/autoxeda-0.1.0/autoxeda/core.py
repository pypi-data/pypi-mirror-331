# Copyright (C) 2023 Jahanzeb Ahmed
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# AutoxEDA any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# For Guidance reach me out through email jahanzebahmed.mail@gmail.com, or through my website <https://jahanzebahemd.netlify.app/>

import pandas as pd
import numpy as np
import json
import requests
import time
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import seaborn as sns
import statsmodels.api as sm
from scipy import stats
import scipy
import re
from langchain.memory import ConversationBufferMemory
from scipy.stats import shapiro  # Shapiro-Wilk test for normality
from scipy.stats import kstest   # Kolmogorov-Smirnov test for normality
from scipy.stats import f_oneway # ANOVA (requires grouped data handling separately)
from scipy.stats import chi2_contingency  # Chi-squared goodness of fit (with contingency table)
from scipy.stats import levene   # Levene's test for equal variances
from scipy.stats import pearsonr # Pearson correlation test
from scipy.stats import spearmanr # Spearman rank correlation test
from scipy.stats import f        # F-test for variance comparison (used with scipy.stats.f.cdf)
from statsmodels.tsa.stattools import adfuller  # Augmented Dickey-Fuller test for stationarity
from scipy.stats import jarque_bera  # Jarque-Bera test for skewness and kurtosis
from statsmodels.stats.diagnostic import het_breuschpagan  # Breusch-Pagan test (requires regression residuals)
from statsmodels.stats.stattools import durbin_watson  # Durbin-Watson test for autocorrelation
from statsmodels.stats.outliers_influence import variance_inflation_factor  # VIF for multicollinearity
from scipy.stats import anderson  # Anderson-Darling test for distribution fit
from statsmodels.tsa.stattools import acf  # Needed for Ljung-Box test (via statsmodels)
from statsmodels.stats.diagnostic import acorr_ljungbox  # Ljung-Box test for residual independence
from statsmodels.tsa.stattools import grangercausalitytests  # Granger causality test
from statsmodels.tsa.seasonal import seasonal_decompose  # Time-series decomposition (used in visualizations)
from statsmodels.graphics.gofplots import qqplot  # Q-Q plot for normality checking
from pandas.plotting import lag_plot  # Lag plot for autocorrelation
from tqdm import tqdm

# Custom JSON Encoder (unchanged)
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (pd.Series, pd.DataFrame)):
            return obj.to_dict()
        elif isinstance(obj, Axes):
            return "Matplotlib Axes object"
        elif isinstance(obj, Figure):
            return "Matplotlib Figure object"
        elif hasattr(obj, 'dtype'):
            return str(obj)
        return super(NumpyEncoder, self).default(obj)

load_dotenv()

# GroqLLM Class (unchanged)
class GroqLLM:
    def __init__(self, api_key, endpoint="https://api.groq.com/openai/v1/chat/completions", model="qwen-2.5-coder-32b"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model

    def call(self, prompt, system_prompt=None, max_tokens=2000):
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens
        }
        for attempt in range(3):
            try:
                response = requests.post(self.endpoint, headers=headers, json=data)
                response.raise_for_status()  # Raises exception for 4xx/5xx errors
                return response.json()["choices"][0]["message"]["content"]
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"Rate limit hit. Retry {attempt + 1}/{retries} in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Error in LLM call: {e}")
                    return None
            except Exception as e:
                print(f"Error in LLM call: {e}")
                return None
        print("Max retries exceeded for LLM call.")
        return None

# Helper Function to Extract JSON
def extract_json(response):
    """Extract and clean JSON from LLM response."""
    start = response.find('{')
    end = response.rfind('}') + 1
    if start != -1 and end != -1:
        json_str = response[start:end]
        json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas before }
        json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas before ]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Failed to parse cleaned JSON: {e}")
            return None
    return None

def compute_initial_summary(df):
    summary = {
        "general": {
            "n_rows": len(df),
            "n_cols": len(df.columns),
            "data_types_overview": {str(k): int(v) for k, v in df.dtypes.value_counts().to_dict().items()},  # Convert keys to strings
            "total_missing": int(df.isnull().sum().sum()),
            "missing_percentage": float(df.isnull().sum().sum() / df.size * 100),
            "duplicated_rows": int(df.duplicated().sum())
        },
        "columns": {},
        "overall": {}
    }

    # Define numeric columns for later use
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    # Column-wise summaries
    for col in df.columns:
        col_summary = {
            "data_type": str(df[col].dtype),  # Convert dtype to string
            "missing_count": int(df[col].isnull().sum()),
            "missing_percentage": float(df[col].isnull().mean() * 100)
        }
        
        if np.issubdtype(df[col].dtype, np.number):
            # Convert all numpy types to native Python types
            desc_stats = {k: float(v) if isinstance(v, (np.floating, np.integer)) else v 
                         for k, v in df[col].describe().to_dict().items()}
            Q1, Q3 = df[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            iqr_outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)][col].count()
            if df[col].std() != 0:
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                z_outliers = int((z_scores > 3).sum())
            else:
                z_outliers = 0
            skewness = df[col].skew()
            if abs(skewness) > 1:
                dist_note = "highly skewed"
            elif abs(skewness) > 0.5:
                dist_note = "moderately skewed"
            else:
                dist_note = "approximately symmetric"
            col_summary.update({
                "descriptive_stats": desc_stats,
                "skewness": float(skewness),
                "kurtosis": float(df[col].kurt()),
                "iqr_outliers": int(iqr_outliers),
                "z_score_outliers": z_outliers,
                "distribution_note": dist_note
            })
        elif df[col].dtype == "object" or pd.api.types.is_categorical_dtype(df[col]):
            unique_vals = df[col].nunique()
            total_vals = df[col].count()
            if unique_vals == total_vals:
                top_cat = None
                top_freq = 1
                balance_note = "all unique values (likely an ID column)"
            else:
                top_cat = df[col].mode().iloc[0] if not df[col].mode().empty else None
                # Convert to string if it's an object that might not be JSON serializable
                if top_cat is not None and not isinstance(top_cat, (str, int, float, bool)):
                    top_cat = str(top_cat)
                top_freq = int(df[col].value_counts().iloc[0]) if not df[col].value_counts().empty else 0
                balance_note = "highly imbalanced" if top_freq / total_vals > 0.9 else "balanced"
            col_summary.update({
                "unique_values": unique_vals,
                "top_category": top_cat,
                "top_category_frequency": top_freq,
                "balance_note": balance_note
            })
        summary["columns"][col] = col_summary

    if len(numeric_cols) == 0:
        summary["overall"]["top_pearson_correlations"] = {}
        summary["overall"]["top_spearman_correlations"] = {}
        return summary

    # Compute Pearson correlation, using only the upper triangle to avoid duplicates
    pearson_corr = df[numeric_cols].corr(method='pearson').abs()
    mask = np.triu(np.ones(pearson_corr.shape), k=1).astype(bool)
    top_pearson = pearson_corr.where(mask).stack().dropna().sort_values(ascending=False).head(5)
    # Convert tuple keys to strings
    top_pearson = {str(k): float(v) for k, v in top_pearson.to_dict().items()}  # Convert values to float

    # Compute Spearman correlation, using only the upper triangle to avoid duplicates
    spearman_corr = df[numeric_cols].corr(method='spearman').abs()
    top_spearman = spearman_corr.where(mask).stack().dropna().sort_values(ascending=False).head(5)
    top_spearman = {str(k): float(v) for k, v in top_spearman.to_dict().items()}  # Convert values to float
    
    summary["overall"]["top_pearson_correlations"] = top_pearson
    summary["overall"]["top_spearman_correlations"] = top_spearman

    non_linear_flags = []
    for pair in top_spearman.keys():
        if pair in top_pearson and top_spearman[pair] > top_pearson[pair] + 0.2:
            non_linear_flags.append(pair)
    if non_linear_flags:
        summary["overall"]["non_linear_flags"] = non_linear_flags

    return summary

def get_approved_options(analysis_type):
    """
    Returns a dictionary of approved tests, visualizations, and insights based on analysis type.

    Parameters:
    - analysis_type (str): "business" or "prediction".

    Returns:
    - dict: Options categorized by tests, visualizations, and insights.
    """
    if analysis_type == "business":
        options = {
            "tests": [
                "Test for normality using Shapiro-Wilk",              # Basic normality test
                "Test for normality using Kolmogorov-Smirnov",        # Alternative normality test
                "Conduct ANOVA on specified groups",                  # Group comparison
                "Chi-squared goodness of fit",                        # Categorical fit test
                "Levene's test for equal variances",                  # Variance equality
                "Pearson correlation test",                           # Linear correlation
                "Spearman rank correlation test",                     # Non-linear correlation
                "F-test for variance comparison",                     # Variance ratio test
                "Trend analysis using Mann-Kendall test"              # Monotonic trend detection
            ],
            "visualizations": [
                "Generate a box plot for outlier detection",          # Outlier visualization
                "Generate a histogram with density plot",             # Distribution shape
                "Generate a correlation heatmap",                     # Variable relationships
                "Generate a bar chart for categorical frequencies",   # Categorical counts
                "Generate a line plot for trend analysis",            # Temporal trends
                "Generate a pie chart for category proportions",      # Categorical proportions
                "Generate a violin plot for distribution spread",     # Detailed distribution
                "Generate a stacked bar chart for group comparison",  # Grouped categorical data
                "Generate a heatmap for missing data patterns"        # Missing value visualization
            ],
            "business_insights": [
                "Provide business insights from the distribution",    # Distribution-based insights
                "Suggest transformations for skewed data",            # Data normalization suggestions
                "Recommend segmentation analysis",                    # Customer/market segmentation
                "Compute YoY/MoM growth rates",                       # Growth metrics
                "Analyze variance impact on business metrics",        # Variance effects
                "Estimate profitability trends",                      # Profit-related insights
                "Identify key drivers using correlation analysis",    # Driver identification
                "Compute customer lifetime value proxies",            # CLV estimation
                "Suggest pricing strategy based on distribution"      # Pricing insights
            ]
        }
    elif analysis_type == "prediction":
        options = {
            "tests": [
                "Test for normality using Shapiro-Wilk",              # Basic normality test
                "Test for normality using Kolmogorov-Smirnov",        # Alternative normality test
                "Conduct ANOVA on specified groups",                  # Group comparison
                "Augmented Dickey-Fuller test",                       # Stationarity test
                "Jarque-Bera test",                                   # Skewness and kurtosis test
                "Breusch-Pagan heteroskedasticity test",              # Heteroskedasticity test
                "Durbin-Watson test for autocorrelation",             # Autocorrelation test
                "Variance Inflation Factor (VIF) for multicollinearity", # Multicollinearity test
                "Anderson-Darling test for distribution fit",         # Distribution goodness-of-fit
                "Ljung-Box test for residual independence",           # Residual randomness test
                "Granger causality test"                              # Causality between variables
            ],
            "visualizations": [
                "Generate a box plot for outlier detection",          # Outlier visualization
                "Generate a histogram with density plot",             # Distribution shape
                "Generate a correlation heatmap",                     # Variable relationships
                "Generate a residual plot",                           # Model residual analysis
                "Generate a Q-Q plot",                                # Normality check
                "Generate a time-series decomposition plot",          # Trend/seasonality visualization
                "Generate a feature importance plot",                 # Predictive feature ranking
                "Generate a partial dependence plot",                 # Feature effect visualization
                "Generate a lag plot for autocorrelation",            # Lag relationships
                "Generate a pairplot with regression lines"           # Pairwise relationships
            ],
            "prediction_insights": [
                "Provide insights on variable predictive power",      # Feature importance
                "Suggest feature transformation based on skewness",   # Transformation recommendations
                "Recommend dimensionality reduction (PCA) visualization", # PCA suggestion
                "Compute information value (IV) for predictors",      # IV for feature selection
                "Provide model validation test recommendations",      # Validation suggestions
                "Analyze outlier impact on predictive performance",   # Outlier effects
                "Suggest interaction terms for model improvement",    # Interaction features
                "Compute feature stability over subsets",             # Feature consistency
                "Recommend cross-validation strategies"               # CV recommendations
            ]
        }
    else:
        raise ValueError("analysis_type must be 'business' or 'prediction'")
    return options


def build_context_summary(context):
    """Build a concise summary from context actions only (exclude full prompt history)."""
    summary_lines = []
    for action in context.get("actions", []):
        # Extract relevant parts from each iteration's output
        line = f"Iteration {action['iteration']}: Action -> {action['llm_decision'].get('recommended_action','')}, " \
               f"Result -> {action['action_result']}"
        summary_lines.append(line)
    return "\n".join(summary_lines)


SYSTEM_PROMPT = """
You are an expert data analyst assisting with an Automated Exploratory Data Analysis (AutoEDA) process. Your task is to analyze a DataFrame 'df' iteratively and provide recommendations or insights based on the given 'analysis_type' ("business" or "prediction").

### Rules for Responses:
1. **Regular Iterations (1 to n):**
   - Use Detail_Level as {0}, and Temperature as {1}, where Detail_Level is defined as either Intermediate, Basic or Advance that control you analysis level. Temperature (0-1) on the other hand is used to control the creativity of your response.
   - Respond **strictly in JSON format** with no extra text outside the JSON object.
   - The JSON must include:
     - 'recommended_action': One of the approved options (tests, visualizations, insights).
     - 'columns': List of column names from 'df' to apply the action.
     - 'code': Python code to execute the action, assigning the output to 'result'.
     - 'rationale': Brief explanation of why this action was chosen.
     - 'confidence_interval': If applicable, otherwise null.
   - Use only valid methods and columns provided in the prompt.
   - Do not repeat actions unless justified by new insights.

2. **Final Iteration (n+1):**
   - Do **not** return JSON. Instead, provide a detailed text report.
   - Analyze the entire context from all previous iterations.
   - If 'analysis_type' is "business":
     - Structure the report with sections (e.g., Summary, Key Findings, Business Recommendations).
     - Focus on insights for business understanding.
   - If 'analysis_type' is "prediction":
     - Provide advanced analysis (e.g., trends, correlations, predictive potential).
     - Include insights relevant to predictive modeling.
   - Use the full context provided to inform your analysis.

3. **Purpose of Iterations:**
   - Each regular iteration builds understanding of the data (e.g., via tests, visualizations, or insights).
   - The final iteration synthesizes all findings into a comprehensive analysis tailored to the 'analysis_type'.
Note: Make sure to Understand Discriptive statistics as much as possible, and account for more Tests then visualizations. For Business lean your analysis toward business analysis, and for prediction lean toward prediction analysis. Make sure No Visualization or Test should be repeated again unless necessary for deeper understanding.
Follow these instructions precisely for each iteration. (Do not cause any error in Json response as it need to programatically parsed.)
"""

# Updated build_prompt
def build_prompt(context, iteration, options, analysis_type, df, is_final=False):
    context_summary = build_context_summary(context)
    insight_key = "business_insights" if analysis_type == "business" else "prediction_insights"
    
    if not is_final:
        prompt = (
            f"Iteration {iteration} of AutoXEDA Dynamic Analysis:\n"
            f"The DataFrame is named 'df' and has the following columns: {list(df.columns)}\n"
            "Past Action Outputs:\n"
            f"{context_summary}\n\n"
            "Approved Methods:\n"
            "Tests: " + ", ".join(options["tests"]) + "\n"
            "Visualizations: " + ", ".join(options["visualizations"]) + "\n"
            "Insights: " + ", ".join(options[insight_key]) + "\n\n"
            "Based on the above context, choose the next best action. "
            "Return your recommendation as a JSON object with keys:\n"
            "  'recommended_action' (one of the approved options),\n"
            "  'columns' (column name(s) to apply the action),\n"
            "  'code' (Python code; assign output to 'result' - e.g., test stats or plot filename),\n"
            "  'rationale' (brief explanation),\n"
            "  'confidence_interval' (if applicable).\n"
            "Use 'df' as the DataFrame name and valid columns from {list(df.columns)}. "
            "Return only the JSON object, no extra text."
        )
    else:
        prompt = (
            f"Final Iteration of AutoXEDA Analysis:\n"
            f"The DataFrame is 'df' with columns: {list(df.columns)}\n"
            f"Analysis Type: {analysis_type}\n"
            "Provide a comprehensive analysis based on all previous iterations. "
            "Structure your response as a detailed text report (not JSON) based on the 'analysis_type':\n"
            "- For 'business': Include sections like Summary, Key Findings, Business Recommendations.\n"
            "- For 'prediction': Provide advanced analysis, trends, and insights for predictive modeling.\n"
            "Current context:\n" + json.dumps(context, cls=NumpyEncoder)
        )
    return prompt


def execute_generated_code(code, df):
    """
    Executes dynamically generated Python code in a restricted environment.
    The code should assign its output to a variable named 'result'.
    Only allowed libraries and the DataFrame 'df' are provided.
    """
    allowed_globals = {
        "pd": pd,
        "np": np,
        "stats": stats,
        "sm": sm,
        "plt": plt,
        "df": df,
        "__builtins__": __builtins__  # In production, further restrict built-ins as needed.
    }
    local_env = {}
    try:
        exec(code, allowed_globals, local_env)
        result = local_env.get("result", None)
        # Convert any numpy types to Python native types
        if result is not None:
            if isinstance(result, dict):
                # Use custom JSON encoder to convert types
                result = json.loads(json.dumps(result, cls=NumpyEncoder))
        return result
    except Exception as e:
        raise RuntimeError(f"Error executing generated code: {e}")

# Updated execute_action
def execute_action(decision, df, groq_llm, retries):
    max_retries = retries
    retries = 0
    code = decision.get("code", "")
    while retries < max_retries:
        try:
            result = execute_generated_code(code, df)
            if result is None:
                raise RuntimeError("No result returned from executed code.")
            return result
        except Exception as e:
            print(f"Error during code execution (retry {retries+1}): {e}")
            error_prompt = (
                f"The previous code failed with error: {e}\n"
                f"The DataFrame is 'df' with columns: {list(df.columns)}\n"
                "Original decision: " + json.dumps(decision, cls=NumpyEncoder) + "\n"
                "Provide a corrected JSON object with the same keys. Ensure 'code' uses valid arguments for pandas and matplotlib (e.g., 'color' instead of 'colormap' for DataFrame.hist, or use plt.hist for colormaps). Assign the output to 'result'."
            )
            fixed_response = groq_llm.call(error_prompt, system_prompt=SYSTEM_PROMPT, max_tokens=1000)
            fixed_decision = extract_json(fixed_response)
            if fixed_decision and "code" in fixed_decision:
                code = fixed_decision["code"]
                retries += 1
            else:
                print("Failed to get a valid fixed response from LLM.")
                retries += 1
    print("Execution failed after retries; skipping.")
    return {"error": "Execution failed after retries."}

def print_final_output(context):
    # Header for the summary
    print("\n" + "="*140)
    print("FINAL AUTOXEDA ANALYSIS SUMMARY".center(80))
    print("="*140)
    
    # Create a summary DataFrame from the actions
    action_data = []
    for action in context["actions"]:
        iteration = action["iteration"]
        decision = action["llm_decision"]
        result = action["action_result"]
        action_data.append({
            "Iteration": iteration,
            "Recommended Action": decision["recommended_action"],
            "Columns": ", ".join(decision["columns"]),
            "Rationale": decision["rationale"],
            "Action Result": str(result)  # Convert result to string for display
        })
    summary_df = pd.DataFrame(action_data)
    
    # Display the DataFrame
    print("\nAnalysis Summary Table:\n")
    print(summary_df.to_string(index=False))
    
    # Display the final analysis text
    if "final_analysis" in context:
        print("\n" + "="*140)
        print("FINAL ANALYSIS".center(80))
        print("="*140)
        print(context["final_analysis"])
        print("="*140)
    else:
        print("\nNo final analysis text available.")

# Updated autoeda
def autoeda(data, analysis_type="business", api_key=None, max_retries = 2, columns = None, detail_level = 'intermediate', temperature = 1 ):
    global SYSTEM_PROMPT
    SYSTEM_PROMPT = SYSTEM_PROMPT.format(detail_level, temperature)

    # Validate analysis_type
    if analysis_type not in ["business", "prediction"]:
        raise ValueError("analysis_type must be 'business' or 'prediction'")

    # Validate detail_level
    valid_detail_levels = ["basic", "intermediate", "advanced"]
    if detail_level not in valid_detail_levels:
        raise ValueError(f"detail_level must be one of {valid_detail_levels}, got '{detail_level}'")

    # Validate temperature
    if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 1:
        raise ValueError("temperature must be a number between 0.0 and 1.0")

    # Handle different input types and convert to pandas DataFrame
    if isinstance(data, pd.DataFrame):
        # Input is already a DataFrame, no conversion needed
        df = data
    elif isinstance(data, str):
        # Input is a string, could be a file path or SQL query
        if data.lower().endswith('.csv'):
            if not os.path.exists(df):
                raise FileNotFoundError(f"CSV file '{df}' not found.")
            df = pd.read_csv(data)
        elif data.lower().endswith(('.xls', '.xlsx')):
            if not os.path.exists(df):
                raise FileNotFoundError(f"Excel file '{data}' not found.")
            df = pd.read_excel(data)
        elif data.strip().lower().startswith(('select', 'with')) and sql_conn is not None:
            # Assume it's an SQL query if it starts with SELECT/WITH and sql_conn is provided
            if isinstance(sql_conn, str):
                engine = create_engine(sql_conn)
                df = pd.read_sql(data, engine)
            else:
                # Assume sql_conn is already an engine/connection object
                df = pd.read_sql(data, sql_conn)
        else:
            raise ValueError("String input must be a CSV/Excel file path or SQL query with sql_conn.")
    else:
        raise ValueError("Input must be a pandas DataFrame, CSV file path, Excel file path, or SQL query.")

    if columns is not None:
      missing_cols = [col for col in columns if col not in df.columns]
      if missing_cols:
        raise ValueError(f"Columns {missing_cols} not found in DataFrame.")
      df = df[columns]

    iterations = None
    if iterations is None:
        iterations = 6 if analysis_type == "business" else 10

    # Handle API key
    DEFAULT_API_KEY = os.getenv('GROQ_API_KEY')
    if api_key is None:
        api_key = DEFAULT_API_KEY  # Use in-system key if None
    else:
        # Validate the provided API key
        test_prompt = "Hello"  # Minimal test prompt
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        data = {
            "model": "qwen-2.5-coder-32b",  # Replace with your default model
            "messages": [{"role": "user", "content": test_prompt}],
            "max_tokens": 10
        }
        try:
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()  # Raises exception for 4xx/5xx errors
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValueError("Invalid API key provided. Please provide a valid LLM API key (obtain one from Groq or OpenAI).")
            else:
                raise ValueError(f"API key validation failed: {str(e)}. Check your key and network connection.")
        except Exception as e:
            raise ValueError(f"Error validating API key: {str(e)}. Ensure the key is correct and the service is accessible.")

    total_steps = iterations
    memory = ConversationBufferMemory(return_messages=True)
    initial_summary = compute_initial_summary(df)
    context = {"analysis_type": analysis_type, "initial_summary": initial_summary, "actions": []}
    groq_llm = GroqLLM(api_key=api_key)
    options = get_approved_options(analysis_type)

    with tqdm(total=total_steps, desc="AutoXEDA Progress", unit="step") as pbar:
      # Regular iterations (1 to n)
      for i in range(1, iterations + 1):
          prompt = build_prompt(context, i, options, analysis_type, df, is_final=False)
          memory.save_context({"input": prompt}, {"output": ""})
          llm_response = groq_llm.call(prompt, system_prompt=SYSTEM_PROMPT, max_tokens=1000)
          time.sleep(3)
          if not llm_response:
              print(f"LLM call failed at iteration {i}")
              continue
    
          decision = extract_json(llm_response)
          if not decision:
              print(f"Error parsing LLM response at iteration {i}: {llm_response}")
              continue
    
          action_result = execute_action(decision, df, groq_llm, max_retries)
          context["actions"].append({"iteration": i, "llm_decision": decision, "action_result": action_result})
          memory.save_context({"input": f"Iteration {i} results"}, {"output": json.dumps(action_result, cls=NumpyEncoder)})
          time.sleep(6)
          pbar.update(1)
    
    # Final iteration (n+1)
    final_prompt = build_prompt(context, iterations + 1, options, analysis_type, df, is_final=True)
    memory.save_context({"input": final_prompt}, {"output": ""})
    final_response = groq_llm.call(final_prompt, system_prompt=SYSTEM_PROMPT, max_tokens=2000)  # Increased for detailed report
    if final_response:
        context["final_analysis"] = final_response
    else:
        print("LLM call failed for final analysis")
    pbar.update(1)

    print_final_output(context)
    return context
    
#-------------------------------------------------------------< END >-----------------------------------------------------------------
# Author: Jahanzeb Ahmed 
# Email: jahanzebahmed.mail@gmail.com




