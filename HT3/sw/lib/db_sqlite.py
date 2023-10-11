#! /usr/bin/python3
#
#################################################################
## Copyright (c) 2013 Norbert S. <junky-zs@gmx.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#################################################################
# Ver:0.1.5  / Datum 25.05.2014
# Ver:0.1.7.1/ Datum 04.03.2015 logging from ht_utils added
# Ver:0.1.8  / Datum 21.09.2015 is_sql_db_enabled() now with flag-input
# Ver:0.1.10 / Datum 25.08.2016 minor formatting changes
# Ver:0.2    / Datum 29.08.2016 Fkt.doc added.
# Ver:0.3    / 2023-06-07       tempfile handling added in __init__()
#################################################################
#

import sqlite3
import time
import os
import tempfile
import xml.etree.ElementTree as ET
import ht_utils
import logging


dbNotConnectedError = ValueError('Attempting to use "db_sqlite" that is not connected')


class cdb_sqlite(ht_utils.clog):
    """
    Class 'cdb_sqlite' for creating, reading and writing data from/to sqlite-database
    """
    def __init__(self, configurationfilename, logger=None):
        """
            constructor of class 'cdb_sqlite'
             mandatory: parameter 'configurationfilename' (Path and name)
        """
        try:
            # init/setup logging-file
            if logger == None:
                ht_utils.clog.__init__(self)
                logfilenamepath = os.path.join(tempfile.gettempdir(),"cdb_sqlite.log")
                self._logging = ht_utils.clog.create_logfile(self, logfilenamepath, loggertag="cdb_sqlite")
            else:
                self._logging = logger

            if not isinstance(configurationfilename, str):
                errorstr = "cdb_sqlite;Error;Parameter: configurationfilename"
                self._logging.critical(errorstr)
                raise TypeError(errorstr)

            self.__cfgfilename = configurationfilename
            #get database-name from configuration
            tree = ET.parse(configurationfilename)
            self.__root = tree.getroot()
            self.__dbname = self.__root.find('dbname_sqlite').text
            if not len(self.__dbname):
                errorstr = "cdb_sqlite;Error;'dbname_sqlite' not found in configuration"
                self._logging.critical(errorstr)
                raise NameError(errorstr)

            self.__path = os.path.dirname(self.__dbname)
            self.__basename = os.path.basename(self.__dbname)
            if not os.path.isabs(self.__dbname):
                abspath = os.path.abspath(".")
                self.__fullpathname = os.path.join(abspath, os.path.abspath(self.__dbname))
            else:
                self.__fullpathname = self.__dbname

            self.__sql_enable = False
            self.__connection = None
            self.__cursor = None

            for sql_part in self.__root.findall('sql-db'):
                self.__sql_enable = sql_part.find('enable').text.upper()
                if self.__sql_enable == 'ON' or self.__sql_enable == '1':
                    self.__sql_enable = True
                else:
                    self.__sql_enable = False

        except (OSError, EnvironmentError, TypeError, NameError) as e:
            errorstr = """cdb_sqlite();Error;<{0}>""".format(str(e.args))
            self._logging.critical(errorstr)
            print(errorstr)
            raise e

        except (sqlite3.OperationalError) as e:
            errorstr = """cdb_sqlite.__init__();Error;<{0}>;database<{1}>""".format(e.args[0], self.__dbname)
            self._logging.critical(errorstr)
            print(errorstr)
            raise e

    def __del__(self):
        """
            desctructor of class.
        """
        if not self.__connection == None:
            self.close()

    def addcolumn(self, tablename, columnname, columntype):
        """
            add named column of columntype for table using sql-commands
             mandatory: tablename, columnname, columntype
        """
        if self.__sql_enable == True:
            if self.__connection == None:
                self._logging.critical("cdb_sqlite.addcolumn();Error;database not connected")
                raise dbNotConnectedError
            else:
                # check first is column available, if not create the column
                try:
                    #do nothing if column is already available
                    str_select = "SELECT * FROM " + tablename + " WHERE " + columnname + " NOT NULL;"
                    self.__cursor.execute(str_select)
                except:
                    str_alter = "ALTER TABLE " + tablename + " ADD COLUMN " + columnname + " " + columntype + ";"
                    try:
                        self.__cursor.execute(str_alter)
                    except (sqlite3.OperationalError) as e:
                        errorstr = """cdb_sqlite.addcolumn();Error;<{0}>;Table<{1}>;Column<{2}>""".format(
                                e.args[0],
                                tablename,
                                columnname)
                        self._logging.critical(errorstr)
                        print(errorstr)

    def close(self):
        """
            close cursor and connection to sql-database
             mandatory: none
        """
        if self.__sql_enable == True:
            try:
                if not self.__connection == None:
                    self.__cursor.close()
                    self.__connection.close()
                    self.__cursor = None
                    self.__connection = None
            except:
                errorstr = "cdb_sqlite.close();Error;couldn't close sql-database"
                self._logging.critical(errorstr)
                print(errorstr)

    def connect(self):
        """
            connect and get cursor of sql-database
             mandatory: none
        """
        if self.__sql_enable == True:
            try:
                if self.__connection == None:
                    self.__connection = sqlite3.connect(self.__dbname)
                    self.__cursor = self.__connection.cursor()
            except:
                errorstr = "cdb_sqlite.connect();Error;couldn't connect to sql-database"
                self._logging.critical(errorstr)
                print(errorstr)

    def commit(self):
        """
            send commit to database using sql-commands
             mandatory: to be connected to database
        """
        if self.__sql_enable == True:
            if self.__connection == None:
                self._logging.critical("cdb_sqlite.commit();Error;database not connected")
                raise dbNotConnectedError
            else:
                try:
                    if not self.__connection == None:
                        self.__connection.commit()
                except (sqlite3.OperationalError) as e:
                    errorstr = 'cdb_sqlite.commit();Error;<{0}>'.format(e.args[0])
                    self._logging.critical(errorstr)
                    print(errorstr)

    def createindex(self, tablename, indexname, columnname):
        """
            creating index on named column for table using sql-commands
             mandatory: tablename, indexname, columnname
                        to be connected to database
        """
        if self.__sql_enable == True:
            if self.__connection == None:
                self._logging.critical("cdb_sqlite.createindex();Error;database not connected")
                raise dbNotConnectedError
            else:
                strcmd = "CREATE INDEX IF NOT EXISTS " + indexname + " ON " + tablename + "(" + columnname + ");"
                try:
                    self.__cursor.execute(strcmd)
                except (sqlite3.OperationalError) as e:
                    errorstr = 'cdb_sqlite.createindex();Error;<{0}>;Table<{1}>'.format(e.args[0], tablename)
                    self._logging.critical(errorstr)
                    print(errorstr)

    def createtable(self, tablename):
        """
            creating table if not exists using sql-commands
             mandatory: tablename
                        to be connected to database
        """
        if self.__sql_enable == True:
            if self.__connection == None:
                self._logging.critical("cdb_sqlite.createtable();Error;database not connected")
                raise dbNotConnectedError
            else:
                strcmd = "CREATE TABLE IF NOT EXISTS " + tablename + " (Local_date_time CURRENT_TIMESTAMP, UTC INT);"
                try:
                    self.__cursor.execute(strcmd)
                except (sqlite3.OperationalError) as e:
                    errorstr = 'cdb_sqlite.createtable();Error;<{0}>;Table<{1}>'.format(e.args[0], tablename)
                    self._logging.critical(errorstr)
                    print(errorstr)

    def delete(self, tablename, columnname, contentvalue, exp='='):
        """
            delete columns where contentvalue and expression is found in table
             mandatory: tablename, columnname, contentvalue
                        to be connected to database
             optional : expression (default is '=')
        """
        if self.__sql_enable == True:
            if self.__connection == None:
                self._logging.critical("cdb_sqlite.delete();Error;database not connected")
                raise dbNotConnectedError
            else:
                try:
                    strcmd = "DELETE FROM " + tablename + " WHERE " + columnname + exp + contentvalue
                    self.__cursor.execute(strcmd)
                except (sqlite3.OperationalError) as e:
                    errorstr = 'cdb_sqlite.delete();Error;<{0}>'.format(e.args[0])
                    self._logging.critical(errorstr)
                    print(errorstr)

    def insert(self, tablename, values, timestamp=None):
        """
            insert values in table using sql-commands
             mandatory: tablename, values [bunch of values]
                        to be connected to database
            optional : timestamp (default is current Localtime and UTC are used)
        """
        if self.__sql_enable == True:
            if self.__connection == None:
                self._logging.critical("cdb_sqlite.insert();Error;database not connected")
                raise dbNotConnectedError
            else:
                if timestamp == None:
                    itimestamp = int(time.time())
                else:
                    itimestamp = int(timestamp)
                localtime = time.localtime(itimestamp)
                # first column:='Local_date_time' default set to Local-time
                __strdatetime="""{:4d}.{:02d}.{:02d} {:02d}:{:02d}:{:02d}""".format(localtime.tm_year, \
                                                                                    localtime.tm_mon, \
                                                                                    localtime.tm_mday, \
                                                                                    localtime.tm_hour, \
                                                                                    localtime.tm_min, \
                                                                                    localtime.tm_sec)

                strcmd = """INSERT INTO '{0}' VALUES('{1}','{2}',{3});""".format(
                    tablename,
                    __strdatetime,
                    itimestamp,
                    ",".join("""'{0}'""".format(str(val).replace('"', '""')) for val in values))
                try:
                    self.__cursor.execute(strcmd)
                except (sqlite3.OperationalError) as e:
                    errorstr = 'cdb_sqlite.insert();Error;<{0}>'.format(e.args[0])
                    self._logging.critical(errorstr)
                    print(errorstr)

    def is_sql_db_enabled(self, enabled_flag=None):
        """
            returns True/False on status sqlite-db enabled / disabled
             mandatory: None
             optional : enabled_flag (setable flag := True / False)
        """
        if enabled_flag != None:
            self.__sql_enable = bool(enabled_flag)
        return self.__sql_enable

    def selectwhere(self, tablename, columnname, searchvalue, exp='=', what='*'):
        """
            returns values from table with named column, expression, searchvalue and what
             mandatory: tablename, columnname, searchvalue
                        to be connected to database
            optional : expression (default is '=')
                        what       (default is '*')
        """
        if self.__sql_enable == True:
            if self.__connection == None:
                self._logging.critical("cdb_sqlite.selectwhere();Error;database not connected")
                raise dbNotConnectedError
            else:
                # function returns the a list of values or empty list on none match
                try:
                    strcmd = "SELECT " + what + " FROM " + tablename + " WHERE " + columnname + " " + exp + " " + searchvalue + ";"
                    return list(self.__cursor.execute(strcmd))
                except (sqlite3.OperationalError) as e:
                    errorstr = 'cdb_sqlite.selectwhere();Error;<{0}>'.format(e.args[0])
                    self._logging.critical(errorstr)
                    print(errorstr)
        else:
            return list()

    def setpragma(self, pragmaname, pragmavalue):
        """
            Set pragma for the database using sql-commands
             mandatory: pragmaname, pragmavalue
                        to be connected to database
        """
        if self.__sql_enable == True:
            if self.__connection == None:
                self._logging.critical("cdb_sqlite.setpragma();Error;database not connected")
                raise dbNotConnectedError
            else:
                try:
                    strcmd="PRAGMA " + pragmaname + " " + pragmavalue
                    self.__cursor.execute(strcmd)
                except (sqlite3.OperationalError) as e:
                    errorstr = 'cdb_sqlite.setpragma();Error;<{0}>'.format(e.args[0])
                    self._logging.critical(errorstr)
                    print(errorstr)

    def gettableinfo(self, tablename):
        """
            returns the current tableinfo using sql-commands
             mandatory: tablename
                        to be connected to database
        """
        if self.__sql_enable == True:
            if self.__connection == None:
                self._logging.critical("cdb_sqlite.gettableinfo();Error;database not connected")
                raise dbNotConnectedError
            else:
                try:
                    strcmd = "PRAGMA table_info ({0})".format(tablename)
                    return self.__cursor.execute(strcmd)
                except (sqlite3.OperationalError) as e:
                    errorstr = 'cdb_sqlite.gettableinfo();Error;<{0}>'.format(e.args[0])
                    self._logging.critical(errorstr)
                    print(errorstr)
        else:
            return list()

    def vacuum(self):
        """
            execute command 'vaccum' on database using sql-commands
             mandatory: to be connected to database
        """
        if self.__sql_enable == True:
            if self.__connection == None:
                self._logging.critical("cdb_sqlite.vacuum();Error;database not connected")
                raise dbNotConnectedError
            else:
                try:
                    self.__cursor.execute("VACUUM")
                except (sqlite3.OperationalError) as e:
                    errorstr = 'cdb_sqlite.vacuum();Error;<{0}>'.format(e.args[0])
                    self._logging.critical(errorstr)
                    print(errorstr)

    #---------------------
    def createdb_sqlite(self):
        """
            creating database 'sqlite'
             The db-structur is taken from xml-configurefile
             mandatory: to be connected to database
        """
        if self.__sql_enable == True:
            if self.__connection == None:
                self._logging.critical("cdb_sqlite.createdb_sqlite();Error;database not connected")
                raise dbNotConnectedError
            else:
                try:
                    #first of all (before table-creation) set pragma auto_vacuum
                    self.setpragma("auto_vacuum", "= full")

                    for syspart in self.__root.findall('systempart'):
                        syspartname = syspart.attrib["name"]
                        # create table
                        self.createtable(syspartname)
                        # set index for first column 'data_time'
                        self.createindex(syspartname, "idate_time", "Local_date_time")

                        for logitem in syspart.findall('logitem'):
                            name = logitem.attrib["name"]
                            datatype = logitem.find('datatype').text
                            datause = logitem.find('datause').text
                            maxvalue = logitem.find('maxvalue').text
                            default = logitem.find('default').text
                            unit = logitem.find('unit').text
                    #        print(name,datatype,datause,maxvalue,default,unit)
                            self.addcolumn(syspartname, name, datatype.upper())
                    self.commit()
                except (sqlite3.OperationalError, EnvironmentError) as e:
                    errorstr = 'create_db.sqlite();Error;<{0}>'.format(e.args[0])
                    self._logging.critical(errorstr)
                    print(errorstr)
                    raise e

    def configurationfilename(self):
        """
            returns the used xml-config filename.
             mandatory: none
        """
        return self.__cfgfilename

    def db_sqlite_filename(self, pathname=None):
        """
            returns and setup of used sqlite-db  filename.
             mandatory: none
        """
        # function sets / returns the db-name
        if not pathname == None:
            self.__dbname = pathname
        return self.__dbname

    def is_sqlite_db_available(self, dbname=None):
        """
            returns True/False on status sqlite-db available/not available
             mandatory: none
        """
        dbfilename = dbname if not dbname == None else self.__dbname
        if os.access(dbfilename, os.W_OK and os.R_OK):
            return True
        else:
            return False

