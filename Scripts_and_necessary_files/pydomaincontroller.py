import os
import re
import ldap3
from dotenv import load_dotenv
from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE
from ldap3.utils.dn import escape_rdn
from ldap3.utils.conv import escape_filter_chars

load_dotenv()

ldap_server = os.getenv("LDAP_SERVER")
ldap_user = os.getenv("LDAP_USER")
ldap_password = os.getenv("LDAP_PASSWORD")
ldap_base_dn = os.getenv("LDAP_BASE_DN")

# def _connection_decorator(func):
#     def wrapper(self, *args, **kwargs):
#         self.conn = Connection(self.server, user=ldap_user, password=ldap_password, client_strategy=ldap3.SYNC)
#         self.conn.bind()
#         returned_value = func(self, *args, **kwargs)
#         self.conn.unbind()
#         return returned_value
#
#     return wrapper

class PyDomainController:
    """Class that directly connects and talks to a domain."""
    def __init__(self):
        self.server = Server(ldap_server, get_info=ldap3.ALL)
        self.conn = Connection(self.server, user=ldap_user, password=ldap_password, client_strategy=ldap3.SYNC)
        self.conn.bind()

    def search_for(self, searched_name:str, object_class:str, attr:list=ldap3.ALL_ATTRIBUTES, additional_base_ou:str="", entries=True):
        """Function for searching for a user inside a domain. It formats the query so it can't be used to bypass it in any way."""
        formatted_name = escape_filter_chars(escape_rdn(searched_name))
        additional_base_ou = additional_base_ou + "," if additional_base_ou else ""
        self.conn.search(additional_base_ou+ldap_base_dn, search_filter=f"(&(name=*{formatted_name}*)(objectClass={object_class}))",
        attributes=attr)
        if entries:
            return self.conn.entries
        else:
            return self.conn.response

    def modify_user(self, searched_name:str, new_name:str= "", new_surname:str= "", new_mail:str= "", new_cn:str= "", new_ou:str= ""):
        """Function that modifies given user inside a domain. Can be used for changing 'givenName', 'sn', 'UserPrincipalName',
        'cn' or 'organizationalUnit' where the user is located."""
        result = self.search_for(searched_name, "User", ["distinguishedName"], entries=False)
        if len(result) < 4:
            return "Couldn't find searched user"
        elif len(result) > 4:
            return "Found more than one user"

        user_dn = result[0]["dn"]
        changes_dict = {}
        if new_name:
            changes_dict["givenName"] = [(MODIFY_REPLACE, [new_name])]
        if new_surname:
            changes_dict["sn"] = [(MODIFY_REPLACE, [new_surname])]
        if new_mail:
            changes_dict["userPrincipalName"] = [(MODIFY_REPLACE,[new_mail])]
        if changes_dict:
            try:
                self.conn.modify(user_dn, changes_dict)
            except Exception as e:
                error = f"An error occurred while changing name, surname or email\n{str(type(e).__name__)}: {str(e)}"
                return error, True
        if new_cn and new_ou:
            result = self.search_for(new_ou, "organizationalUnit", entries=False)
            if len(result) < 4:
                return "Couldn't find searched OU"
            elif len(result) > 4:
                return "Found more than one OU"

            new_ou_dn = result[0]["dn"]
            try:
                self.conn.modify_dn(user_dn, f"cn={new_cn}", new_superior=new_ou_dn)
            except Exception as e:
                error = f"An error occurred while changing username or OU\n{str(type(e).__name__)}: {str(e)}"
                return error, True
        elif new_cn:
            try:
                self.conn.modify_dn(user_dn, f"cn={new_cn}")
            except Exception as e:
                error = f"An error occurred while changing username\n{str(type(e).__name__)}: {str(e)}"
                return error, True
        elif new_ou:
            result = self.search_for(new_ou, "organizationalUnit", entries=False)
            if len(result) < 4:
                return "Couldn't find searched OU"
            elif len(result) > 5:
                return "Found more than one OU"

            new_ou_dn = result[0]["dn"]
            try:
                self.conn.modify_dn(user_dn, f"cn={searched_name}", new_superior=new_ou_dn)
            except Exception as e:
                error = f"An error occurred while changing OU \n{str(type(e).__name__)}: {str(e)}"
                return error, True
        return "All changes have been applied"

    def change_group(self, searched_name:str, groups_str:str="", delete:bool=False):
        """Function used for adding or removing user from groups."""
        result = self.search_for(searched_name, "User", ["distinguishedName"], entries=False)
        if len(result) < 4:
            return "Couldn't find searched user"
        elif len(result) > 4:
            return "Found more than one user"

        user_dn = result[0]["dn"]
        groups = re.split(", |,\n|,|\n" ,groups_str)
        if not delete:
            for group in groups:
                if group != "":
                    result = self.search_for(group, "Group", ["distinguishedName"], entries=False)
                    if len(result) < 4:
                        return f"Couldn't find searched group: '{group}'"
                    elif len(result) > 4:
                        return f"Found more than one group: '{group}'"
                    group_dn = result[0]["dn"]
                    try:
                        self.conn.modify(group_dn, {"member": [(MODIFY_ADD, user_dn)]})
                        if self.conn.result["result"] == 68:
                            return f"User is already in this group:  '{result[0]["dn"]}'"
                    except Exception as e:
                        error = f"An error occurred while adding user to this group: '{group}'\n{str(type(e).__name__)}: {str(e)}"
                        return error, True
                else:
                    return "Insert the correct name of the group"
            return "Adding to all the groups have been successful"
        else:
            for group in groups:
                if group != "":
                    result = self.search_for(group, "Group", ["distinguishedName"], entries=False)
                    if len(result) < 4:
                        return f"Couldn't find searched group: '{group}'"
                    elif len(result) > 4:
                        return f"Found more than one group: '{group}'"
                    group_dn = result[0]["dn"]
                    try:
                        self.conn.modify(group_dn, {"member": [(MODIFY_DELETE, user_dn)]})
                        if self.conn.result["result"] == 53:
                            return f"User has already been removed from this group: '{result[0]["dn"]}'"
                    except Exception as e:
                        error = f"An error occurred while removing user from this group: '{group}'\n{str(type(e).__name__)}: {str(e)}"
                        return error, True
                else:
                    return "Insert the correct name of the group"
            return "Removing from all the groups have been successful"

    def create_new_ou(self, new_ou:str, directory:str="morski"):
        """Function used for creating new OUs inside the domain."""
        result = self.search_for(directory, "organizationalUnit",
                                 ["distinguishedName"], "ou=morski", False)
        if len(result) < 1:
            return "Couldn't find searched OU"
        elif len(result) > 1:
            return "Found more than one OU"

        dest_dn = result[0]["dn"]
        try:
            self.conn.add(f"ou={new_ou},{dest_dn}", object_class="organizationalUnit")
            if self.conn.result["result"] == 68:
                return "Given OU already exists in this directory"
            return "Creating new OU has been successful"
        except Exception as e:
            error = f"En error occurred while creating new OU \n{str(type(e).__name__)}: {str(e)}"
            return error, True

    def __del__(self):
        self.conn.unbind()