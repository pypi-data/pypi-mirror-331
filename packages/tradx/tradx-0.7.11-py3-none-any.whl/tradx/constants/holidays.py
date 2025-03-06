"""
This module defines a list of holidays and special trading days for 2024 and 2025.

These lists can be used for applications like holiday validation, event scheduling, 
and financial market operations.
"""
from datetime import datetime

holidays = [
    datetime(2024, 12, 25).date(),  # Christmas
    datetime(2025, 2, 26).date(),  # Mahashivratri
    datetime(2025, 3, 14).date(),  # Holi
    datetime(2025, 3, 31).date(),  # Id-Ul-Fitr (Ramadan Eid)
    datetime(2025, 4, 10).date(),  # Shri Mahavir Jayanti
    datetime(2025, 4, 14).date(),  # Dr. Baba Saheb Ambedkar Jayanti
    datetime(2025, 4, 18).date(),  # Good Friday
    datetime(2025, 5, 1).date(),  # Maharashtra Day
    datetime(2025, 8, 15).date(),  # Independence Day
    datetime(2025, 8, 27).date(),  # Ganesh Chaturthi
    datetime(2025, 10, 2).date(),  # Mahatma Gandhi Jayanti/Dussehra
    datetime(2025, 10, 21).date(),  # Diwali Laxmi Pujan
    datetime(2025, 10, 22).date(),  # Diwali-Balipratipada
    datetime(2025, 11, 5).date(),  # Prakash Gurpurb Sri Guru Nanak Dev
    datetime(2025, 12, 25).date(),  # Christmas
]
special_trading_days = [
    datetime(2025, 2, 1).date(),  # Budget Day
]