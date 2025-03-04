# LangAgent/setup.py

# * LIBRARIES
from setuptools import setup, find_packages

# Load the README file as the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="langagent",  # The name of your package
    version="3.3.9",  # Initial version
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
    # LangChain & AI Frameworks
    "langchain",
    "langchain-community",
    "langchain-core",
    "langchain-experimental",
    "langchain-groq",
    "langchain-openai",
    "langchain-text-splitters",
    "langgraph==0.3.2",
    "langsmith>=0.1.125",

    # AI-powered Search & NLP
    "tavily-python",
    "sentence-transformers>=2.2.2",

    # Jupyter & Interactive Tools
    "ipython==8.18.0",
    "ipywidgets==8.1.2",
    "nbformat>=4.2.0",

    # Data Science & Visualization
    "plotly>=5.0.0",
    "matplotlib>=3.5.0",
    "seaborn>=0.11.2",
    "tqdm>=4.0.0",
    "numpy>=1.21.0",
    "pandas>=1.1.0",
    "numexpr>=2.8.4",
    "pyjanitor==0.20.14",  # Data cleaning & wrangling

    # Web Scraping & APIs
    "requests>=2.25.1",
    "beautifulsoup4>=4.9.3",
    "pyowm>=3.3.0",  # OpenWeatherMap API

    # Cloud & Infrastructure
    "kubernetes==29.0.0",

    # Financial & Trading Data
    "yfinance>=0.1.0",

    # File Handling & Document Processing
    "PyYAML>=6.0",  # YAML parsing
    "pypdf2>=3.0.0",  # PDF processing
    "python-pptx>=0.6.21",  # PowerPoint automation
    "python-docx>=0.8.11",  # Word document processing
    "xlsxwriter==1.3.7",  # Writing Excel files
    "openpyxl",  # Excel file reading & writing

    # Database & SQL
    "sqlalchemy>=2.0.0",
    "sqlite-utils",  # SQLite database tools
    "pymysql",  # MySQL support
    "psycopg2",  # PostgreSQL support
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
