# LangAgent/setup.py

# * LIBRARIES
from setuptools import setup, find_packages

# Load the README file as the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="langagent",  # The name of your package
    version="3.1.2",  # Initial version
    author="Kwadwo Daddy Nyame Owusu - Boakye",  # Author's name
    author_email="kwadwo.owusuboakye@outlook.com",  # Author's contact email
    description = (
        "LangAgent is a powerful multi-agent system designed to automate and streamline complex tasks, including research, "
        "automated code generation, logical reasoning, data analysis, business intelligence, trading insights, and dynamic reporting. "
    ),  # Detailed short description
    long_description=long_description,  # Long description from README.md
    long_description_content_type="text/markdown",  # Content type of README
    url="https://github.com/knowusuboaky/LangAgent",  # GitHub repository URL
    packages=find_packages(include=["langagent", "langagent.*"]),  # Automatically find all packages and submodules in langagent
    license="MIT",  # <-- Add this
    install_requires = [
    # LangChain Core & Extensions
    "langsmith",  # For managing and debugging LangChain apps
    "langchain==0.3.14",  # LangChain library
    "langchain_community==0.3.14",  # Community extensions for LangChain
    "langchain_openai==0.2.14",  # OpenAI integration for LangChain
    "langchain_experimental==0.3.4",  # Experimental LangChain features
    "langchain-groq==0.2.2",  # Groq integration for LangChain
    "langgraph==0.2.60",  # Graph-related utilities for LangChain

    # Core AI & NLP
    "torch",  # PyTorch for deep learning models
    "sentence-transformers>=2.2.2",  # For embeddings and text similarity
    "transformers",  # Hugging Face Transformers for NLP tasks
    "nltk==3.5",  # Natural Language Toolkit for NLP
    "tavily-python",  # AI-powered search & automation
    "beautifulsoup4>=4.9.3",  # Web scraping

    # Core Data Science
    "numpy>=1.21.0",  # Numerical computations
    "pandas>=1.1.0",  # Data manipulation
    "scikit-learn>=0.24.0",  # Machine learning models
    "statsmodels",  # Statistical modeling
    "matplotlib>=3.5.0",  # Visualization library
    "seaborn>=0.11.2",  # Statistical data visualization
    "altair==4.1.0",  # Declarative statistical visualization
    "ppscore==1.2.0",  # Predictive power score for feature selection
    "pyjanitor==0.20.14",  # Data cleaning & wrangling

    # Web Requests & Configuration Parsing
    "requests",  # HTTP requests library
    "pyyaml",  # YAML file parsing

    # Database & SQL
    "sqlalchemy>=2.0.0",  # ORM for database management
    "sqlite-utils",  # SQLite database tools
    "pymysql",  # MySQL support
    "psycopg2",  # PostgreSQL support

    # Financial & Trading Data
    "yfinance>=0.1.0",  # Yahoo Finance API
    "quantstats",  # Portfolio statistics & risk analysis

    # Excel & File Handling
    "xlsxwriter==1.3.7",  # Writing Excel files
    "openpyxl",  # Excel file reading & writing
    "pypdf2>=3.0.0",  # PDF parsing
    "python-pptx>=0.6.21",  # PowerPoint automation
    "python-docx>=0.8.11",  # Word document processing
    "nbformat>=4.2.0",  # Jupyter Notebook format support

    # Pandas Extensions & Utilities
    "pandas_flavor",  # Extend Pandas functionalities
    "numexpr>=2.8.4",  # Fast numerical expressions
    "pyowm>=3.3.0",  # OpenWeatherMap API

    # Visualization & Interactive Display
    "plotly>=5.0.0",  # Required for plotly, px, and graph_objects
    "ipython",  # Required for IPython.display (e.g., Image)
    "matplotlib>=3.5.0",  # Required for matplotlib.pyplot (plt)
    ],
    classifiers=[  # Optional classifiers for PyPI
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",  # Minimum Python version requirement
    keywords = [
    "AI",
    "machine learning",
    "language models",
    "multi-agent systems",
    "research automation",
    "code generation",
    "data analysis",
    "reasoning",
    "reporting",
    "LangChain",
    "LangSmith",
    "Python",
    "SQL",
    "data visualization",
    "automation",
    "OpenAI",
    "data science",
    "natural language processing",
    "deep learning",
    "document summarization",
    "web scraping",
    "APIs",
    "business intelligence",
    "feature engineering",
    "data preprocessing",
    "workflow optimization",
    "predictive modeling",
    "database querying",
    "data pipelines",
    "generative AI",
    "semantic search",
    "vector embeddings",
    "knowledge graphs",
    "GPT",
    "ML model deployment",
    "supervised learning",
    "unsupervised learning",
    "clustering",
    "data cleaning",
    "data wrangling",
    "topic modeling",
    "data storytelling",
    "decision support systems",
    "model explanations",
    "interactive dashboards",
    "EDA tools",
    "API integration",
    "text analytics",
    "clustering algorithms",
    "data enrichment",
    "regression models",
    "classification models",
    "time series analysis",
    "causal inference",
    "Bayesian models",
    "exploratory data analysis",
    "model interpretability",
    "knowledge extraction",
    "reasoning systems",
    "churn prediction",
    "customer insights",
    "transformers",
    "sentence transformers",
    "ChatGPT",
    "high-performance computing",
    "data-driven decision making",
    "real-time analytics",
    "data engineering",
    "data governance",
    "data security",
    "cloud-native applications",
    "streamlit",
    "financial modeling",
    "market research",
    "data quality assurance",
    "ETL processes",
    "cloud computing",
    "intelligent systems",
    "real-time processing",
    "AI-powered tools",
    "advanced analytics",
    "open source",
    "Bayesian networks",
    "data augmentation",
    "data dashboards",
    "natural language understanding",
    "knowledge discovery",
    "causal modeling",
    "data fusion",
    "AI workflows",
    "AI tools",
    "text generation",
    "machine reasoning",
    "algorithmic trading",
    "quantitative analysis",
    "hedge funds",
    "financial forecasting",
    "risk management",
    "technical analysis",
    "fundamental analysis",
    "portfolio optimization",
    "automated trading",
    "market sentiment analysis",
    "alternative data",
    "real-time trading signals",
    "stock price prediction",
    "algorithmic investing",
    "Monte Carlo simulations",
    "statistical arbitrage",
    "high-frequency trading",
    "trading strategies",
    "portfolio backtesting",
    "factor investing",
    "economic indicators",
    "macro trends",
    "trading AI",
    "stock market insights",
    "market anomaly detection",
    ],  # Keywords for discoverability
)
