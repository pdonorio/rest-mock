# -*- coding: utf-8 -*-

# i want this piece of code to be the ABSTRACT base of other subclasses
import abc
from ... import get_logger

logger = get_logger(__name__)

"""
# === Singleton - Design Pattern ===

Examples of Singleton Patterns
    - taken from "Learning Python Design Patterns" by Gennadiy Zlobin
"""

# # === Singleton Python 2 implementation ===
# class Singleton(object):
#     """
#     This is the class that implements *the Singleton pattern* in classic way
#     """
#     def __new__(cls):
#         if not hasattr(cls, 'instance'):
#             cls.instance = super(Singleton, cls).__new__(cls)
#         return cls.instance


class Borg(object):
    """
    This is the class that implements the
    ***borg*** Singleton pattern for subClassing!
    """
    _shared_state = {}

    def __new__(cls, *args, **kwargs):
        obj = super(Borg, cls).__new__(cls, *args, **kwargs)
        obj.__dict__ = cls._shared_state
        return obj

"""
# === Database connection with singleton ===

Working on a Connection (abstract?) object to implement
with different database (SQL and NoSQL)
"""


class Connection(Borg):
    __metaclass__ = abc.ABCMeta

    """
    == My Abstract Connection ==
    With your DBMS implement a "make_connection" method.
    But then use only **get_connection** to avoid duplicates.
    """
    _connection = None      # main property

    def __init__(self, use_database=True, connect=True):
        """ This is were i want to make sure i connect """
        super(Connection, self).__init__()
        if connect:
            self.get_connection(use_database)

    @classmethod
    def __subclasshook__(cls, C):
        """
        I am telling python that:
        The class who implements a 'make_connection' is a Connection subclass
        """
        if cls is Connection:
            if any("make_connection" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented

    @abc.abstractmethod
    def make_connection(self, use_database):
        """
        You have to implement this method to specify how your database
        can connect to an ORM or driver.
        """
        pass

    def get_connection(self, use_database):
        """ Singleton: having only one _connection in your app """

        ##########################################################
        # **Warning**: to check if connection exists may change
        # From one db to another
        if self._connection is not None:
            # A connection exists
            if self._connection.check_open and self._connection.check_open():
                logger.debug("Already connected")
                return self._connection

        logger.debug("Trying connection")
        self._connection = self.make_connection(use_database)
        return self._connection

# === How to verify one object ===
# print Connection().get_connection() #2times
