from dotenv import load_dotenv
import psycopg2 as ps
import os
from sqlalchemy import Table, Column, MetaData, Integer, Computed