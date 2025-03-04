# LangAgent/__init__.py

# Import agents from the research team
from .research_team.agents.researcher import create_researcher as researcher
from .research_team.agents.coder import create_coder as coder
from .research_team.agents.weather import create_weather as weather

# Import agents from the logic team
from .logic_team.agents.calculator import create_calculator as calculator
from .logic_team.agents.reasoner import create_reasoner as reasoner

# Import agents from the business intelligence team
from .business_intelligence_team.agents.bi_analyst_agent import create_bi_analyst as bi_analyst

# Import agents from the data science team
from .data_science_team.agents.data_cleaning_agent import make_data_cleaning_agent as data_cleaning_agent
from .data_science_team.agents.data_wrangling_agent import make_data_wrangling_agent as data_wrangling_agent
from .data_science_team.agents.feature_engineering_agent import make_feature_engineering_agent as feature_engineering_agent
from .data_science_team.agents.sql_database_agent import make_sql_database_agent as sql_database_agent

# Import agents from the trading team
from .trading_team.agents.fundamentals_analyst import make_fundamentals_agent as fundamentals_agent
from .trading_team.agents.sentiments_analyst import make_sentiments_agent as sentiments_agent
from .trading_team.agents.technicals_analyst import make_technicals_agent as technicals_agent
from .trading_team.agents.valuations_analyst import make_valuations_agent as valuations_agent
from .trading_team.agents.risk_manager import make_risk_manager_agent as risk_manager_agent
from .trading_team.agents.portfolio_manager import make_portfolio_manager_agent as portfolio_manager_agent

# Import agents from the text clustering team
from .text_clustering_team.agents.topic_generator import create_topic_generator as topic_generator

# Import agents from the reporting team
from .reporting_team.agents.interpreter import create_interpreter as interpreter
from .reporting_team.agents.summarizer import create_summarizer as summarizer

# Import supervisor chain
from .supervisor.supervisor_chain import create_supervisor_chain as supervisor_chain

# Define what will be accessible when doing `from LangAgent import *`
__all__ = [
    # Research team agents
    'researcher', 'coder', 'weather',
    # Logic team agents
    'calculator', 'reasoner',
    # Business intelligence team agents
    'bi_analyst',
    # Data science team agents
    'data_cleaning_agent', 'data_wrangling_agent', 'feature_engineering_agent', 'sql_database_agent',
    # Trading team agents
    'fundamentals_agent', 'sentiments_agent', 'technicals_agent', 'valuations_agent', 'risk_manager_agent', 'portfolio_manager_agent',
    # Text clustering team agents
    'topic_generator',
    # Reporting team agents
    'interpreter', 'summarizer',
    # Supervisor chain
    'supervisor_chain'
]