#--- class cdb_sqlite end ---#

### Runs only for test ###########
if __name__ == "__main__":
    configurationfilename = './../etc/config/4test/create_db_test.xml'
    HT3_db = cdb_sqlite(configurationfilename)
    dbfilename = HT3_db.db_sqlite_filename()
    print("------------------------")
    print("Config: get sql-database configuration at first")
    print("configfile            :'{0}'".format(configurationfilename))
    print("sql db-file           :'{0}'".format(dbfilename))
    print("sql db_enabled        :{0}".format(HT3_db.is_sql_db_enabled()))
    HT3_db.connect()
    print("Create database:{}".format(dbfilename))
    HT3_db.createdb_sqlite()
    if HT3_db.is_sqlite_db_available(dbfilename):
        print("database available")
    else:
        print("database not available")

    print("Create table 'testtable'")
    HT3_db.createtable("testtable")

    print("Add column to table")
    HT3_db.addcolumn("testtable", "Messwert1_int", "INT")
    HT3_db.addcolumn("testtable", "Messwert_real", "REAL")
    HT3_db.addcolumn("testtable", "Counter_int", "INT")
    HT3_db.addcolumn("testtable", "hexdump", "TEXT")

    HT3_db.createindex("testtable", "idate_time", "Local_date_time")
    HT3_db.commit()
    counter = 0
    print("Insert values to table")
    values = [44, 35.1, 2345, "hexdump1"]
    HT3_db.insert("testtable", values)
    while counter < 10:
        values = [(43+counter*2), 32.1, (2340+counter), "counting"]
        HT3_db.insert("testtable", values)
        time.sleep(1)
        print(counter + 1)
        counter += 1
    HT3_db.commit()

    values = [34, 45.6, 3456, "liste eintragen"]
    HT3_db.insert("testtable", values)
    HT3_db.commit()
    print("-------------------------------------------")
    print("view   'Counter_int'-raws equal 2347")
    selectvalues = HT3_db.selectwhere("testtable", "Counter_int", "2347")
    for zeile in selectvalues:
        print(zeile)

    print("-------------------------------------------")
    print("delete 'Counter_int'-raws if equal 2347")
    HT3_db.delete("testtable", "Counter_int", "2347")
    HT3_db.commit()
    print(" view must be empty")
    selectvalues = HT3_db.selectwhere("testtable", "Counter_int", "2347")
    for zeile in selectvalues:
        print(zeile)

    print("-------------------------------------------")
    print("view   'Counter_int'-raws less then 2347")
    selectvalues = HT3_db.selectwhere("testtable", "Counter_int", "2347", "<")
    for zeile in selectvalues:
        print(zeile)

    print("-------------------------------------------")
    print("delete 'Counter_int'-raws if less then 2347")
    HT3_db.delete("testtable", "Counter_int", "2347", "<")
    HT3_db.commit()
    print(" view must be empty")
    selectvalues = HT3_db.selectwhere("testtable", "Counter_int", "2347", "<")
    for zeile in selectvalues:
        print(zeile)

    print("-------------------------------------------")
    print(" select 'Messwert1_int'-raws greather then '50'")
    print("  and view attached Local_date_time")
    selectvalues = HT3_db.selectwhere("testtable", "Messwert1_int", "50", ">", "Local_date_time")
    for zeile in selectvalues:
        print(zeile)

    print("-------------------------------------------")
    print(" table_info from 'solar'")
    infos = HT3_db.gettableinfo("solar")
    for info in infos:
        print(info)

    HT3_db.vacuum()
    HT3_db.close()
