import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import squarify
import numpy as np
import warnings

# Suppress warnings for cleaner output
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

# Set aesthetic styles
sns.set_style("darkgrid")
sns.set_palette("pastel")
plt.style.use("ggplot")

def plot(data, x=None, y=None, kind=None, **kwargs):
    """
    Generate quick visualizations based on the data type and parameters.
    
    Parameters:
        data (pd.DataFrame or pd.Series): The dataset to visualize.
        x (str, optional): Column name for the x-axis.
        y (str, optional): Column name for the y-axis.
        kind (str, optional): Type of plot ('hist', 'scatter', 'box', etc.).
        **kwargs: Additional arguments for Seaborn or Matplotlib.
    """
    if isinstance(data, pd.Series):
        kind = kind or 'hist'
        sns.histplot(data, kde=True, color='royalblue', **kwargs)
    elif isinstance(data, pd.DataFrame):
        if x and y:
            kind = kind or 'scatter'
            if kind == 'scatter':
                sns.scatterplot(data=data, x=x, y=y, hue=y, palette='coolwarm', **kwargs)
            elif kind == 'line':
                sns.lineplot(data=data, x=x, y=y, color='darkorange', linewidth=2, **kwargs)
            elif kind == 'box':
                sns.boxplot(data=data, x=x, y=y, palette='viridis', **kwargs)
            elif kind == 'bar':
                sns.barplot(data=data, x=x, y=y, palette='crest', **kwargs)
            elif kind == 'bubble':
                plt.scatter(data[x], data[y], s=np.abs(data[y]) * 0.1, alpha=0.6, color='mediumseagreen')
            elif kind == 'area':
                plt.fill_between(data[x], data[y], color='teal', alpha=0.5)
            elif kind == 'heatmap':
                sns.heatmap(data[[x, y]].corr(), annot=True, cmap='coolwarm', linewidths=0.5)
            elif kind == 'pie':
                data.groupby(x)[y].sum().plot.pie(autopct='%1.1f%%', cmap='Set3')
            elif kind == 'donut':
                data.groupby(x)[y].sum().plot.pie(autopct='%1.1f%%', cmap='Set3', wedgeprops={'width': 0.4})
            elif kind == 'treemap':
                squarify.plot(sizes=data[y].values, label=data[x].values, alpha=0.7, color=sns.color_palette("Spectral", len(data)))
            elif kind == 'density':
                sns.kdeplot(data=data, x=x, y=y, cmap='magma', fill=True)
            else:
                print("Error: Unsupported plot type.")
                return
        elif x:
            kind = kind or 'hist'
            sns.histplot(data[x], kde=True, color='slateblue', **kwargs)
        else:
            print("Error: Please specify x and/or y for DataFrame plots.")
            return
    else:
        print("Error: Input data must be a Pandas DataFrame or Series.")
        return
    
    plt.show()

def explore(data):
    """
    Perform automatic exploratory data analysis, detecting numerical and categorical columns.
    """
    if not isinstance(data, pd.DataFrame):
        print("Error: Input data must be a Pandas DataFrame.")
        return
    
    print("Dataset Overview:")
    print(data.info())
    print("\nMissing Values:")
    print(data.isnull().sum())
    print("\nSummary Statistics:")
    print(data.describe())
    
    num_cols = data.select_dtypes(include=['number']).columns.tolist()
    cat_cols = data.select_dtypes(exclude=['number']).columns.tolist()
    
    print("\nDetected Numerical Columns:", num_cols)
    print("Detected Categorical Columns:", cat_cols)
    
    for col in num_cols:
        plt.figure(figsize=(6, 4))
        sns.histplot(data[col], kde=True, color='royalblue')
        plt.title(f'Distribution of {col}')
        plt.show()
        
        plt.figure(figsize=(6, 4))
        sns.boxplot(y=data[col], palette='Set2')
        plt.title(f'Boxplot of {col}')
        plt.show()
    
    for col in cat_cols:
        plt.figure(figsize=(6, 4))
        sns.countplot(y=data[col], order=data[col].value_counts().index, palette='coolwarm')
        plt.title(f'Count of {col}')
        plt.show()
    
    if len(num_cols) > 1:
        plt.figure(figsize=(8, 6))
        sns.heatmap(data[num_cols].corr(), annot=True, cmap='coolwarm', linewidths=0.5)
        plt.title('Correlation Heatmap')
        plt.show()
    
    if len(num_cols) > 1:
        for i in range(len(num_cols) - 1):
            for j in range(i + 1, len(num_cols)):
                plt.figure(figsize=(6, 4))
                sns.scatterplot(data=data, x=num_cols[i], y=num_cols[j], hue=num_cols[i], palette='magma')
                plt.title(f'Scatter Plot: {num_cols[i]} vs {num_cols[j]}')
                plt.show()
    
    print("Exploratory Data Analysis completed!")
